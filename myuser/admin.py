from django.contrib import admin
from django.shortcuts import reverse
from django.utils.html import format_html
from myuser.models import PatientUser, DoctorUser, DoctorSetTime, UploadImage


class BaseUserAdmin(object):
    def username_link(self, obj):
        url = reverse('admin:aduser_adminuser_change', args=[obj.owner.id])
        return format_html("<a href='{}'>{}</a>", url, obj.owner.username)

    username_link.short_description = '真实姓名'


@admin.register(PatientUser)
class PatientUserAdmin(BaseUserAdmin, admin.ModelAdmin):
    list_display = ('id', 'username_link', 'position', 'image_count', 'video_count', 'referral_count', 'owner',)
    search_fields = ('owner__phone', 'id', 'owner__username')


@admin.register(DoctorUser)
class DoctorUserAdmin(BaseUserAdmin, admin.ModelAdmin):
    list_display = ('id', 'username_link', 'hospital', 'department', 'good_point', 'owner')
    search_fields = ('owner__phone', 'id', 'owner__username')


@admin.register(DoctorSetTime)
class DoctorSetTimeAdmin(admin.ModelAdmin):
    list_display = ('id', 'start_time', 'end_time', 'week_day', 'owner')
    search_fields = ('id', 'start_time', 'end_time', 'owner__owner__phone')


@admin.register(UploadImage)
class UploadImageAdmin(admin.ModelAdmin):
    list_display = ('id',)
