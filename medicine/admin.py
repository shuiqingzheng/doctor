from django import forms
from django.contrib import admin, messages
from django.shortcuts import reverse
from django.utils.html import format_html
from django.conf import settings
from django.http import HttpResponseRedirect
from medicine.models import Medicine, MedicineType, MedicineStock, MedicineImages

TOTAL_IMAGE_COUNT = 5


@admin.register(MedicineType)
class MedicineTypeAdmin(admin.ModelAdmin):

    def father_name(self, obj):
        type_obj = MedicineType.objects.get(id=obj.father_id)
        url = reverse('admin:medicine_medicinetype_change', args=[type_obj.id])
        return format_html("<a href='{}'>{}</a>", url, type_obj.type_name)

    list_display = ('pk', 'type_name', 'father_name')
    father_name.short_description = '父类名称'
    search_fields = ('type_name', 'id')


class ImagesInline(admin.TabularInline):

    def image_tag(self, obj):
        path = ':'.join([settings.NGINX_SERVER, str(settings.NGINX_PORT)])
        return format_html('<img src="{}" width=100 height=100 />'.format(path + obj.image.url))

    fieldsets = (
        (None, {'fields': ('image_tag', 'image', 'is_first')}),
    )
    readonly_fields = ('image_tag',)
    image_tag.short_description = '图片预览'
    model = MedicineImages
    max_num = 5
    show_change_link = True
    template = 'medicine-image.html'


@admin.register(Medicine)
class MedicineAdmin(admin.ModelAdmin):
    list_display = ('pk', 'officical_name', 'product_name', 'type_one', 'type_two', 'type_three', 'product_state')
    search_fields = ('pk', 'officical_name', 'product_name', 'type_one', 'type_two', 'type_three')
    inlines = [
        ImagesInline,
    ]
    fieldsets = (
        ('药品类型(请认真核对类型名称)', {'fields': ['type_one', 'type_two', 'type_three']}),
        ('药品信息', {'fields': ['officical_name', 'product_name', 'standard',
                             'price', 'product_source', 'good_for', 'detail',
                             'product_state']})
    )

    def save_formset(self, request, form, formset, change):
        """
        Given an inline formset save it to the database.
        """
        if len(formset.cleaned_data) > TOTAL_IMAGE_COUNT:
            instances = formset.save(commit=False)
            for ins in instances:
                continue
            formset.save_m2m()

            messages.error(request, '药品对应的图片不可超过五张(<=5), 请核查...')
            return HttpResponseRedirect(request.path)

        formset.save()


@admin.register(MedicineStock)
class MedicineStockAdmin(admin.ModelAdmin):
    list_display = ('id', 'medicine_name', 'medicine_description', 'create_time')
    search_fields = ('medicine_name', )


@admin.register(MedicineImages)
class MedicineImagesAdmin(admin.ModelAdmin):

    def image_tag(self, obj):
        path = ':'.join([settings.NGINX_SERVER, str(settings.NGINX_PORT)])
        return format_html('<img src="{}" />'.format(path + obj.image.url))

    list_display = ('id', 'is_first', 'image', 'owner')
    fieldsets = fieldsets = (
        (None, {'fields': ('owner', 'image_tag', 'image', 'is_first')}),
    )
    readonly_fields = ('image_tag',)
    image_tag.short_description = '图片展示'

    def save_model(self, request, obj, form, change):
        """
        判定是否超过五张图片
        """
        num = obj.owner.medicine_images.count()
        if num >= TOTAL_IMAGE_COUNT and not change:
            messages.set_level(request, messages.ERROR)
            return messages.error(request, '药品对应的图片不可超过五张(<=5), 请核查...')
        else:
            obj.save()
