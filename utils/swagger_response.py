from rest_framework import serializers


class ResponseSuccessSerializer(serializers.Serializer):
    detail = serializers.CharField(label='响应字段名称')