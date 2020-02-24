from django.contrib import admin
from myuser.models import PatientUser, DoctorUser, DoctorSetTime


@admin.register(PatientUser)
class PatientUserAdmin(admin.ModelAdmin):
    list_display = ('id', 'owner')


@admin.register(DoctorUser)
class DoctorUserAdmin(admin.ModelAdmin):
    list_display = ('id', 'owner')


@admin.register(DoctorSetTime)
class DoctorSetTimeAdmin(admin.ModelAdmin):
    list_display = ('id', 'owner')
