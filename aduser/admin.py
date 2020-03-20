from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from aduser.models import AdminUser


class UserCreationForm(forms.ModelForm):
    """A form for creating new users. Includes all the required
    fields, plus a repeated password."""
    password1 = forms.CharField(label=u'密码', widget=forms.PasswordInput)
    password2 = forms.CharField(label=u'再次输入密码', widget=forms.PasswordInput)

    class Meta:
        model = AdminUser
        fields = ('email', 'username', 'phone', 'password')

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(u"密码输入不一致！")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super(UserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    password hash display field.
    """
    password = ReadOnlyPasswordHashField(label=("密码"),
                                         help_text=(
        '忘记密码 --> <a href={} '
        'style="padding: 5px;font-size: 14px;color:white;background: #84adc6;"'
        '>修改密码</a>'.format('../password/')
    ),)

    class Meta:
        model = AdminUser
        fields = ('email', 'username', 'phone', 'password', 'is_active', 'is_staff')

    def clean_password(self):
        return self.initial["password"]


class MyUserAdmin(UserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm

    list_display = ('pk', 'email', 'username', 'phone',
                    'sex', 'is_staff')
    list_filter = ('is_staff', 'groups',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('个人信息', {'fields': ('username', 'phone', 'sex',)}),
        ('权限', {'fields': ('is_staff', 'groups', 'user_permissions',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'phone', 'password1', 'password2')}
         ),
    )
    perm_fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('个人信息', {'fields': ('username', 'phone', 'sex',)}),
    )
    search_fields = ('email', 'username', 'phone', 'id')
    ordering = ('pk', 'phone',)
    filter_horizontal = ('groups', 'user_permissions',)

    def get_fieldsets(self, request, obj=None):
        if not request.user.is_superuser:
            return self.perm_fieldsets

        return super().get_fieldsets(request, obj)


admin.site.register(AdminUser, MyUserAdmin)
admin.site.site_header = '汉典云健康系统'
admin.site.site_title = '汉典云健康系统'
