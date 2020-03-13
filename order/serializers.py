from rest_framework import serializers
from order.models import QuestionOrder


class QuestionOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionOrder
        fields = '__all__'


class PaySerializer(serializers.Serializer):
    openid = serializers.CharField(label='openid', required=True)
    order_id = serializers.IntegerField(label='订单id', required=True)

    def validate(self, attrs):
        order_id = attrs.get('order_id')
        try:
            QuestionOrder.objects.get(id=order_id)
        except QuestionOrder.DoesNotExist:
            raise serializers.ValidationError('对应的订单不存在')

        return attrs


class CallBackSerializer(serializers.Serializer):
    pass
