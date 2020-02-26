from rest_framework import serializers
from diagnosis.models import DiaDetail, History
from myuser.models import PatientUser
from myuser.serializers import PatientBaseInfoSerializer


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


class HistorySerializer(serializers.ModelSerializer):

    class Meta:
        model = History
        fields = ('id', 'history_create_time', 'history_content', 'recipe')
        depth = 1


class DS(serializers.Serializer):
    base_info = PatientBaseInfoSerializer(label='患者基本信息')
    results = HistorySerializer(label='病史列表', many=True)


class DemoSerializer(serializers.Serializer):
    """
    - swagger接口显示的response
    """
    base_info = PatientBaseInfoSerializer(label='患者基本信息')
    count = serializers.IntegerField(label='总数量')
    next = serializers.URLField(label='下一页', required=False)
    previous = serializers.URLField(label='上一页', required=False)
    results = HistorySerializer(label='病史列表', many=True)
