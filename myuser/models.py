from django.db import models
from django.contrib.auth.hashers import check_password
from aduser.models import AdminUser


class UploadFile(models.Model):
    def custom_func_upload_to(instance, filename):
        if len(filename) >= 100:
            filename = filename[:-50:-1][::-1]
        return 'upload/file/{}'.format(filename)

    file_path = models.FileField(upload_to=custom_func_upload_to, verbose_name='文件', help_text='文件')

    def __str__(self):
        return '{}'.format(self.pk)

    class Meta:
        db_table = 'uploadfile'
        verbose_name = '上传文件'
        verbose_name_plural = verbose_name
        ordering = ['-pk', ]


class UploadImage(models.Model):
    def custom_func_upload_to(instance, filename):
        if len(filename) >= 100:
            filename = filename[:-50:-1][::-1]
        return 'upload/images/{}'.format(filename)

    image = models.ImageField(upload_to=custom_func_upload_to, verbose_name='图片', help_text='图片')

    def __str__(self):
        return '{}'.format(self.pk)

    class Meta:
        db_table = 'uploadimage'
        verbose_name = '上传图片'
        verbose_name_plural = verbose_name
        ordering = ('-pk', )


class BaseUser(models.Model):
    def custom_func_upload_to(instance, filename):
        return 'upload/user_picture/{0}/{1}'.format(instance.id, filename)

    user_picture = models.URLField(max_length=200, null=True, blank=True, verbose_name='用户头像', help_text='用户头像')

    nick_name = models.CharField(max_length=20, blank=True, verbose_name='微信昵称', help_text='微信昵称')

    id_card = models.CharField(max_length=18, blank=True, null=True, unique=True, verbose_name='身份证号', help_text='身份证号')

    USER_SEX_CHOICES = (
        ('男', '男'),
        ('女', '女'),
        ('未知', '未知')
    )

    birthday = models.DateField(blank=True, null=True, verbose_name='出生年月', help_text='出生年月')

    room_id = models.CharField(max_length=12, blank=True, null=True, verbose_name='视频/语音房间号', help_text='视频/语音房间号')

    def check_password(self, pwd):
        return check_password(pwd, self.password)

    class Meta:
        abstract = True


class PatientUser(BaseUser):
    """
    患者:
    姓名-威信昵称-身份证号-出生年月-图文咨询次数-视频咨询次数-复诊次数
    """
    owner = models.OneToOneField(AdminUser, on_delete=models.CASCADE, related_name='patient', verbose_name='用户')

    position = models.CharField(max_length=50, blank=True, null=True, verbose_name='职业', help_text='职业')

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
    owner = models.OneToOneField(AdminUser, on_delete=models.CASCADE, related_name='doctor', verbose_name='用户')

    hospital = models.CharField(max_length=120, blank=True, null=True, verbose_name='医院', help_text='医院')

    score = models.IntegerField(blank=True, default=0, verbose_name='患者好评', help_text='患者好评')

    server_times = models.IntegerField(default=0, verbose_name='服务患者次数', help_text='服务患者次数')

    good_at = models.TextField(blank=True, null=True, verbose_name='擅长诊疗方向', help_text='擅长诊疗方向')

    good_point = models.CharField(max_length=200, blank=True, null=True, verbose_name='执业点', help_text='执业点')

    DEPARTMENT_CHOICES = (
        ('未知', '未知'),
        ('中医', '中医'),
        ('全科', '全科')
    )
    department = models.CharField(choices=DEPARTMENT_CHOICES, default='未知', max_length=100, blank=True, verbose_name='科室', help_text='科室')

    summary = models.CharField(max_length=255, blank=True, null=True, verbose_name='一句话概括', help_text='一句话概括')

    image_question = models.DecimalField(default=0.0, max_digits=5, decimal_places=2, blank=True, null=True, verbose_name='图文咨询', help_text='图文咨询')

    bool_image_question = models.BooleanField(default=False, blank=True, verbose_name='是否开启图文咨询', help_text='是否开启图文咨询')

    video_question = models.DecimalField(default=0.0, max_digits=5, decimal_places=2, blank=True, null=True, verbose_name='视频咨询', help_text='视频咨询')

    bool_video_question = models.BooleanField(default=False, blank=True, verbose_name='是否开启视频咨询', help_text='是否开启视频咨询')

    referral = models.DecimalField(default=0.0, max_digits=5, decimal_places=2, blank=True, null=True, verbose_name='复诊收费', help_text='复诊收费')

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
    owner = models.ForeignKey(DoctorUser, on_delete=models.CASCADE, related_name='settime', verbose_name='医生ID')

    start_time = models.DateTimeField(verbose_name='起始时间', help_text='起始时间')

    end_time = models.DateTimeField(verbose_name='结束时间', help_text='结束时间')

    WEEK_DAY_CHOICES = (
        ('1', '周一'),
        ('2', '周二'),
        ('3', '周三'),
        ('4', '周四'),
        ('5', '周五'),
        ('6', '周六'),
        ('7', '周日'),
    )
    week_day = models.CharField(max_length=4, choices=WEEK_DAY_CHOICES, default='1', blank=True, verbose_name='周几', help_text='周几')

    def __str__(self):
        return '{}'.format(self.pk)

    class Meta:
        db_table = 'doctorsettime'
        verbose_name = '医生预约时间'
        verbose_name_plural = verbose_name
        ordering = ['-pk', ]
