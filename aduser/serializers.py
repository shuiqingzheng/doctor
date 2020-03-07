from rest_framework import serializers
from aduser.models import AdminUser


class AdminUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdminUser
        fields = '__all__'


class UpdatePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(label='原始密码')
    password = serializers.CharField(label='新密码')
    subpassword = serializers.CharField(label='验证密码')

    def validate(self, attrs):
        old_password = attrs.get('old_password')
        password = attrs.get('password')
        subpassword = attrs.get('subpassword')
        token = self.context['request'].auth
        if not token.user.check_password(old_password):
            raise serializers.ValidationError('原始密码错误')

        if password != subpassword:
            raise serializers.ValidationError('两次输入密码不一致')

        token.user.set_password(password)
        token.user.save()
        return attrs
