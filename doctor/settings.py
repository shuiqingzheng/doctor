"""
Django settings for admin project.

Generated by 'django-admin startproject' using Django 2.1.7.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.1/ref/settings/
"""

import os
# import sentry_sdk
# from sentry_sdk.integrations.django import DjangoIntegration

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '3b)#h%=v9r)gcvw)y^jokuh#d9rp&0@pea@$4cp+eo5tn(7u_o'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

CORS_ORIGIN_ALLOW_ALL = True
# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'drf_yasg',
    'oauth2_provider',
    'rest_framework',
    'django_filters',
    'ckeditor',
    'ckeditor_uploader',

    'article',
    'aduser',
    'myuser',
    'medicine',
    'order',
    'diagnosis',
    'importfile',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    # 'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'doctor.middleware.MyMiddleware'
]

ROOT_URLCONF = 'doctor.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'doctor.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'admin',
        'HOST': '127.0.0.1',
        'PORT': 3306,
        'PASSWORD': 'shuiqing',
        'USER': 'root'
    }
}

# Password validation
# https://docs.djangoproject.com/en/2.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

AUTHENTICATION_BACKENDS = [
    'myuser.utils.UsernameMobileAuthBackend',
]

# Internationalization
# https://docs.djangoproject.com/en/2.1/topics/i18n/

LANGUAGE_CODE = 'zh-Hans'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/

STATIC_URL = '/static/'

AUTH_USER_MODEL = 'aduser.AdminUser'

STATIC_ROOT = os.path.join(BASE_DIR, 'collect_static')

STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]

MEDIA_ROOT = os.path.join(BASE_DIR, 'media/')

MEDIA_URL = '/media/'

CKEDITOR_UPLOAD_PATH = "uploads/"

OAUTH2_PROVIDER = {
    'AUTHORIZATION_CODE_EXPIRE_SECONDS': 60 * 5,
    'ACCESS_TOKEN_EXPIRE_SECONDS': 60 * 60 * 8,
    'SCOPES': {
        'doctor': '医生权限',
        'patient': '患者权限',
        'extreme': '高级权限',
    }
}

OAUTH2_PROVIDER_APPLICATION_MODEL = 'oauth2_provider.Application'
OAUTH2_PROVIDER_ACCESS_TOKEN_MODEL = 'oauth2_provider.AccessToken'
OAUTH2_PROVIDER_REFRESH_TOKEN_MODEL = 'oauth2_provider.RefreshToken'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'oauth2_provider.contrib.rest_framework.OAuth2Authentication',
    ),
    'DEFAULT_PAGINATION_CLASS': 'doctor.pagination.CustomPagination',
    'PAGE_SIZE': 10,
    'NON_FIELD_ERRORS_KEY': 'detail',
}

SWAGGER_SETTINGS = {
    'USE_SESSION_AUTH': False,
    'SECURITY_DEFINITIONS': {
        '汉典云健康系统API': {
            'type': 'oauth2',
            'authorizationUrl': '/o/authorize/',
            'tokenUrl': '/o/token/',
            'flow': 'password',
            'scopes': {
                'doctor': '医生权限',
                'patient': '患者权限',
                'extreme': '高级权限',
            }
        }
    },
    'OAUTH2_CONFIG': {
        'clientId': 'huazai',
        'clientSecret': 'huazai',
        'appName': 'Handian'
    },
}

CODE_EXPIRED = 10 * 60

# settings.py
CELERY_TASK_SERIALIZER = 'pickle'
CELERY_RESULT_SERIALIZER = 'pickle'
CELERY_ACCEPT_CONTENT = ['pickle']

CELERY_BROKER_URL = 'redis://127.0.0.1:6378/0'
CELERY_RESULT_BACKEND = 'redis://127.0.0.1:6378/1'

REDIS_HOST = '127.0.0.1'
REDIS_PORT = 6378
REDIS_DB = 2
# 验证码过期时间
REDIS_KEY_TTL = 5 * 60

# NGINX相关信息
NGINX_SERVER = 'http://127.0.0.1'
NGINX_PORT = 8889

DATETIME_FORMAT = '%H:%M:%S'
DATETIME_TOTAL_FORMAT = '%Y-%m-%d %H:%M:%S'
DATETIME_INPUT_FORMATS = ['%Y-%m-%d %H:%M:%S', ]

# sentry_sdk.init(
#     dsn="http://1360c6d6c5424614a199e0ea29cd0ead@39.99.225.130:9000/2",
#     integrations=[DjangoIntegration()],

#     # If you wish to associate users to errors (assuming you are using
#     # django.contrib.auth) you may enable sending PII data.
#     send_default_pii=True
# )

# 微信相关参数
APPID = 'wx355b0ef93ef23f9a'
MCHID = '1328839501'
APPSECRET = 'fab3b340e0d2964c2ba70908496c021e'
# key设置路径：微信商户平台(pay.weixin.qq.com)-->账户设置-->API安全-->密钥设置
KEY = '243278132033cc5c47e869c8c34d015e'
OPENID_URL = "https://api.weixin.qq.com/sns/jscode2session"
# NOTIFY_URL = 'http://127.0.0.1:9000/order/callback/'
NOTIFY_URL = 'https://hdmp.hdzyhosp.com/order/callback/'

# NGINX_ROOT_PATH = ':'.join([NGINX_SERVER, str(NGINX_PORT)])
# NOTIFY_URL = '/'.join([NGINX_ROOT_PATH, 'order/callback/'])
# print(NOTIFY_URL)
# print(NOTIFY_URL)
