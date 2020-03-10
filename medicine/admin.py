from django.contrib import admin
from django.shortcuts import reverse
from django.utils.html import format_html
from medicine.models import Medicine, MedicineType


@admin.register(MedicineType)
class MedicineTypeAdmin(admin.ModelAdmin):
    def father_name(self, obj):
        type_obj = MedicineType.objects.get(id=obj.father_id)
        url = reverse('admin:medicine_medicinetype_change', args=[type_obj.id])
        return format_html("<a href='{}'>{}</a>", url, type_obj.type_name)

    list_display = ('pk', 'type_name', 'father_name')
    father_name.short_description = '父类名称'
    search_fields = ('type_name', 'id')


@admin.register(Medicine)
class MedicineAdmin(admin.ModelAdmin):
    list_display = ('pk', 'officical_name', 'product_name', 'type_one', 'type_two', 'type_three', 'product_state')
    search_fields = ('pk', 'officical_name', 'product_name', 'type_one', 'type_two', 'type_three')
