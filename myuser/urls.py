from django.urls import path
from myuser.views import PatientView, DoctorView, SmsView
from diagnosis.views import DiaDetailView, HistoryView


urlpatterns = [
    # register
    path('sms/<str:phone>/', SmsView.as_view(), name='sms'),
    # 患者
    path('patient/register/', PatientView.as_view({'post': 'create'}), name='patient-register'),
    # path('patient/login/', PatientView.as_view({'post': 'create'}), name='patient-login'),
    # 复诊主页面
    path('patient/visit/main/', PatientView.as_view({'get': 'main'}), name='patient-visit-main'),
    # 寻找医生
    path('patient/visit/look/', DoctorView.as_view({'get': 'list'}), name='patient-visit-look'),

    # 医生
    path('doctor/register/', DoctorView.as_view({'post': 'create'}), name='doctor-register'),
    # log in
    # path('patient/login', PatientView.as_view({'post': 'login'}), name='patient-login'),

    # 医生复诊首页
    path('doctor/visit/index/', DiaDetailView.as_view({'get': 'list'}), name='patient-visit-index'),
    # 单人病例
    path('doctor/visit/<int:pk>/history/', HistoryView.as_view({'get': 'user_history'}), name='patient-visit-history'),
]
