from django.db import models
from django.utils import timezone


class Order(models.Model):
    """
    订单：
    """
    nonce_str = models.CharField(max_length=200, blank=True, null=True, verbose_name='随机字符串', help_text='随机字符串')
    # 问题： 设计外键合适还是直接保存ID
    patient_id = models.IntegerField(blank=True, verbose_name='患者id', help_text='患者id')

    doctor_id = models.IntegerField(blank=True, verbose_name='医生id', help_text='医生id')

    create_time = models.DateTimeField(default=timezone.now, blank=True, null=True, verbose_name='创建日期', help_text='创建日期')

    order_num = models.CharField(unique=True, max_length=100, verbose_name='订单编号', help_text='订单编号')

    order_price = models.DecimalField(max_digits=8, decimal_places=2, verbose_name='订单价格', help_text='订单价格')

    PAY_CHOICES = (
        ('未支付', '未支付'),
        ('已支付', '已支付'),
        ('已配送', '已配送'),
        ('申请退费', '申请退费'),
        ('已退费', '已退费'),
    )
    pay_state = models.CharField(choices=PAY_CHOICES, max_length=4, verbose_name='支付状态', help_text='支付状态')

    class Meta:
        abstract = True


class QuestionOrder(Order):
    """
    咨询订单
    ：患者姓名-医生姓名-创建时间范围以及订单状态检索和展示
    """
    FORM_CHOICES = (
        ('视频', '视频'),
        ('图文', '图文'),
        ('复诊', '复诊')
    )
    question_order_form = models.CharField(choices=FORM_CHOICES, max_length=4, verbose_name='咨询类型', help_text='咨询类型')

    BUSINESS_CHOICES = (
        ('待支付', '待支付'),
        ('待会诊', '待会诊'),
        ('会诊完成', '会诊完成')
    )
    business_state = models.CharField(choices=BUSINESS_CHOICES, max_length=4, verbose_name='业务状态', help_text='业务状态')

    def __str__(self):
        return '{}'.format(self.pk)

    class Meta:
        db_table = 'questionorder'
        verbose_name = '咨询订单'
        verbose_name_plural = verbose_name
        ordering = ['-pk', ]


class MedicineOrder(Order):
    """
    药品订单
    ：药品名称-患者名称-患者手机号-创建时间-订单状态
    """
    FORM_CHOICES = (
        ('药品', '药品'),
        ('处方', '处方'),
    )
    # 打折后的价格
    discount_price = models.DecimalField(null=True, max_digits=8, decimal_places=2, verbose_name='折后价格', help_text='折后价格')

    medicine_order_form = models.CharField(choices=FORM_CHOICES, max_length=4, verbose_name='类型', help_text='类型')

    def __str__(self):
        return '{}'.format(self.pk)

    class Meta:
        db_table = 'medicineorder'
        verbose_name = '药品订单'
        verbose_name_plural = verbose_name
        ordering = ['-pk', ]
