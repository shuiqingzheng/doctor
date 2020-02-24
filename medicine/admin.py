from django.contrib import admin
from medicine.models import Medicine, MedicineType


@admin.register(MedicineType)
class MedicineTypeAdmin(admin.ModelAdmin):
    list_display = ('pk', 'type_name')


@admin.register(Medicine)
class MedicineAdmin(admin.ModelAdmin):
    list_display = ('pk', 'officical_name')