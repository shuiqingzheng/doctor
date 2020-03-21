from rest_framework import serializers
from myuser.models import PatientUser, DoctorUser, DoctorSetTime, UploadImage
from aduser.models import AdminUser
from django.contrib.auth.hashers import make_password
from utils.random_number import create_random_number
from .utils import redis_conn
from celery_tasks.tasks import register_task
from django.conf import settings


class UploadImageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField(read_only=True, label='图片地址')

    class Meta:
        model = UploadImage
        fields = '__all__'
        extra_kwargs = {
            'image': {
                'write_only': True
            }
        }

    def get_image_url(self, obj):
        photo_url = obj.image.url
        address = ':'.join((settings.NGINX_SERVER, str(settings.NGINX_PORT)))
        return ''.join(('://'.join(('https', address)), photo_url))


class SmsSerializer(serializers.Serializer):
    phone = serializers.CharField(min_length=11, max_length=11, label='手机号')

    def validate(self, attrs):
        phone = attrs.get('phone')
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
            user = AdminUser.objects.get(phone=phone)
        except AdminUser.DoesNotExist:
            pass
        else:
            raise serializers.ValidationError('%s用户已存在，请登录' % user.phone)

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


class ForgetPasswordSerializer(BaseRegisterSerializer):

    def validate(self, attrs):
        phone = attrs.get('phone')
        password = attrs.get('password')
        subpassword = attrs.get('subpassword')
        validate_code = attrs.get('validate_code')
        key_name = '_'.join([phone, 'sms'])
        value = redis_conn.get(key_name)

        try:
            AdminUser.objects.get(phone=phone)
        except AdminUser.DoesNotExist:
            raise serializers.ValidationError('%s手机号未注册，请先注册' % phone)

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


class PatientInfoSerializer(serializers.Serializer):
    USER_SEX_CHOICES = (
        ('男', '男'),
        ('女', '女'),
        ('未知', '未知')
    )
    sex = serializers.ChoiceField(choices=USER_SEX_CHOICES, label='性别', required=False)
    age = serializers.IntegerField(label='年龄', required=False)
    username = serializers.CharField(label='真实姓名', required=False)
    id_card = serializers.CharField(label='身份证号码', required=False)
    nick_name = serializers.CharField(label='昵称', required=False)
    birthday = serializers.DateField(label='出生日期', required=False)
    position = serializers.CharField(label='职业', required=False)
    user_picture = serializers.URLField(label='患者头像', required=False)


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


class AdminUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = AdminUser
        fields = '__all__'


class DoctorInfoSerializer(serializers.Serializer):
    username = serializers.CharField(label='真实姓名', required=False)
    hospital = serializers.CharField(label='医院', required=False)
    DEPARTMENT_CHOICES = (
        ('未知', '未知'),
        ('中医', '中医'),
        ('全科', '全科')
    )
    department = serializers.ChoiceField(choices=DEPARTMENT_CHOICES, label='科室', required=False)
    good_point = serializers.CharField(label='职称', required=False)
    good_at = serializers.CharField(label='擅长方向', required=False)
    summary = serializers.CharField(label='主要成果', required=False)
    user_picture = serializers.URLField(label='医生头像', required=False)
    nick_name = serializers.CharField(label='昵称', required=False)
    image_question = serializers.DecimalField(max_digits=5, decimal_places=2, label='图文咨询价格', required=False)
    bool_image_question = serializers.BooleanField(label='是否开启图文咨询', required=False)
    video_question = serializers.DecimalField(max_digits=5, decimal_places=2, label='视频咨询价格', required=False)
    bool_video_question = serializers.BooleanField(label='是否开启视频咨询', required=False)
    referral = serializers.DecimalField(max_digits=5, decimal_places=2, label='复诊价格', required=False)
    bool_referral = serializers.BooleanField(label='是否开启复诊咨询', required=False)


class DoctorUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = DoctorUser
        fields = '__all__'
        read_only_fields = ['owner']


class DoctorRetrieveSerializer(serializers.ModelSerializer):
    username = serializers.StringRelatedField(label='医生姓名', read_only=True, source='owner.username')
    email = serializers.StringRelatedField(label='医生邮箱', read_only=True, source='owner.email')
    phone = serializers.StringRelatedField(label='医生电话', read_only=True, source='owner.phone')
    sex = serializers.StringRelatedField(label='医生性别', read_only=True, source='owner.sex')
    age = serializers.StringRelatedField(label='医生年龄', read_only=True, source='owner.age')

    class Meta:
        model = DoctorUser
        fields = ('id', 'user_picture', 'username', 'email', 'phone', 'sex', 'age',
                  'hospital', 'score', 'good_at', 'good_point', 'department', 'summary',
                  'image_question', 'bool_image_question', 'video_question',
                  'bool_video_question', 'referral', 'bool_referral',
                  'is_success', 'reason')


