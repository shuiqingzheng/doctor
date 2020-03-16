from rest_framework import serializers
from diagnosis.models import DiaDetail, History, Recipe, DiaMedicine, ImageDetail, VideoDetail
from myuser.models import PatientUser, UploadImage
from myuser.serializers import PatientBaseInfoSerializer
from medicine.models import Medicine
from django.conf import settings


class ImageDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImageDetail
        fields = '__all__'


class VideoDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = VideoDetail
        fields = '__all__'


class DiaDetailSerializer(serializers.ModelSerializer):
    # business_state = serializers.StringRelatedField(label='状态', read_only=True, source='order_question__business_state')
    business_state = serializers.SerializerMethodField(label='状态')

    username = serializers.SerializerMethodField()
    order_time = serializers.DateTimeField(format=settings.DATETIME_FORMAT)

    class Meta:
        model = DiaDetail
        fields = ('id', 'username', 'patient_main', 'order_time', 'business_state', 'voice_info', 'image_one', 'image_two', 'image_three', 'room_number', 'is_video', 'patient_id')

    def get_business_state(self, obj):
        o = obj.order_question
        if not o:
            return None
        return o.business_state

    def get_username(self, obj):
        # 查询患者
        try:
            patient = PatientUser.objects.get(id=obj.patient_id)
        except PatientUser.DoesNotExist:
            raise serializers.ValidationError('信息错误')
        else:
            return patient.owner.username


class PatientDiaDetailSerializer(serializers.ModelSerializer):
    order_time = serializers.DateTimeField(label='预约时间', required=False, format=settings.DATETIME_FORMAT)

    class Meta:
        model = DiaDetail
        fields = ('id', 'patient_main', 'order_time', 'voice_info', 'image_one', 'image_two', 'image_three', 'patient_id', 'doctor_id', 'is_video', 'room_number')


class SwaggerPDDSerializer(serializers.Serializer):
    is_video = serializers.BooleanField(label='是否视频复诊')
    patient_main = serializers.CharField(label='患者主诉')
    voice_info = serializers.CharField(label='录音', required=False)
    order_time = serializers.DateTimeField(label='预约时间', format=settings.DATETIME_FORMAT)
    order_price = serializers.DecimalField(label='订单总价格', max_digits=8, decimal_places=2)
    image_one = serializers.URLField(label='上传图片1', required=False)
    image_two = serializers.URLField(label='上传图片2', required=False)
    image_three = serializers.URLField(label='上传图片3', required=False)


class SwaggerUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = UploadImage
        fields = '__all__'


class HistorySerializer(serializers.ModelSerializer):

    class Meta:
        model = History
        fields = '__all__'
        depth = 1
        extra_kwargs = {
            'doctor_id': {'write_only': True},
            'patient_id': {'write_only': True},
        }


class CreateHistorySerializer(serializers.ModelSerializer):

    class Meta:
        model = History
        fields = ('id', 'history_content')


class DiaMedicineSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiaMedicine
        fields = '__all__'
        read_only_fields = ['owner', ]

    def validate_medicine_name(self, value):
        try:
            Medicine.objects.get(officical_name=value)
        except Medicine.DoesNotExist:
            raise serializers.ValidationError('{}: 该药品不存在'.format(value))
        return value


class RecipeRetrieveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = '__all__'


class RecipeSerializer(serializers.ModelSerializer):
    medicine_list = DiaMedicineSerializer(many=True)

    class Meta:
        model = Recipe
        fields = ('total_price', 'recipe_result', 'price_type', 'medicine_list')

    def create(self, validated_data):
        medicine_list = validated_data.pop('medicine_list')
        recipe = Recipe.objects.create(**validated_data)
        dia_serializer = DiaMedicineSerializer(data=medicine_list, many=True)
        dia_serializer.is_valid(raise_exception=True)
        dia_serializer.save(owner=recipe)
        return recipe


class SwaggerHistorySerializer(serializers.Serializer):
    """
    - swagger接口显示的response
    """
    base_info = PatientBaseInfoSerializer(label='患者基本信息')
    count = serializers.IntegerField(label='总数量')
    next = serializers.URLField(label='下一页', required=False)
    previous = serializers.URLField(label='上一页', required=False)
    results = HistorySerializer(label='病史列表', many=True)
