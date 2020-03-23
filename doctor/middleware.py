from django.contrib import admin
from medicine.models import MedicineImages
from medicine.admin import MedicineImagesAdmin
from django.utils.deprecation import MiddlewareMixin


class MyMiddleware(MiddlewareMixin):
    """
    : 不同用户具备不同的注册模型
    """

    def process_request(self, request):
        # 只适用于admin后台管理
        if request.path.startswith('/admin'):
            user = request.user

            if user.is_superuser:
                if not admin.site.is_registered(MedicineImages):
                    admin.site.register(MedicineImages, MedicineImagesAdmin)
            else:
                if admin.site.is_registered(MedicineImages):
                    admin.site.unregister(MedicineImages)
