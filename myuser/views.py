from rest_framework import viewsets, generics, status
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

    def index(self, request, *args, **kwargs):
        response_context = dict()
        # 复诊排名前三
        results = DiaDetail.objects.values('doctor_id').annotate(dia=Count('doctor_id')).order_by('-dia')
        # <QuerySet [{'dia': 3, 'doctor_id': 2}, {'dia': 1, 'doctor_id': 3}]>
        try:
            doctor_objs = [DoctorUser.objects.get(id=result.get('doctor_id')) for num, result in enumerate(results) if num < 3]
        except DoctorUser.DoesNotExist:
            pass

        print(doctor_objs)
        # 复诊对低价
        b = DoctorUser.objects.filter(bool_referral=True).aggregate(Min('referral'))
        print(b)
        response_context['min_price'] = b
        # 自己曾咨询过的复诊（未登录的话就不显示）
        return Response(response_context)

    def find(self, request, *args, **kwargs):
        response_context = dict()
        return Response(response_context)


class DoctorView(BaseRegisterView, viewsets.ModelViewSet):
    """
    医生:
    create()->手机号注册;
    """
    permission_classes = [AllowAny, ]
    # requsired_scopes = ['basic']
    queryset = DoctorUser.objects.all()
    serializer_class = DoctorSerializer
    model = DoctorUser
