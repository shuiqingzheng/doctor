"""admin URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from medicine.views import choose_one, choose_two_and_three

schema_view = get_schema_view(
    openapi.Info(
        title="汉典云健康系统API",
        default_version='v1',
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('api/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('api-docs/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

    path('admin/', admin.site.urls),
    path('choose_one/', choose_one),
    path('choose_two_and_three/', choose_two_and_three),

    path('o/', include('oauth2_provider.urls', namespace='oauth2_provider')),

    path('', include('myuser.urls'), name='myuser'),
    path('order/', include('order.urls'), name='order'),
    path('diag/', include('diagnosis.urls'), name='diagnosis'),
    path('medicine/', include('medicine.urls'), name='medicine'),
]
