from django.urls import path
from diagnosis.views import (
    HistoryView, DiaDetailView, DiaDetailPatientView,
    RecipeView
)
from myuser.views import PatientView


urlpatterns = [
    # 病历
    path('history/<int:patient_id>/', HistoryView.as_view({'get': 'user_history'}), name='history-pk-detail'),
    path('history/<int:patient_id>/<int:diagdetail_id>/', HistoryView.as_view({'post': 'create'}), name='history-create'),

    # 复诊
    # 复诊记录：医生-全部；患者-个人所有
    path('review/', DiaDetailView.as_view({'get': 'list'}), name='diadetail-list'),
    path('review/<int:pk>/', DiaDetailView.as_view({'get': 'retrieve'}), name='diadetail-retrieve'),
    # 复诊患者创建病情描述
    path('review/create/<int:doctor_id>/', DiaDetailPatientView.as_view({'post': 'create'}), name='diadetail-create'),
    # path('review/uploadimage/', UploadImageView.as_view({'post': 'create'}), name='diadetail-uploadimage'),
    # 患者复诊主页面
    path('review/patient/', PatientView.as_view({'get': 'main'}), name='patient-review-main'),

    # 处方
    # 医生创建处方
    path('recipe/create/<int:history_id>/', RecipeView.as_view({'post': 'create'}), name='doctor-create-recipe'),
    # 根据病历获取处方
    path('recipe/<int:history_id>/', RecipeView.as_view({'get': 'retrieve'}), name='recipe-retrieve'),

]
