from django.urls import path
from myuser.views import (
    PatientView, DoctorView, SmsView,
    PatientInfoView, DoctorInfoView,
    DoctorSetTimeView
)
# from medicine.views import MedicineDoctorView, MedicinePatientView


urlpatterns = [
    # register
    path('sms/<str:phone>/', SmsView.as_view(), name='sms'),
    # 患者
    path('patient/register/', PatientView.as_view({'post': 'create'}), name='patient-register'),
    path('patient/update/', PatientInfoView.as_view({'post': 'update'}), name='patient-info-update'),
    # path('patient/login/', PatientView.as_view({'post': 'create'}), name='patient-login'),
    # 复诊主页面
    # path('patient/visit/main/', PatientView.as_view({'get': 'main'}), name='patient-visit-main'),
    # 寻找医生
    # path('patient/visit/look/', DoctorView.as_view({'get': 'list'}), name='patient-visit-look'),
    # 复诊医生的详情（医生条件：1.被审核; 2.开通复诊）
    # path('patient/visit/doctor/<int:pk>/', DoctorView.as_view({'get': 'retrieve'}), name='patient-visit-doctor'),
    # 复诊患者创建病情描述
    # path('patient/visit/create/<int:doctor_id>/', DiaDetailPatientView.as_view({'post': 'create'}), name='patient-visit-create'),
    # 药品列表
    # path('patient/medicine/', MedicinePatientView.as_view({'get': 'list'}), name='patient-medicine'),

    # 医生
    path('doctor/register/', DoctorView.as_view({'post': 'create'}), name='doctor-register'),
    path('doctor/info/', DoctorInfoView.as_view({'get': 'retrieve'}), name='doctor-info'),
    path('doctor/update/', DoctorInfoView.as_view({'post': 'update'}), name='doctor-info-update'),

    # 复诊医生列表
    path('doctor/review/', DoctorView.as_view({'get': 'list'}), name='doctor-review-list'),
    path('doctor/review/<int:pk>/', DoctorView.as_view({'get': 'retrieve'}), name='doctor-review-pk'),

    # 医生复诊首页
    # path('doctor/visit/index/', DiaDetailDoctorView.as_view({'get': 'list'}), name='doctor-visit-index'),
    # 查看单人病例
    # path('doctor/visit/<int:pk>/history/', HistoryView.as_view({'get': 'user_history'}), name='doctor-visit-history'),
    # 创建病历
    # path('doctor/visit/<int:pk>/history/create/', HistoryView.as_view({'post': 'create'}), name='doctor-visit-create-history'),
    # 开处方
    # path('doctor/visit/<int:history_id>/recipe/', RecipeView.as_view({'post': 'create'}), name='doctor-create-recipe'),
    # 药品列表
    # path('doctor/medicine/', MedicineDoctorView.as_view({'get': 'list'}), name='doctor-medicine'),
    # 预约时间
    path('doctor/time/', DoctorSetTimeView.as_view({'get': 'list', 'post': 'create'}), name='doctor-settime'),
    # path('doctor/time/create/', DoctorSetTimeView.as_view({'post': 'create'}), name='doctor-settime'),
]
