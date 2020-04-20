from django.contrib import admin
from article.models import Article


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'article_doctor', 'create_time']
