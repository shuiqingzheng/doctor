from django.db import models
from order.models import QuestionOrder, MedicineOrder
from ckeditor.fields import RichTextField


class Recipe(models.Model):
    order = models.ForeignKey(
        MedicineOrder,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='recipe',
        verbose_name='药品订单',
        help_text='药品订单'
    )
    total_price = models.DecimalField(max_digits=6, decimal_places=2, verbose_name='总价格', help_text='总价格')
    recipe_result = RichTextField(verbose_name='诊断结论', help_text='诊断结论')
    PRICE_TYPE_CHOICES = (
        ('医师号', '医师号'),
        ('其他号', '其他号')
    )
    price_type = models.CharField(choices=PRICE_TYPE_CHOICES, max_length=50, blank=True, null=True, verbose_name='挂号类型', help_text='挂号类型')

    def __str__(self):
        return '{}'.format(self.pk)

    class Meta:
        db_table = 'recipe'
        verbose_name = '处方'
        verbose_name_plural = verbose_name
        ordering = ['-pk', ]


class DiaMedicine(models.Model):
    owner = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='diamedicine')
    medicine_name = models.CharField(max_length=200, blank=True, verbose_name='药品名称', help_text='药品名称')
    medicine_num = models.IntegerField(blank=True, default=0, verbose_name='药品单件数量', help_text='药品单件数量')
    medicine_price = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, verbose_name='药品单价', help_text='药品单价')

    def __str__(self):
        return '{}'.format(self.pk)

    class Meta:
        db_table = 'diamedicine'
        verbose_name = '处方中药品列表'
        verbose_name_plural = verbose_name
        ordering = ['-pk', ]


class History(models.Model):
    """
    患者病历
    """
    patient_id = models.IntegerField(blank=True, verbose_name='患者ID', help_text='患者ID')

    doctor_id = models.IntegerField(blank=True, verbose_name='医生ID', help_text='医生ID')

    history_create_time = models.DateTimeField(blank=True, verbose_name='就诊时间', help_text='就诊时间')

    # 病历内容(富文本)
    history_content = RichTextField(verbose_name='病历内容', help_text='病历内容')

    recipe = models.OneToOneField(Recipe, null=True, blank=True, on_delete=models.CASCADE, related_name='history', verbose_name='处方')

    def __str__(self):
        return '{}'.format(self.pk)

    class Meta:
        db_table = 'history'
        verbose_name = '病历'
        verbose_name_plural = verbose_name
        ordering = ['-pk', ]


class Detail(models.Model):
    """
    诊断详情
    """
    # def custom_func_upload_to(instance, filename):
    #     return 'upload/review/{}'.format(filename)

    patient_id = models.IntegerField(blank=True, verbose_name='患者ID', help_text='患者ID')
    doctor_id = models.IntegerField(blank=True, verbose_name='医生ID', help_text='医生ID')
    patient_main = models.TextField(verbose_name='患者主诉', help_text='患者主诉')
    image_one = models.URLField(blank=True, null=True, verbose_name='上传图片url-1', help_text='上传图片url-1')
    image_two = models.URLField(blank=True, null=True, verbose_name='上传图片url-2', help_text='上传图片url-2')
    image_three = models.URLField(blank=True, null=True, verbose_name='上传图片url-3', help_text='上传图片url-3')
    # image_one = models.ImageField(upload_to=custom_func_upload_to, blank=True, null=True, verbose_name='上传图片1', help_text='上传图片1')

    # image_two = models.ImageField(upload_to=custom_func_upload_to, blank=True, null=True, verbose_name='上传图片2', help_text='上传图片2')

    # image_three = models.ImageField(upload_to=custom_func_upload_to, blank=True, null=True, verbose_name='上传图片3', help_text='上传图片3')

    order_time = models.DateTimeField(null=True, verbose_name='预约时间', help_text='预约时间')

    create_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True


class DiaDetail(Detail):
    """
    复诊详情
    """
    order_question = models.OneToOneField(QuestionOrder, on_delete=models.CASCADE, related_name='diadetail', blank=True, null=True, verbose_name='咨询订单')

    order_medicine = models.OneToOneField(MedicineOrder, on_delete=models.CASCADE, related_name='diadetail', blank=True, null=True, verbose_name='药品订单')

    recipe = models.OneToOneField(Recipe, null=True, blank=True, on_delete=models.CASCADE, related_name='diadetail')

    is_video = models.BooleanField(default=False, verbose_name='是否视频复诊', help_text='是否视频复诊')

    video_info = models.CharField(max_length=200, blank=True, null=True, verbose_name='复诊视频回放', help_text='复诊视频回放')

    voice_info = models.URLField(blank=True, null=True, verbose_name='患者录音', help_text='患者录音')

    room_number = models.IntegerField(blank=True, null=True, verbose_name='视频房间号', help_text='视频房间号')

    def __str__(self):
        return '{}'.format(self.pk)

    class Meta:
        db_table = 'diadetail'
        verbose_name = '复诊详情'
        verbose_name_plural = verbose_name
        ordering = ['-pk', ]


class ImageDetail(Detail):
    """
    图文详情
    """
    order_question = models.OneToOneField(QuestionOrder, on_delete=models.CASCADE, related_name='imagedetail', blank=True, null=True, verbose_name='咨询订单')

    order_medicine = models.OneToOneField(MedicineOrder, on_delete=models.CASCADE, related_name='imagedetail', blank=True, null=True, verbose_name='药品订单')

    response_answer = RichTextField(verbose_name='医生回复', help_text='医生回复')

    def __str__(self):
        return '{}'.format(self.pk)

    class Meta:
        db_table = 'imagedetail'
        verbose_name = '图文详情'
        verbose_name_plural = verbose_name
        ordering = ['-pk', ]


class VideoDetail(Detail):
    """
    视频详情
    """
    order_question = models.OneToOneField(QuestionOrder, on_delete=models.CASCADE, related_name='videodetail', blank=True, null=True, verbose_name='咨询订单')

    order_medicine = models.OneToOneField(MedicineOrder, on_delete=models.CASCADE, related_name='videodetail', blank=True, null=True, verbose_name='药品订单')

    video_info = models.CharField(max_length=100, blank=True, null=True, verbose_name='复诊视频回放', help_text='复诊视频回放')

    def __str__(self):
        return '{}'.format(self.pk)

    class Meta:
        db_table = 'videodetail'
        verbose_name = '视频详情'
        verbose_name_plural = verbose_name
        ordering = ['-pk', ]
