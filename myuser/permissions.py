from rest_framework.permissions import BasePermission
from rest_framework.exceptions import PermissionDenied
from myuser.contants import patient_write_fields
from myuser.models import PatientUser


class PatientBasePermission(BasePermission):
    """
    - 患者复诊： 预约复诊时， 需要患者的信息完整
    """
    def _validate_auth(self, request, view):
        print('++++++++++')
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
