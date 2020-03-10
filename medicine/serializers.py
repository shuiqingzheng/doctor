from rest_framework import serializers
from medicine.models import Medicine, MedicineType


class Medicineserializer(serializers.ModelSerializer):
    class Meta:
        model = Medicine
        fields = '__all__'


class MedicineTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicineType
        # fields = '__all__'
        exclude = ['medicine_number']
