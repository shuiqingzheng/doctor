from django.urls import path
from myuser.views import (
    index,
    PatientView, DoctorView, SmsView,
    PatientInfoView, DoctorInfoView,
    DoctorSetTimeView
)
from aduser.views import DoctorPasswordView, PatientPasswordView


urlpatterns = [
    # index
    path('', index, name='index'),
    # register
    path('sms/<str:phone>/', SmsView.as_view(), name='sms'),
    # 患者
    path('patient/register/', PatientView.as_view({'post': 'create'}), name='patient-register'),
    path('patient/info/', PatientInfoView.as_view({'get': 'retrieve'}), name='patient-info'),
    path('patient/resetpassword/', PatientPasswordView.as_view({'put': 'update'}), name='patient-reset-password'),
    path('patient/update/', PatientInfoView.as_view({'post': 'update'}), name='patient-info-update'),

    # 医生
    path('doctor/register/', DoctorView.as_view({'post': 'create'}), name='doctor-register'),
    path('doctor/resetpassword/', DoctorPasswordView.as_view({'put': 'update'}), name='doctor-reset-password'),
    path('doctor/info/', DoctorInfoView.as_view({'get': 'retrieve'}), name='doctor-info'),
    path('doctor/update/', DoctorInfoView.as_view({'post': 'update'}), name='doctor-info-update'),

    # 复诊医生列表
    path('doctor/review/', DoctorView.as_view({'get': 'list'}), name='doctor-review-list'),
    path('doctor/review/<int:pk>/', DoctorView.as_view({'get': 'retrieve'}), name='doctor-review-pk'),

    # 预约时间
    path('doctor/time/', DoctorSetTimeView.as_view({'get': 'list', 'post': 'create'}), name='doctor-settime'),
    path('doctor/time/<int:pk>/', DoctorSetTimeView.as_view({'delete': 'destroy'}), name='doctor-delete-time'),
]
