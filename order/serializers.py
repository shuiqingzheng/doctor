from rest_framework import serializers
from order.models import QuestionOrder, MedicineOrder
from django.conf import settings


class MedicineOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicineOrder
        fields = '__all__'


class OrderMedicineOrderSerializer(serializers.ModelSerializer):
    create_time = serializers.DateTimeField(format=settings.DATETIME_TOTAL_FORMAT, required=False)

    class Meta:
        model = MedicineOrder
        exclude = ['patient_id', 'doctor_id', 'nonce_str']


class QuestionOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionOrder
        fields = '__all__'


class OrderQuestionOrderSerializer(serializers.ModelSerializer):
    create_time = serializers.DateTimeField(format=settings.DATETIME_TOTAL_FORMAT, required=False)

    class Meta:
        model = QuestionOrder
        exclude = ['patient_id', 'doctor_id', 'nonce_str']


class PaySerializer(serializers.Serializer):
    openid = serializers.CharField(label='openid', required=True)
    order_id = serializers.IntegerField(label='订单id', required=True)
    ORDER_TYPE_CHOICES = (
        ('question', 'question'),
        ('medicine', 'medicine')
    )
    order_type = serializers.ChoiceField(choices=ORDER_TYPE_CHOICES, label='支付订单类型', required=True)

    def validate(self, attrs):
        order_id = attrs.get('order_id')
        order_type = attrs.get('order_type')
        if order_type == 'question':
            try:
                QuestionOrder.objects.get(id=order_id)
            except QuestionOrder.DoesNotExist:
                raise serializers.ValidationError('对应的咨询订单不存在')
        else:
            try:
                MedicineOrder.objects.get(id=order_id)
            except MedicineOrder.DoesNotExist:
                raise serializers.ValidationError('对应的处方订单不存在')

        return attrs


class CallBackSerializer(serializers.Serializer):
    pass
