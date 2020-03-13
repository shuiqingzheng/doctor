from django.urls import path
from order.views import OpenIDView, PayView, CallBackView


urlpatterns = [
    path('openid/<str:jscode>/', OpenIDView.as_view(), name='patient-get-openid'),
    path('pay/', PayView.as_view(), name='patient-create-bill'),
    path('order/callback/', CallBackView.as_view(), name='call-create-bill'),
]
