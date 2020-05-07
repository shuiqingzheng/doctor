from django.contrib import admin
from django.shortcuts import reverse
from django.utils.html import format_html
from order.models import QuestionOrder, MedicineOrder
from myuser.models import DoctorUser, PatientUser


class BaseOrderAdmin(object):

    def patient_info(self, obj):
        patient = PatientUser.objects.get(id=obj.patient_id)
        url = reverse('admin:aduser_adminuser_change', args=[patient.owner.id])
        return format_html('<a href="{}">{}</a>', url, patient.owner.phone)

    def doctor_info(self, obj):
        doctor = DoctorUser.objects.get(id=obj.doctor_id)
        url = reverse('admin:aduser_adminuser_change', args=[doctor.owner.id])
        return format_html('<a href="{}">{}</a>', url, doctor.owner.phone)

    patient_info.short_description = '患者信息'
    doctor_info.short_description = '医生信息'


@admin.register(QuestionOrder)
class QuestionOrderAdmin(BaseOrderAdmin, admin.ModelAdmin):
    list_display = ('pk', 'order_num', 'order_price', 'pay_state', 'business_state', 'question_order_form', 'patient_info', 'doctor_info', 'create_time')
    search_fields = ('pk', 'order_num', 'pay_state', 'business_state', 'question_order_form')
    fieldsets = (
        (None, {'fields': ['patient_id', 'doctor_id', 'order_num',
                           'order_price', 'pay_state', 'question_order_form', 'business_state']}),
    )


@admin.register(MedicineOrder)
class MedicineOrderAdmin(BaseOrderAdmin, admin.ModelAdmin):
    list_display = ('pk', 'order_num', 'order_price', 'pay_state', 'medicine_order_form', 'patient_info', 'doctor_info', 'create_time')
    search_fields = ('pk', 'order_num', 'pay_state', 'medicine_order_form')
    fieldsets = (
        (None, {'fields': ['patient_id', 'doctor_id', 'order_num', 'order_price',
                           'discount_price', 'pay_state', 'medicine_order_form']}),
    )
