from django.contrib import admin
from order.models import QuestionOrder, MedicineOrder


@admin.register(QuestionOrder)
class QuestionOrderAdmin(admin.ModelAdmin):
    list_display = ('pk', 'doctor_id')


@admin.register(MedicineOrder)
class MedicineOrderAdmin(admin.ModelAdmin):
    list_display = ('pk', 'doctor_id')