from django.db import models

from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
# from oauth2_provider.backends import OAuth2Backend

class AdUserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, phone, password, username=None, **extra_fields):
        if not email:
            raise ValueError('邮箱必填')

        if not phone:
            raise ValueError('手机号必填')

        user = self.model(username=username, email=email, phone=phone, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, phone, password, username=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, phone, username, **extra_fields)

    def create_superuser(self, email, phone, password, username=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, phone, password, username, **extra_fields)


class AdminUser(AbstractBaseUser, PermissionsMixin):
    # 姓名/手机/邮箱/密码
    email = models.EmailField(blank=True, null=True, unique=True, verbose_name='邮箱', help_text='邮箱')
    username = models.CharField(null=True, blank=True, max_length=125, verbose_name='姓名', help_text='姓名')
    phone = models.CharField(max_length=11, unique=True, verbose_name='手机号', help_text='手机号')
    is_active = models.BooleanField(default=True,)

    USER_SEX_CHOICES = (
        ('男', '男'),
        ('女', '女'),
        ('未知', '未知')
    )
    sex = models.CharField(choices=USER_SEX_CHOICES, max_length=2, blank=True, null=True, verbose_name='性别', help_text='性别')

    age = models.IntegerField(blank=True, null=True, verbose_name='年龄', help_text='年龄')

    STATE_CHOICES = (
        ('激活', '激活'),
        ('锁定', '锁定')
    )
    state = models.CharField(choices=STATE_CHOICES, max_length=10, blank=True, null=True, verbose_name='状态', help_text='状态')

    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = ['email', ]

    objects = AdUserManager()

    def get_full_name(self):
        # The user is identified by their email address
        return self.email

    def get_short_name(self):
        # The user is identified by their email address
        return self.email

    is_staff = models.BooleanField(default=False,)
    is_superuser = models.BooleanField(default=False,)

    def __str__(self):  # __unicode__ on Python 2
        return '{}'.format(self.phone)

    class Meta:
        db_table = 'adminuser'
        verbose_name = '用户'
        verbose_name_plural = verbose_name
        ordering = ('-pk',)
