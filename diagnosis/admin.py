from django.contrib import admin
from diagnosis.models import (
    DiaDetail, ImageDetail, VideoDetail,
    Recipe, DiaMedicine, History
)

@admin.register(DiaDetail)
class DiaDetailAdmin(admin.ModelAdmin):
    list_display = ('id', 'patient_id', 'doctor_id', 'create_time')


@admin.register(ImageDetail)
class ImageDetailAdmin(admin.ModelAdmin):
    list_display = ('id', 'patient_id', 'doctor_id', 'create_time')


@admin.register(VideoDetail)
class VideoDetailAdmin(admin.ModelAdmin):
    list_display = ('id', 'patient_id', 'doctor_id', 'create_time')


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('id',)


@admin.register(DiaMedicine)
class DiaMedicineAdmin(admin.ModelAdmin):
    list_display = ('id',)


@admin.register(History)
class HistoryAdmin(admin.ModelAdmin):
    list_display = ('id',)
