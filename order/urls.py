from django.urls import path
from order.views import OpenIDView, PayView, CallBackView, QuestionOrderView


urlpatterns = [
    path('', QuestionOrderView.as_view({'get': 'list'}), name='order-list'),
    path('<int:pk>/', QuestionOrderView.as_view({'get': 'retrieve'}), name='order-detail'),
    path('openid/<str:jscode>/', OpenIDView.as_view(), name='patient-get-openid'),
    path('pay/', PayView.as_view(), name='patient-create-bill'),
    path('order/callback/', CallBackView.as_view(), name='call-create-bill'),
]
