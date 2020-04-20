from django.urls import path
from article.views import ArticleView

urlpatterns = [
    path('', ArticleView.as_view({
        'get': 'list',
        'post': 'create',
    }), name='article'),

    path('<int:pk>/', ArticleView.as_view({
        'put': 'partial_update',
        'get': 'retrieve'
    }), name='article-pk'),

]
