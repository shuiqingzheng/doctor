from django.db import models
from ckeditor.fields import RichTextField


class MedicineType(models.Model):

    LEVEL_CHOICES = (
        ('1', '1'),
        ('2', '2'),
        ('3', '3')
    )
    medicine_number = models.CharField(choices=LEVEL_CHOICES, max_length=2, blank=True, verbose_name='药品分类级别', help_text='药品分类级别')

    type_name = models.CharField(max_length=200, unique=True, blank=True, verbose_name='药品类别名称', help_text='药品类别名称')

    father_id = models.IntegerField(null=True, blank=True, verbose_name='父类ID/名称', help_text='父类ID/名称')

    def __str__(self):
        return self.type_name

    class Meta:
        db_table = 'medicinetype'
        verbose_name = '药品类别'
        verbose_name_plural = verbose_name
        ordering = ['-pk', ]


class Medicine(models.Model):
    """
    药品：
    正式名称-商品名-规格-价格-生产厂家-生产日期-适应证-说明书（富文本）-药品图片-药品状态
    """
    type_one = models.CharField(max_length=200, blank=True, null=True, verbose_name='一级类别', help_text='一级类别')

    type_two = models.CharField(max_length=200, blank=True, null=True, verbose_name='二级分类', help_text='二级分类')

    type_three = models.CharField(max_length=200, blank=True, null=True, verbose_name='三级分类', help_text='三级分类')

    officical_name = models.CharField(max_length=200, verbose_name='正式名称', help_text='正式名称')

    product_name = models.CharField(max_length=200, verbose_name='商品名', help_text='商品名')

    standard = models.CharField(max_length=200, verbose_name='规格', help_text='规格')

    price = models.DecimalField(max_digits=8, decimal_places=3, verbose_name='价格', help_text='价格')

    product_source = models.CharField(max_length=200, verbose_name='生产厂家', help_text='生产厂家')

    good_for = models.CharField(max_length=200, verbose_name='适应症', help_text='适应症')

    detail = RichTextField(verbose_name='说明书')

    product_images = models.CharField(max_length=200, blank=True, null=True, verbose_name='药品图片', help_text='药品图片')

    # 上传图片限制问题
    # upload_images = models.CharField()

    product_state = models.BooleanField(blank=True, default=False, verbose_name='药品是否上架', help_text='药品是否上架')

    def __str__(self):
        return self.officical_name

    class Meta:
        db_table = 'medicine'
        verbose_name = '药品'
        verbose_name_plural = verbose_name
        ordering = ['-pk', ]


class MedicineImages(models.Model):
    """
    药品相关图片
    """
    owner = models.ForeignKey(Medicine, on_delete=models.CASCADE, related_name='medicine_images')

    def custom_func_upload_to(instance, filename):
        return 'upload/medicine/{}'.format(filename)

    image = models.ImageField(upload_to=custom_func_upload_to, verbose_name='药品图片', help_text='药品图片')

    is_first = models.BooleanField(default=False, blank=True, verbose_name='是否作为封面', help_text='是否作为封面')

    def __str__(self):
        return '{}'.format(self.pk)

    class Meta:
        db_table = 'medicineimages'
        verbose_name = '药品图片'
        verbose_name_plural = verbose_name
        ordering = ['-pk']


class MedicineStock(models.Model):
    medicine_name = models.CharField(max_length=200, verbose_name='药品名称', help_text='药品名称')
    medicine_description = models.TextField(verbose_name='药品说明', help_text='药品说明')
    create_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.medicine_name

    class Meta:
        db_table = 'medicinestock'
        verbose_name = '药品库存上报记录'
        verbose_name_plural = verbose_name
        ordering = ['-create_time']
