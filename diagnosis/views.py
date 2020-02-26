from rest_framework import viewsets, filters
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from diagnosis.models import DiaDetail, History
from diagnosis.filters import SearchDiaDetail
from diagnosis.pagination import UserHistoryCustomPagination
from diagnosis.serializers import (
    DiaDetailSerializer, HistorySerializer, DemoSerializer,
    DS
)
from myuser.models import PatientUser
from myuser.serializers import PatientBaseInfoSerializer
from drf_yasg.utils import swagger_auto_schema


class DiaDetailView(viewsets.ModelViewSet):
    permission_classes = [AllowAny, ]
    # requsired_scopes = ['basic']
    queryset = DiaDetail.objects.order_by('-order_time')
    serializer_class = DiaDetailSerializer
    filter_backends = [SearchDiaDetail, ]
    model = DiaDetail


class HistoryView(viewsets.ModelViewSet):
    permission_classes = [AllowAny, ]
    # requsired_scopes = ['basic']
    queryset = History.objects.order_by('-history_create_time')
    serializer_class = HistorySerializer
    model = History

    @swagger_auto_schema(responses={'200': DemoSerializer})
    def user_history(self, request, pk, *args, **kwargs):
        # 患者基本信息
        try:
            patient = PatientUser.objects.get(id=pk)
        except PatientUser.DoesNotExist:
            pass
        else:
            serializer_patient = PatientBaseInfoSerializer(instance=patient)

        # 所有病例
        all_history = self.model.objects.filter(patient_id=pk)
        page = self.paginate_queryset(all_history)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            response = self.get_paginated_response(serializer.data)
            response.data['base_info'] = serializer_patient.data
            return response

        response_context = {
            'base_info': serializer_patient.data,
            'history_list': serializer.data
        }

        return Response(response_context)
