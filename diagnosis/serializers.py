from rest_framework import serializers
from diagnosis.models import DiaDetail, History, Recipe, DiaMedicine
from myuser.models import PatientUser
from myuser.serializers import PatientBaseInfoSerializer
from medicine.models import Medicine


class DiaDetailSerializer(serializers.ModelSerializer):
    business_state = serializers.StringRelatedField(label='状态', read_only=True, source='order_question__business_state')

    username = serializers.SerializerMethodField()

    class Meta:
        model = DiaDetail
        fields = ('id', 'username', 'patient_main', 'order_time', 'business_state')

    def get_username(self, obj):
        # 查询患者
        try:
            patient = PatientUser.objects.get(id=obj.patient_id)
        except PatientUser.DoesNotExist:
            raise serializers.ValidationError('信息错误')
        else:
            return patient.owner.username


class Demo(serializers.Serializer):
    o = serializers.ImageField(required=True)


class PatientDiaDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = DiaDetail
        fields = ('id', 'patient_main', 'order_time', 'voice_info', 'image_one', 'image_two', 'image_three', 'patient_id', 'doctor_id')


class SwaggerPDDSerializer(serializers.Serializer):
    patient_main = serializers.CharField(label='患者主诉')
    voice_info = serializers.CharField(label='录音', required=False)
    order_time = serializers.DateTimeField(label='预约时间', required=False)
    image_one = serializers.ImageField(label='上传图片1', required=False)
    image_two = serializers.ImageField(label='上传图片2', required=False)
    image_three = serializers.ImageField(label='上传图片3', required=False)


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
