from django.shortcuts import render
from django.http import Http404
from rest_framework import viewsets, generics, status, filters
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import AllowAny
from django.db.models import Count, Min
from django.db import transaction
from aduser.models import AdminUser
from myuser.models import PatientUser, DoctorUser, DoctorSetTime, UploadImage
from myuser.serializers import (
    AdminUserRegisterSerializer, SmsSerializer, ForgetPasswordSerializer,
    PatientSerializer, DoctorSerializer, PatientInfoSerializer,
    AdminUserSerializer, DoctorInfoSerializer, DoctorRetrieveSerializer,
    DoctorUpdateSerializer, DoctorSetTimeSerializer, PatientRetrieveSerializer,
    UploadImageSerializer,
)
from diagnosis.models import DiaDetail
from medicine.permissions import TokenHasPermission
from myuser.utils import redis_conn, UpdateModelSameCode
from myuser.permissions import PatientBasePermission, DoctorBasePermission
from oauth2_provider.contrib.rest_framework import TokenHasScope


def index(request, *args, **kwargs):
    return render(request, 'index.html')


class UploadImageView(viewsets.ModelViewSet):
    permission_classes = [TokenHasPermission, ]
    # required_scopes = ['patient']
    serializer_class = UploadImageSerializer
    queryset = UploadImage.objects.order_by('-pk')
    parser_classes = [MultiPartParser]


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
        elif self.action == 'update':
            return ForgetPasswordSerializer

        return self.serializer_class

    def update(self, request, *args, **kwargs):
        """
        - 用户(患者或医生)根据手机和验证码进行修改密码
        """
        s = self.get_serializer(data=request.data)
        s.is_valid(raise_exception=True)
        data = s.validated_data
        user = AdminUser.objects.get(phone=data.get('phone'))
        user.set_password(data['password'])
        user.save()
        return Response({'detail': '密码修改成功'})

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
                raise e
            transaction.savepoint_commit(point)

        return Response({'detail': '注册成功'}, status=status.HTTP_201_CREATED, )


class PatientView(BaseRegisterView, viewsets.ModelViewSet):
    permission_classes = [AllowAny, ]
    # requsired_scopes = ['basic']
    queryset = PatientUser.objects.all()
    serializer_class = PatientSerializer
    model = PatientUser

    def list(self, request, *args, **kwargs):
        """
        - 医生查询对应的相关病人
        """
        return super().list(request, *args, **kwargs)

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


class PatientInfoView(UpdateModelSameCode, viewsets.ModelViewSet):
    permission_classes = [TokenHasScope, ]
    required_scopes = ['patient']
    queryset = PatientUser.objects.all()
    serializer_class = PatientInfoSerializer
    model = PatientUser

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return PatientRetrieveSerializer
        return self.serializer_class

    def get_object(self):
        user = self.request.auth.user
        try:
            p = PatientUser.objects.get(owner=user)
        except PatientUser.DoesNotExist:
            raise Http404
        return p

    def partial_update(self, request, *args, **kwargs):
        """
        - 患者补充或者修改自身信息
        """
        data = request.data
        patient = self.get_object()
        self.atomic_func(data, patient, PatientUser, PatientSerializer, AdminUserSerializer)
        return Response({'detail': '修改成功'})


class DoctorView(viewsets.ModelViewSet):
    """
    """
    permission_classes = [TokenHasScope, ]
    required_scopes = ['patient']
    queryset = DoctorUser.objects.filter(is_success=True)
    serializer_class = DoctorSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['hospital', 'department', 'owner__username', 'good_at']
    ordering_fields = ['owner__username', 'score', 'server_times']
    model = DoctorUser

    def get_queryset(self):
        current_url = self.request.path
        if self.action == 'retrieve':
            self.permission_classes = [PatientBasePermission, ]

        if 'review' in current_url:
            return self.queryset.filter(bool_referral=True)

        return self.queryset

    def list(self, request, *args, **kwargs):
        """
        - 按要求查询'复诊'医生（医院，科室，姓名，擅长）
        """
        return super().list(request, *args, **kwargs)


class DoctorRegisterView(BaseRegisterView, viewsets.ModelViewSet):
    """
    - 医生注册
    """
    permission_classes = [AllowAny, ]
    queryset = DoctorUser.objects.filter(is_success=True)
    serializer_class = DoctorSerializer
    model = DoctorUser


class DoctorInfoView(UpdateModelSameCode, viewsets.ModelViewSet):
    permission_classes = [TokenHasScope, ]
    required_scopes = ['doctor']
    queryset = DoctorUser.objects.all()
    serializer_class = DoctorInfoSerializer
    model = DoctorUser

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return DoctorRetrieveSerializer
        return self.serializer_class

    def get_object(self):
        user = self.request.auth.user
        try:
            doctor = DoctorUser.objects.get(owner=user)
        except DoctorUser.DoesNotExist:
            raise Http404
        return doctor

    def partial_update(self, request, *args, **kwargs):
        """
        - 医生补充或者修改自身信息
        """
        data = request.data
        doctor = self.get_object()
        self.atomic_func(data, doctor, DoctorUser, DoctorUpdateSerializer, AdminUserSerializer)
        return Response({'detail': '修改成功'})


class BaseSetTimeView(viewsets.ModelViewSet):
    queryset = DoctorSetTime.objects.all()
    serializer_class = DoctorSetTimeSerializer


class DoctorSetTimeView(BaseSetTimeView):
    permission_classes = [TokenHasScope, DoctorBasePermission]
    required_scopes = ['doctor']

    def get_doctor_obj(self, auth):
        if not hasattr(auth, 'user'):
            return

        if not hasattr(auth.user, 'doctor'):
            return

        try:
            doctor = DoctorUser.objects.get(owner=auth.user)
        except DoctorUser.DoesNotExist:
            doctor = None
        return doctor

    def get_queryset(self):
        doctor = self.get_doctor_obj(self.request.auth)
        if doctor and self.action == 'list':
            return self.queryset.filter(owner=doctor)

        return self.queryset

    def create(self, request, *args, **kwargs):
        """
        - 医生创建预约时间
        """
        doctor = self.get_doctor_obj(request.auth)
        if not doctor:
            return Response({'detail': '用户不存在,请检查对应账号'}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(owner=doctor)
        return Response(serializer.data)


class PatientGetTimeView(BaseSetTimeView):
    permission_classes = [TokenHasScope, ]
    required_scopes = ['patient']

    def validate_doctor_info(self, pk):
        try:
            doctor = DoctorUser.objects.get(pk=pk)
        except DoctorUser.DoesNotExist:
            doctor = None
        return doctor

    def list(self, request, doctor_id, *args, **kwargs):
        """
        - 根据医生ID获取对应医生的可预约时间列表
        """
        doctor = self.validate_doctor_info(doctor_id)
        queryset = self.get_queryset().filter(owner=doctor)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
