from rest_framework import serializers
from order.models import QuestionOrder, MedicineOrder
from myuser.models import DoctorUser
from myuser.serializers import DoctorRetrieveSerializer
from diagnosis.serializers import RecipeRetrieveSerializer, DiaMedicineSerializer
from django.conf import settings


class MedicineOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicineOrder
        fields = '__all__'


class OrderMedicineOrderSerializer(serializers.ModelSerializer):
    recipe_info = serializers.SerializerMethodField(label='处方信息')

    create_time = serializers.DateTimeField(format=settings.DATETIME_TOTAL_FORMAT, required=False)

    class Meta:
        model = MedicineOrder
        exclude = ['patient_id', 'doctor_id', 'nonce_str']

    def get_recipe_info(self, obj):
        response_data = dict()
        recipe = obj.recipe

        if not recipe:
            return {'detail': '处方被删除'}

        serializer_recipe = RecipeRetrieveSerializer(recipe)
        response_data.update(serializer_recipe.data)

        medicine_queryset = recipe.diamedicine.all()
        if not medicine_queryset:
            return response_data

        serializer_medicine = DiaMedicineSerializer(medicine_queryset, many=True)
        response_data['medicine_info'] = serializer_medicine.data

        return response_data


class QuestionOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionOrder
        fields = '__all__'


class OrderQuestionOrderSerializer(serializers.ModelSerializer):
    doctor_info = serializers.SerializerMethodField(label='医生信息')

    create_time = serializers.DateTimeField(format=settings.DATETIME_TOTAL_FORMAT, required=False)

    class Meta:
        model = QuestionOrder
        exclude = ['patient_id', 'doctor_id', 'nonce_str']

    def get_doctor_info(self, obj):
        try:
            doctor = DoctorUser.objects.get(pk=obj.doctor_id)
        except DoctorUser.DoesNotExist:
            return {'detail': '医生账号不存在'}

        s = DoctorRetrieveSerializer(doctor)
        return s.data


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
