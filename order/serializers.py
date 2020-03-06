from rest_framework import serializers
from order.models import QuestionOrder


class QuestionOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionOrder
        fields = '__all__'
