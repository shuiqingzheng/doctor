import os
from celery import Celery

# 调用django环境, 进行初始化
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'doctor.settings')

app = Celery('doctor')

# 引用设置配置
app.config_from_object('doctor.settings', namespace='CELERY')

# 注册celery任务
app.autodiscover_tasks(['celery_tasks.tasks'])