class PatientRetrieveSerializer(serializers.ModelSerializer):
    username = serializers.StringRelatedField(label='患者姓名', read_only=True, source='owner.username')
    email = serializers.StringRelatedField(label='患者邮箱', read_only=True, source='owner.email')
    phone = serializers.StringRelatedField(label='患者电话', read_only=True, source='owner.phone')
    sex = serializers.StringRelatedField(label='患者性别', read_only=True, source='owner.sex')
    age = serializers.StringRelatedField(label='患者年龄', read_only=True, source='owner.age')

    class Meta:
        model = PatientUser
        fields = ('id', 'username', 'email', 'phone', 'sex', 'age', 'position',
                  'image_count', 'video_count', 'referral_count', 'patient_state',
                  'nick_name', 'id_card', 'birthday')


class DoctorSerializer(serializers.ModelSerializer):
    """
    : 患者查看医生的对应信息字段
    """
    # user_picture_url = serializers.SerializerMethodField()
    username = serializers.StringRelatedField(label='医生姓名', read_only=True, source='owner.username')

    class Meta:
        model = DoctorUser
        fields = ('id', 'nick_name', 'user_picture', 'referral', 'username', 'hospital', 'good_at')


class DoctorSetTimeSerializer(serializers.ModelSerializer):
    start_time = serializers.DateTimeField(format=settings.DATETIME_FORMAT, label='开始时间')
    end_time = serializers.DateTimeField(format=settings.DATETIME_FORMAT, label='结束时间')
    WEEK_DAY_CHOICES = (
        ('周一', '周一'),
        ('周二', '周二'),
        ('周三', '周三'),
        ('周四', '周四'),
        ('周五', '周五'),
        ('周六', '周六'),
        ('周日', '周日'),
    )
    week_day = serializers.ChoiceField(choices=WEEK_DAY_CHOICES, label='周几')
    # 时间段总长
    total_time = 15 * 60
    # 时间间隔
    plus_time = 10 * 60

    class Meta:
        model = DoctorSetTime
        fields = '__all__'
        read_only_fields = ['owner']

    def validate(self, attrs):
        # 时间验证
        # 1. 时间段不可少于15分钟
        # 2. 时间段间隔不可少于10分钟

        auth = self.context['request'].auth
        week_day = attrs.get('week_day')
        start_time = attrs.get('start_time')
        end_time = attrs.get('end_time')

        # valide_end_time = start_time + datetime.timedelta(minutes=self.total_time)
        # 只需要计算时分秒
        start_total_seconds = (start_time.hour * 60 * 60) + (start_time.minute * 60) + (start_time.second)
        end_total_seconds = (end_time.hour * 60 * 60) + (end_time.minute * 60) + (end_time.second)

        if (end_total_seconds - start_total_seconds) < self.total_time:
            raise serializers.ValidationError('时间段不可少于15分钟')

        # 查询所有的归于自身的开始时间
        if hasattr(auth.user, 'doctor'):
            time_data_list = []
            time_objs_list = DoctorSetTime.objects.filter(owner=auth.user.doctor, week_day=week_day).values('start_time', 'end_time')

            if not time_objs_list:
                return attrs

            for t in time_objs_list:
                et = t.get('end_time')
                st = t.get('start_time')
                et_total_seconds = (et.hour * 60 * 60) + (et.minute * 60) + (et.second)
                st_total_seconds = (st.hour * 60 * 60) + (st.minute * 60) + (st.second)

                time_data = {
                    's': st_total_seconds,
                    'e': et_total_seconds,
                }
                time_data_list.append(time_data)

            cur = {
                's': start_total_seconds,
                'e': end_total_seconds,
                'identity': 'current_time'
            }
            time_data_list.append(cur)

            new_data_list = sorted(time_data_list, key=lambda k: k['s'])
            current_index = new_data_list.index(cur)

            if current_index == 0:
                if (new_data_list[current_index + 1]['s'] - end_total_seconds) < self.plus_time:
                    raise serializers.ValidationError('时间段间隔不可少于10分钟')
            elif current_index == (len(new_data_list) - 1):
                if (start_total_seconds - new_data_list[current_index - 1]['e']) < self.plus_time:
                    raise serializers.ValidationError('时间段间隔不可少于10分钟')
            else:
                sn = start_total_seconds - new_data_list[current_index - 1]['e']
                ne = new_data_list[current_index + 1]['s'] - end_total_seconds
                if sn < self.plus_time or ne < self.plus_time:
                    raise serializers.ValidationError('时间段间隔不可少于10分钟')
        return attrs
