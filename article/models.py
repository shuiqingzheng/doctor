from django.db import models
# from ckeditor.fields import RichTextField
from myuser.models import DoctorUser


class ArticleType(models.Model):
    """
    文章分类
    """
    article_type = models.CharField(max_length=100, blank=True, verbose_name='文章类别', help_text='文章类别')

    def __str__(self):
        return self.article_type

    class Meta:
        db_table = 'articletype'
        verbose_name = '文章分类'
        verbose_name_plural = verbose_name
        ordering = ['-pk', ]


class SpecialArticle(models.Model):
    """
    专题分类
    """
    name = models.CharField(max_length=100, blank=True, verbose_name='专题名称', help_text='专题名称')

    # images = models.CharField(max_length='')  # 专题图片

    author = models.CharField(max_length=100, blank=True, default='未知', verbose_name='专题编者', help_text='专题编者')

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'specialarticle'
        verbose_name = '专题分类'
        verbose_name_plural = verbose_name
        ordering = ['-pk', ]


class Article(models.Model):
    """
    文章
    """
    # 文章分类
    article_type = models.ForeignKey(ArticleType, null=True, blank=True, on_delete=models.CASCADE, related_name='article')
    # 专题分类
    special = models.ForeignKey(SpecialArticle, null=True, blank=True, on_delete=models.CASCADE, related_name='article')

    title = models.CharField(max_length=200, blank=True, verbose_name='文章标题', help_text='文章标题')

    create_time = models.DateTimeField(auto_now_add=True, verbose_name='文章日期', help_text='文章日期')

    content = models.TextField(verbose_name='文章内容', help_text='文章内容')

    # 发布文章的医生
    article_doctor = models.ForeignKey(DoctorUser, on_delete=models.CASCADE, related_name='article')

    ARTICLE_STATE_CHOICES = (
        ('已发布', '已发布'),
        ('草稿', '草稿'),
        ('已撤回', '已撤回'),
        ('管理员撤回', '管理员撤回')
    )
    article_state = models.CharField(choices=ARTICLE_STATE_CHOICES, max_length=10, blank=True, default='草稿', verbose_name='文章状态', help_text='文章状态')

    article_click = models.IntegerField(default=1, blank=True, verbose_name='文章热度（整数）', help_text='文章热度（整数）')

    def __str__(self):
        return '{}'.format(self.pk)

    class Meta:
        db_table = 'article'
        verbose_name = '文章'
        verbose_name_plural = verbose_name
        ordering = ['-pk', ]
