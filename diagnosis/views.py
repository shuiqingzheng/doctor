from rest_framework import viewsets, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django_filters.utils import timezone
# from django_filters.rest_framework import DjangoFilterBackend
from diagnosis.models import DiaDetail, History, Recipe
from diagnosis.filters import SearchDiaDetail
from diagnosis.serializers import (
    DiaDetailSerializer, HistorySerializer, SwaggerHistorySerializer,
    RecipeSerializer, CreateHistorySerializer,
)
from myuser.models import PatientUser
from myuser.serializers import PatientBaseInfoSerializer
from drf_yasg.utils import swagger_auto_schema
from oauth2_provider.contrib.rest_framework import TokenHasScope
from utils.swagger_response import ResponseSuccessSerializer


class DiaDetailView(viewsets.ModelViewSet):
    permission_classes = [AllowAny, ]
    # requsired_scopes = ['basic']
    queryset = DiaDetail.objects.order_by('-order_time')
    serializer_class = DiaDetailSerializer
    filter_backends = [SearchDiaDetail, ]
    model = DiaDetail

    def list(self, request, *args, **kwargs):
        """
        - 所有患者的复诊记录
        """
        return super().list(request, *args, **kwargs)


class HistoryView(viewsets.ModelViewSet):
    permission_classes = [TokenHasScope, ]
    required_scopes = ['doctor']
    queryset = History.objects.order_by('-history_create_time')
    serializer_class = CreateHistorySerializer
    model = History

    def valid_patient_info(self, pk):
        try:
            patient = PatientUser.objects.get(id=pk)
        except PatientUser.DoesNotExist:
            return Response({'detail': '用户不存在'}, status=status.HTTP_404_NOT_FOUND)
        return patient

    def create(self, request, pk, *args, **kwargs):
        """
        - 医生为患者创建病历
        """
        # 患者基本信息
        patient = self.valid_patient_info(pk)
        data = {
            'patient_id': patient.id,
            'doctor_id': request.auth.user.id,
            'history_create_time': timezone.now()
        }
        data.update(**request.data)
        s = HistorySerializer(data=data)
        s.is_valid(raise_exception=True)
        s.save()
        print(s)
        return Response(s.data)

    @swagger_auto_schema(responses={'200': SwaggerHistorySerializer})
    def user_history(self, request, pk, *args, **kwargs):
        """
        - 患者的病历（返回数据包含基本信息、病历列表）
        """
        # 患者基本信息
        patient = self.valid_patient_info(pk)
        serializer_patient = PatientBaseInfoSerializer(instance=patient)

        # 所有病例
        all_history = self.model.objects.filter(patient_id=pk)
        page = self.paginate_queryset(all_history)
        if page is not None:
            serializer = HistorySerializer(page, many=True)
            response = self.get_paginated_response(serializer.data)
            response.data['base_info'] = serializer_patient.data
            return response

        response_context = {
            'base_info': serializer_patient.data,
            'history_list': serializer.data
        }

        return Response(response_context)


class RecipeView(viewsets.ModelViewSet):
    permission_classes = [TokenHasScope, ]
    required_scopes = ['doctor']
    queryset = Recipe.objects.order_by('-pk')
    serializer_class = RecipeSerializer
    lookup_field = 'history_id'
    model = Recipe

    @swagger_auto_schema(responses={'200': ResponseSuccessSerializer})
    def create(self, request, history_id, *args, **kwargs):
        """
        - 医生为患者根据病历ID进行创建处方
        """
        try:
            history = History.objects.get(pk=history_id)
        except History.DoesNotExist:
            return Response({'detail': '病历未创建'}, status=status.HTTP_404_NOT_FOUND)
        else:
            recipe_serializer = RecipeSerializer(data=request.data)
            recipe_serializer.is_valid(raise_exception=True)
            recipe = recipe_serializer.save()
            # TODO 异步生成药品订单
            history.recipe = recipe
            history.save()
        return Response({'detail': '处方提交成功'})
