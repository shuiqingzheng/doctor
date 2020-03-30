from django.urls import path
from order.views import OpenIDView, PayView, callback, QuestionOrderView, MedicineOrderView


urlpatterns = [
    path('question/', QuestionOrderView.as_view({'get': 'list'}), name='question-order-list'),
    path('recipe/', MedicineOrderView.as_view({'get': 'list'}), name='recipe-order-list'),

    path('<int:pk>/', QuestionOrderView.as_view({'get': 'retrieve'}), name='order-detail'),
    path('openid/<str:jscode>/', OpenIDView.as_view(), name='patient-get-openid'),
    path('pay/', PayView.as_view(), name='patient-create-bill'),
    path('callback/', callback, name='callback-bill'),
]
