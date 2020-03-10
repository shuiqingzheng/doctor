from django.urls import path
from medicine.views import MedicineView, MedicineTypeView


urlpatterns = [
    # 药品列表
    path('', MedicineView.as_view({'get': 'list'}), name='user-get-medicine'),

    path('type/<str:type_level>/', MedicineTypeView.as_view({'get': 'medicineType'}), name='user-get-medicineType'),
]
