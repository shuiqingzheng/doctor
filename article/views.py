from rest_framework import views, viewsets
from article.models import Article
from article.serializers import ArticleSerializer
from article.permissions import DiffUserPermission


class ArticleView(viewsets.ModelViewSet):
    permission_classes = [DiffUserPermission, ]
    serializer_class = ArticleSerializer

    def get_queryset(self):
        token = self.request.auth
        if hasattr(token, 'user'):
            user = token.user
            if hasattr(user, 'doctor'):
                return Article.objects.filter(article_doctor=user.doctor).order_by('-create_time')

        return Article.objects.filter(article_state='已发布').order_by('-create_time')
