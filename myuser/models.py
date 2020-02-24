from django.db import models
from django.contrib.auth.hashers import check_password
from aduser.models import AdminUser


class BaseUser(models.Model):
    def custom_func_upload_to(instance, filename):
        return 'upload/user_picture/{0}/{1}'.format(instance.id, filename)

    user_picture = models.ImageField(upload_to=custom_func_upload_to, null=True, blank=True, verbose_name='用户头像', help_text='用户头像')

    # email = models.EmailField(blank=True, unique=True, null=True, verbose_name='邮箱', help_text='邮箱')

    nick_name = models.CharField(max_length=20, blank=True, verbose_name='微信昵称', help_text='微信昵称')

    id_card = models.CharField(max_length=18, blank=True, null=True, unique=True, verbose_name='身份证号', help_text='身份证号')

    # username = models.CharField(null=True, blank=True, max_length=125, verbose_name='姓名', help_text='姓名')

    # phone = models.CharField(max_length=11, blank=True, unique=True, verbose_name='手机号', help_text='手机号')

    # password = models.CharField(max_length=128,)

    USER_SEX_CHOICES = (
        ('男', '男'),
        ('女', '女'),
        ('未知', '未知')
    )
    # sex = models.CharField(choices=USER_SEX_CHOICES, max_length=2, blank=True, null=True, verbose_name='性别', help_text='性别')

    # age = models.IntegerField(blank=True, null=True, verbose_name='年龄', help_text='年龄')

    birthday = models.DateField(blank=True, null=True, verbose_name='出生年月', help_text='出生年月')

    room_id = models.CharField(max_length=12, blank=True, null=True, verbose_name='视频/语音房间号', help_text='视频/语音房间号')

    # is_active = models.BooleanField(default=True, verbose_name='账号是否激活', help_text='账号是否激活')

    def check_password(self, pwd):
        return check_password(pwd, self.password)

    class Meta:
        abstract = True


class PatientUser(BaseUser):
    """
    患者:
    姓名-威信昵称-身份证号-出生年月-图文咨询次数-视频咨询次数-复诊次数
    """
    owner = models.OneToOneField(AdminUser, on_delete=models.CASCADE, related_name='patient')

    image_count = models.IntegerField(blank=True, default=0, verbose_name='图文咨询次数', help_text='图文咨询次数')

    video_count = models.IntegerField(blank=True, default=0, verbose_name='视频咨询次数', help_text='视频咨询次数')

    referral_count = models.IntegerField(blank=True, default=0, verbose_name='复诊次数', help_text='复诊次数')

    is_patient = models.BooleanField(blank=True, default=False, verbose_name='是否符合复诊患者', help_text='是否符合复诊患者')

    patient_state = models.CharField(max_length=20, blank=True, null=True, verbose_name='病人复诊状态', help_text='病人复诊状态')

    is_patientuser = models.BooleanField(default=True, verbose_name='患者', help_text='患者')

    def __str__(self):
        return '%s' % self.pk

    class Meta:
        db_table = 'patientuser'
        verbose_name = '患者'
        verbose_name_plural = verbose_name
        ordering = ('-pk', )


class DoctorUser(BaseUser):
    """
    医生:
    姓名-手机-医院-好评次数-擅长诊疗方向-执业点-一句话概括-图文咨询（是否开启）-视频咨询（是否开启）-复诊收费（是否开启）
    -科室
    """
    owner = models.OneToOneField(AdminUser, on_delete=models.CASCADE, related_name='doctor')

    hospital = models.CharField(max_length=120, blank=True, null=True, verbose_name='医院', help_text='医院')

    score = models.IntegerField(blank=True, default=0, verbose_name='患者好评', help_text='患者好评')

    good_at = models.TextField(blank=True, null=True, verbose_name='擅长诊疗方向', help_text='擅长诊疗方向')

    good_point = models.CharField(max_length=200, blank=True, null=True, verbose_name='执业点', help_text='执业点')

    DEPARTMENT_CHOICES = (
        ('未知', '未知'),
        ('中医', '中医'),
        ('全科', '全科')
    )
    department = models.CharField(choices=DEPARTMENT_CHOICES, default='未知', max_length=100, blank=True, verbose_name='科室', help_text='科室')

    summary = models.CharField(max_length=255, blank=True, null=True, verbose_name='一句话概括', help_text='一句话概括')

    image_question = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, verbose_name='图文咨询', help_text='图文咨询')

    bool_image_question = models.BooleanField(default=False, blank=True, verbose_name='是否开启图文咨询', help_text='是否开启图文咨询')

    video_question = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, verbose_name='视频咨询', help_text='视频咨询')

    bool_video_question = models.BooleanField(default=False, blank=True, verbose_name='是否开启视频咨询', help_text='是否开启视频咨询')

    referral = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, verbose_name='复诊收费', help_text='复诊收费')

    bool_referral = models.BooleanField(default=False, blank=True, verbose_name='是否开启复诊收费', help_text='是否开启复诊收费')

    is_success = models.BooleanField(default=False, blank=True, verbose_name='注册请求是否通过', help_text='注册请求是否通过')

    reason = models.CharField(max_length=200, blank=True, null=True, verbose_name='注册驳回理由', help_text='注册驳回理由')

    is_doctor = models.BooleanField(default=True, verbose_name='医生', help_text='医生')

    def __str__(self):
        return '%s' % self.pk

    class Meta:
        db_table = 'doctoruser'
        verbose_name = '医生'
        verbose_name_plural = verbose_name
        ordering = ('-pk', )


class DoctorSetTime(models.Model):
    owner = models.ForeignKey(DoctorUser, on_delete=models.CASCADE, related_name='settime')

    start_time = models.DateTimeField(verbose_name='起始时间', help_text='起始时间')

    end_time = models.DateTimeField(verbose_name='结束时间', help_text='结束时间')

    def __str__(self):
        return '{}'.format(self.pk)

    class Meta:
        db_table = 'doctorsettime'
        verbose_name = '医生预约时间'
        verbose_name_plural = verbose_name
        ordering = ['-pk', ]