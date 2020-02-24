import redis
import re
from django.conf import settings
from django.contrib.auth.backends import ModelBackend
from myuser.models import PatientUser, DoctorUser
from aduser.models import AdminUser

redis_conn = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_DB, decode_responses=True)


def get_user_by_account(account):
    """
    根据帐号获取user对象
    account: 账号，可以是用户名，也可以是手机号
    return: User对象 或者 None
    """
    try:
        user = AdminUser.objects.get(phone=account)
    except AdminUser.DoesNotExist:
        return None
    else:
        return user


class UsernameMobileAuthBackend(ModelBackend):
    '''o/token => phone'''

    def authenticate(self, request, username=None, password=None, **kwargs):
        user = get_user_by_account(username)
        if user is not None and user.check_password(password):
            return user
