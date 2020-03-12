from django.urls import path
from medicine.views import MedicineView, MedicineTypeView, MedicineStockView


urlpatterns = [
    # 药品列表
    path('', MedicineView.as_view({'get': 'list'}), name='medicine-list'),
    path('<int:pk>/', MedicineView.as_view({'get': 'retrieve'}), name='medicine-detail'),

    # 库存
    path('stock/', MedicineStockView.as_view({'post': 'create', 'get': 'list'}), name='medicinestock-create'),
    path('stock/<int:pk>/', MedicineStockView.as_view({'delete': 'destroy', 'get': 'retrieve'}), name='medicinestock'),

    path('type/<str:type_level>/', MedicineTypeView.as_view({'get': 'medicineType'}), name='medicineType-list'),
]
