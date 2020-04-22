from django.conf import settings
from rest_framework import serializers
from article.models import Article


class ArticleSerializer(serializers.ModelSerializer):
    create_time = serializers.DateTimeField(format=settings.DATETIME_TOTAL_FORMAT, read_only=True)
    author = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Article
        fields = '__all__'
        read_only_fields = ['article_click', 'article_type', 'special', 'article_doctor']

    def get_author(self, obj):
        doctor = obj.article_doctor

        if not doctor:
            return

        return doctor.owner.username

    def create(self, validated_data):
        doctor = self.context['view'].request.auth.user.doctor
        validated_data.update({
            'article_doctor': doctor
        })
        return Article.objects.create(**validated_data)
