from rest_framework.permissions import BasePermission, SAFE_METHODS


class DiffUserPermission(BasePermission):
    """
    @判断对应的用户是什么身份
    @病人不可修改和创建
    @医生只可以修改自己创建的文章(article_state为'管理员撤回'状态时,文章也不可修改)
    """

    def has_permission(self, request, view):
        token = request.auth
        req_method = request.method

        if not token:
            return False

        if hasattr(token, 'user'):
            user = token.user
            if hasattr(user, 'patient') and req_method in ('PUT', 'POST'):
                return False

        return True

    def has_object_permission(self, request, view, obj):
        user = request.auth.user
        req_method = request.method

        if hasattr(user, 'doctor'):
            doctor = user.doctor
            if hasattr(obj, 'article_doctor'):
                article_doctor = obj.article_doctor
                if req_method == 'PUT' and article_doctor != doctor:
                    return False

        if '管理员' in obj.article_state and req_method not in SAFE_METHODS:
            return False

        return True
