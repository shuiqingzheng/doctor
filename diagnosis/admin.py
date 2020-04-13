from django.contrib import admin
from django.shortcuts import reverse
from django.utils.html import format_html
from diagnosis.models import (
    DiaDetail, ImageDetail, VideoDetail,
    Recipe, DiaMedicine, History, Prescription
)
from order.admin import BaseOrderAdmin


class BaseDetailAdmin(BaseOrderAdmin):
    pass


@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = ('id', 'patient_id', 'doctor_id', 'nums', 'create_time')
    search_fields = ('patient_id', 'doctor_id')


@admin.register(DiaDetail)
class DiaDetailAdmin(BaseDetailAdmin, admin.ModelAdmin):
    list_display = ('id', 'patient_main', 'is_video', 'room_number', 'patient_id', 'doctor_id', 'order_question', 'order_medicine', 'create_time')
    search_fields = ('patient_main', 'room_number')


@admin.register(ImageDetail)
class ImageDetailAdmin(BaseDetailAdmin, admin.ModelAdmin):
    list_display = ('id', 'patient_info', 'doctor_info', 'order_question', 'order_medicine', 'create_time', )


@admin.register(VideoDetail)
class VideoDetailAdmin(BaseDetailAdmin, admin.ModelAdmin):
    list_display = ('id', 'patient_info', 'doctor_info', 'order_question', 'order_medicine', 'create_time')


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'recipe_result', 'price_type')


@admin.register(DiaMedicine)
class DiaMedicineAdmin(admin.ModelAdmin):
    def recipe_info(self, obj):
        url = reverse('admin:diagnosis_recipe_change', args=[obj.owner.id])
        return format_html("<a href='{}'>{}</a>", url, obj.owner.id)

    list_display = ('id', 'medicine_name', 'medicine_num', 'medicine_price', 'recipe_info')
    recipe_info.short_description = '处方信息'


@admin.register(History)
class HistoryAdmin(BaseDetailAdmin, admin.ModelAdmin):
    list_display = ('id', 'history_content', 'history_create_time', 'patient_info', 'doctor_info', 'recipe')
