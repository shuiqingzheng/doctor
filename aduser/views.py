from rest_framework import viewsets
from rest_framework.response import Response
from aduser.models import AdminUser
from aduser.serializers import AdminUserSerializer, UpdatePasswordSerializer
from medicine.permissions import TokenHasPermission
from oauth2_provider.contrib.rest_framework import TokenHasScope


class AdminUserView(viewsets.ModelViewSet):
    permission_classes = [TokenHasPermission, ]
    queryset = AdminUser.objects.all()
    serializer_class = AdminUserSerializer
    model = AdminUser

    def get_serializer_class(self):
        if self.action == 'update':
            return UpdatePasswordSerializer
        return self.serializer_class

    def update(self, request, *args, **kwargs):
        data = request.data
        s = self.get_serializer(data=data)
        s.is_valid(raise_exception=True)
        return Response({'detail': '密码修改成功'})


class DoctorPasswordView(AdminUserView):
    permission_classes = [TokenHasScope, ]
    required_scopes = ['doctor']


class PatientPasswordView(AdminUserView):
    permission_classes = [TokenHasScope, ]
    required_scopes = ['patient']
