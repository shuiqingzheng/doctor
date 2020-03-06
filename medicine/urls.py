from django.urls import path
from medicine.views import MedicineView


urlpatterns = [
    # 药品列表
    path('', MedicineView.as_view({'get': 'list'}), name='user-get-medicine'),
]
