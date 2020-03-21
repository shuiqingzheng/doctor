import redis
from django.conf import settings
from django.db import transaction
from django.contrib.auth.backends import ModelBackend
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


class UpdateModelSameCode(object):
    """
    : 数据更新时,涉及adminuser的修改; 
    根据数据进行切分, 然后保存到对应表中
    """

    def atomic_func(self, data, user, user_model, user_serializer, admin_user_serializer):
        """
        data: 需要切分的数据
        user: 未更改前的对像
        user_model: 当前对象的类型(models.Model)
        user_serializer: 对应的序列化器
        admin_user_serializer: 固定的序列化(amdinuser的序列化器)
        """
        user_data = dict()
        admin_data = dict()
        # 拆分数据
        for key, value in data.items():
            if not value:
                continue

            if hasattr(user_model, key):
                user_data[key] = value

            if hasattr(AdminUser, key):
                admin_data[key] = value

        with transaction.atomic():
            point = transaction.savepoint()

            try:
                u_serializer = user_serializer(user, data=user_data, partial='partial')
                u_serializer.is_valid(raise_exception=True)
                u_serializer.save()
                admin_serializer = admin_user_serializer(user.owner, data=admin_data, partial='partial')
                admin_serializer.is_valid(raise_exception=True)
                admin_serializer.save()
            except Exception as e:
                transaction.savepoint_rollback(point)
                raise e
            transaction.savepoint_commit(point)
