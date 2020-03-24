from rest_framework import serializers
from medicine.models import Medicine, MedicineType, MedicineStock
from django.conf import settings


class Medicineserializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField(label='图片封面')

    class Meta:
        model = Medicine
        # fields = '__all__'
        exclude = ['product_images']

    def get_image_url(self, obj):
        address = ':'.join((settings.NGINX_SERVER, str(settings.NGINX_PORT)))

        if self.context['view'].action == 'retrieve':
            obj_images = obj.medicine_images.all()
            response_url = [''.join([address, o.image.url]) for o in obj_images]
            return response_url

        obj_images = obj.medicine_images.filter(is_first=True)

        if not obj_images:
            obj_images = obj.medicine_images.order_by('-pk')

        if obj_images:
            url = obj_images[0].image.url
            return ''.join([address, url])
        else:
            return


class MedicineTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicineType
        # fields = '__all__'
        exclude = ['medicine_number']


class MedicineStockSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicineStock
        fields = '__all__'
