from rest_framework import serializers
from myuser.models import PatientUser, DoctorUser
from aduser.models import AdminUser
from django.contrib.auth.hashers import make_password, check_password
from utils.random_number import create_random_number
from .utils import redis_conn

from celery_tasks.tasks import register_task


class SmsSerializer(serializers.Serializer):
    phone = serializers.CharField(min_length=11, max_length=11, label='手机号')

    def validate(self, attrs):
        phone = attrs.get('phone')
        try:
            patient = AdminUser.objects.get(phone=phone)
        except AdminUser.DoesNotExist:
            # 注册
            # 1. 发送验证码
            # 1.1 生成随机码
            # 1.2 异步发送
            sms_code = create_random_number()
            key_name = '_'.join([phone, 'sms'])
            redis_conn.setex(key_name, 5 * 60, sms_code)
            result = register_task.delay(phone, sms_code)

            import json
            a = json.loads(result.get())
            if a.get('Code') != 'OK':
                raise serializers.ValidationError('验证码发送失败，请重新尝试...')
        else:
            raise serializers.ValidationError('用户已存在，请登录')
        return attrs

class BaseRegisterSerializer(serializers.Serializer):
    phone = serializers.CharField(min_length=11, max_length=11, label='手机号')
    password = serializers.CharField(min_length=6, max_length=18, label='密码')
    subpassword = serializers.CharField(min_length=6, max_length=18, label='验证密码')
    validate_code = serializers.CharField(min_length=6, max_length=6, error_messages={'blank': '验证码不可为空'}, label='短信验证码')

    def validate(self, attrs):
        phone = attrs.get('phone')
        password = attrs.get('password')
        subpassword = attrs.get('subpassword')
        validate_code = attrs.get('validate_code')
        key_name = '_'.join([phone, 'sms'])
        value = redis_conn.get(key_name)

        try:
            patient = AdminUser.objects.get(phone=phone)
        except AdminUser.DoesNotExist:
            pass
        else:
            raise serializers.ValidationError('用户已存在，请登录')

        if not value:
            raise serializers.ValidationError('短信验证码失效， 请重新发送...')
        if not str(validate_code) == str(value):
            raise serializers.ValidationError('短信验证码错误， 请重新输入...')

        if not str(password) == str(subpassword):
            raise serializers.ValidationError('两次输入的密码不相同， 请重新输入...')

        try:
            attrs.pop('subpassword')
            attrs.pop('validate_code')
        except Exception:
            pass

        return attrs


class AdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdminUser
        fields = '__all__'


class PatientSerializer(serializers.ModelSerializer):

    class Meta:
        model = PatientUser
        fields = '__all__'
        read_only_fields = ['owner']


class PatientBaseInfoSerializer(serializers.ModelSerializer):
    username = serializers.StringRelatedField(label='患者真实姓名', read_only=True, source='owner.username')

    sex = serializers.StringRelatedField(label='患者性别', read_only=True, source='owner.sex')

    phone = serializers.StringRelatedField(label='患者手机号', read_only=True, source='owner.phone')

    class Meta:
        model = PatientUser
        fields = ('id', 'username', 'phone', 'id_card', 'position', 'sex', 'birthday')


class PatientVisitSerializer(serializers.ModelSerializer):
    username = serializers.StringRelatedField(label='医生姓名', read_only=True, source='owner.username')

    class Meta:
        model = PatientUser
        fields = ('id', 'username', 'patient_main', '')
        read_only_fields = ['owner']


class AdminUserRegisterSerializer(BaseRegisterSerializer):
    def create(self, validated_data):
        # 账户密码加密
        password = validated_data.get('password')
        validated_data['password'] = make_password(password)
        return AdminUser.objects.create(**validated_data)


class DoctorSerializer(serializers.ModelSerializer):
    # user_picture_url = serializers.SerializerMethodField()
    username = serializers.StringRelatedField(label='医生姓名', read_only=True, source='owner.username')

    class Meta:
        model = DoctorUser
        fields = ('id', 'nick_name', 'user_picture', 'referral', 'username')

    # def get_user_picture_url(self, obj):
    #     if not obj.user_picture:
    #         return None

    #     request = self.context.get('request')
    #     photo_url = obj.user_picture
    #     print(type(photo_url), photo_url)
    #     return photo_url
