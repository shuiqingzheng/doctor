from rest_framework import viewsets, generics, status, filters
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.db.models import Count, Min
from django.db import transaction
from myuser.models import PatientUser, DoctorUser
from myuser.serializers import (
    AdminUserRegisterSerializer, SmsSerializer,
    PatientSerializer, DoctorSerializer,
    AdminSerializer,
)
from diagnosis.models import DiaDetail
from aduser.models import AdminUser
from django.contrib.auth.hashers import make_password
from django_filters.rest_framework import DjangoFilterBackend
from .utils import redis_conn
from utils.sms import aliyun_send_sms_common_api
# from oauth2_provider.contrib.rest_framework import TokenHasScope


class SmsView(generics.RetrieveAPIView):
    """
    注册-手机发送验证码
    """
    permission_classes = [AllowAny, ]
    serializer_class = SmsSerializer

    def get(self, request, *args, **kwargs):
        serializers = self.get_serializer(data=kwargs)
        serializers.is_valid(raise_exception=True)
        phone = serializers.data.get('phone')
        key_name = '_'.join([phone, 'sms'])
        code = redis_conn.get(key_name)
        return Response({'code': code})


class BaseRegisterView(object):
    def get_serializer_class(self):
        if self.action == 'create':
            return AdminUserRegisterSerializer

        return self.serializer_class

    def create(self, request, *args, **kwargs):
        """
        - 注册接口
        """
        # 验证数据
        serializer = AdminUserRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # 保存基本信息
        with transaction.atomic(savepoint=True):
            point = transaction.savepoint()
            try:
                user = serializer.save()
                # 创建空的数据记录-不需要判断
                self.model.objects.create(owner=user)
            except Exception as e:
                transaction.savepoint_rollback(point)
                raise
            transaction.savepoint_commit(point)

        return Response({'detail': '注册成功'}, status=status.HTTP_201_CREATED, )


class PatientView(BaseRegisterView, viewsets.ModelViewSet):
    """
    患者:
    create()->手机号注册;
    """
    permission_classes = [AllowAny, ]
    # requsired_scopes = ['basic']
    queryset = PatientUser.objects.all()
    serializer_class = PatientSerializer
    model = PatientUser

    def main(self, request, *args, **kwargs):
        """
        - 复诊主页面
        - 返回：复诊量排名前三[列表]，最低收费的医生[json]，复诊过的专家（分登录前和登陆后）[列表]
        """
        response_context = dict()
        already_doctor = DoctorUser.objects.filter(bool_referral=True)
        # 复诊排名前三
        results = DiaDetail.objects.values('doctor_id').annotate(dia=Count('doctor_id')).order_by('-dia')
        try:
            doctor_objs = [already_doctor.get(id=result.get('doctor_id')) for num, result in enumerate(results) if num < 3]
        except DoctorUser.DoesNotExist:
            response_context['top_user'] = None
        else:
            serializer_top = DoctorSerializer(instance=doctor_objs, many=True, context={"request": request})
            response_context['top_user'] = serializer_top.data
        # 复诊对低价
        b = already_doctor.aggregate(Min('referral'))
        n = already_doctor.filter(referral__exact=b.get('referral__min'))[0]
        serializer_min = DoctorSerializer(instance=n, context={"request": request})
        response_context['min_price_user'] = serializer_min.data
        # 自己曾咨询过的复诊（未登录的话就不显示）
        auth = request.auth
        if auth:
            # 登录状态
            diadetail_objs = DiaDetail.objects.filter(patient_id=auth.user.id).order_by().values('doctor_id').distinct()
            try:
                dia_doctor_objs = [already_doctor.get(id=result.get('doctor_id')) for num, result in enumerate(diadetail_objs)]
            except DoctorUser.DoesNotExist:
                response_context['after_user'] = None
            else:
                serializer_top = DoctorSerializer(instance=dia_doctor_objs, many=True, context={"request": request})
                response_context['after_user'] = serializer_top.data
        else:
            # 未登录状态
            response_context['after_user'] = None
        return Response(response_context)

    def find(self, request, *args, **kwargs):
        response_context = dict()
        return Response(response_context)


class DoctorView(BaseRegisterView, viewsets.ModelViewSet):
    """
    医生:
    create - 手机号注册;
    """
    permission_classes = [AllowAny, ]
    # requsired_scopes = ['basic']
    queryset = DoctorUser.objects.filter(is_success=True)
    serializer_class = DoctorSerializer
    filter_backends = [filters.SearchFilter, ]
    search_fields = ['hospital', 'department', 'owner__username', 'good_at']
    model = DoctorUser

    def list(self, request, *args, **kwargs):
        """
        - 按要求查询医生（医院，科室，姓名，擅长）
        """
        return super().list(request, *args, **kwargs)
