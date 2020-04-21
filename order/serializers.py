from rest_framework import serializers
from order.models import QuestionOrder, MedicineOrder
from myuser.models import DoctorUser
from myuser.serializers import DoctorRetrieveSerializer
from diagnosis.serializers import RecipeRetrieveSerializer, DiaMedicineSerializer
from django.conf import settings
from medicine.models import Medicine


class MedicineOrderSerializer(serializers.ModelSerializer):

    class Meta:
        model = MedicineOrder
        fields = '__all__'


class OrderMedicineOrderSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    recipe_info = serializers.SerializerMethodField(label='处方信息')

    create_time = serializers.DateTimeField(format=settings.DATETIME_TOTAL_FORMAT, required=False)

    diag_time = serializers.SerializerMethodField()

    class Meta:
        model = MedicineOrder
        exclude = ['patient_id', 'doctor_id', 'nonce_str']

    def get_diag_time(self, val):
        if not hasattr(val, 'diadetail'):
            return
        t = val.diadetail.order_time
        return t.strftime('%Y-%m-%d %H:%M:%S')

    def get_image_url(self, obj):
        address = ':'.join((settings.NGINX_SERVER, str(settings.NGINX_PORT)))
        if not hasattr(obj, 'recipe'):
            return

        recipe = obj.recipe
        if not recipe:
            return

        medicine_queryset = recipe.diamedicine.all()
        if not medicine_queryset:
            return

        ms = Medicine.objects.filter(officical_name__in=[m.medicine_name for m in medicine_queryset])
        if not ms:
            return

        m = ms[0]
        m_images = m.medicine_images.all()

        if not m_images:
            return

        image_obj = m_images[0]
        if not image_obj:
            return

        url = image_obj.image.url
        return ''.join([address, url])

    def get_recipe_info(self, obj):
        response_data = dict()
        if not hasattr(obj, 'recipe'):
            return {'detail': '处方被删除'}

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

    diag_time = serializers.SerializerMethodField()

    class Meta:
        model = QuestionOrder
        exclude = ['patient_id', 'doctor_id', 'nonce_str']

    def get_diag_time(self, val):
        if not hasattr(val, 'diadetail'):
            return
        t = val.diadetail.order_time

        if not t:
            return
        return t.strftime('%Y-%m-%d %H:%M:%S')

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
