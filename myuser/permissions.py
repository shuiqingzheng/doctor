from rest_framework.permissions import BasePermission
from rest_framework.exceptions import PermissionDenied
from myuser.contants import patient_write_fields, doctor_write_fields
from myuser.models import PatientUser, DoctorUser


class PatientBasePermission(BasePermission):
    """
    - 患者复诊： 预约复诊时， 需要患者的信息完整
    """
    def _validate_auth(self, request, view):
        auth = request.auth
        if not auth:
            return False

        user = auth.user
        info = list()
        error_msg = ''

        try:
            not_adminuser = PatientUser.objects.get(owner=user)
        except PatientUser.DoesNotExist:
            return False

        for key, value in patient_write_fields.items():
            if hasattr(user, key):
                result = getattr(user, key)
                info.append(result)

            if hasattr(not_adminuser, key):
                result = getattr(not_adminuser, key)
                info.append(result)

            if not result:
                error_msg += '{}字段未填写;'.format(value)

        if not all(info):
            raise PermissionDenied(detail=error_msg)
        return True

    def has_permission(self, request, view):
        return self._validate_auth(request, view)

    def has_object_permission(self, request, view, obj):
        return self._validate_auth(request, view)


class DoctorVisitPermission(BasePermission):
    """
    - 医生复诊时所需权限（自身开通复诊功能）
    """
    def has_permission(self, request, view):
        user = request.auth.user
        if view.action == 'user_history' and hasattr(user, 'patient'):
            return True

        try:
            doctor = DoctorUser.objects.get(owner=user)
        except DoctorUser.DoesNotExist:
            raise PermissionDenied(detail='医生登录失败,请查看登录账号是否正确')

        if view.action == 'create':
            is_open = doctor.bool_referral
            if not is_open:
                raise PermissionDenied(detail='医生需要开启复诊功能')

        return True

    def has_object_permission(self, request, view, obj):
        print('+++++++++++')
        return True


class DoctorBasePermission(BasePermission):
    """
    - 医生操作： 需要验证是否经过审核（以及信息是否完整）
    """
    def _validate_auth(self, request, view):
        auth = request.auth
        if not auth:
            return False

        user = auth.user
        info = list()
        error_msg = ''
        if view.action == 'user_history' and hasattr(user, 'patient'):
            return True

        try:
            not_adminuser = DoctorUser.objects.get(owner=user)
        except DoctorUser.DoesNotExist:
            return False

        for key, value in doctor_write_fields.items():
            if hasattr(user, key):
                result = getattr(user, key)
                info.append(result)

            if hasattr(not_adminuser, key):
                result = getattr(not_adminuser, key)
                info.append(result)

            if not result:
                error_msg += '{}字段未填写;'.format(value)

        if not all(info):
            raise PermissionDenied(detail=error_msg)

        if not not_adminuser.is_success:
            raise PermissionDenied(detail='请等待审核通过')

        return True

    def has_permission(self, request, view):
        return self._validate_auth(request, view)

    def has_object_permission(self, request, view, obj):
        return self._validate_auth(request, view)


class DoctorCreatePermission(BasePermission):
    def has_permission(self, request, view):
        auth = request.auth
        if view.action == 'create':
            if hasattr(auth.user, 'patient'):
                raise PermissionDenied(detail='患者不具备创建病历权限')

        return True
