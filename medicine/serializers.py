from rest_framework import serializers
from medicine.models import Medicine


class Medicineserializer(serializers.ModelSerializer):
    class Meta:
        model = Medicine
        fields = '__all__'
