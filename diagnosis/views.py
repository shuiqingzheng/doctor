from rest_framework import viewsets, status
from django.http import JsonResponse
# from rest_framework.permissions import AllowAny
# from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from django_filters.utils import timezone
from django.http import QueryDict, Http404
from django.db import transaction
# from django_filters.rest_framework import DjangoFilterBackend
from diagnosis.models import DiaDetail, History, Recipe, DiaMedicine, Prescription
from diagnosis.filters import SearchDiaDetail
from diagnosis.serializers import (
    DiaDetailSerializer, HistorySerializer, SwaggerHistorySerializer,
    RecipeSerializer, CreateHistorySerializer, PatientDiaDetailSerializer,
    SwaggerPDDSerializer, RecipeRetrieveSerializer, DiaMedicineSerializer,
    PrescriptionSerializer
)
from medicine.permissions import TokenHasPermission
from myuser.models import PatientUser, DoctorUser
from myuser.permissions import (
    DoctorVisitPermission, DoctorBasePermission, DoctorCreatePermission
)
from myuser.serializers import PatientBaseInfoSerializer
from drf_yasg.utils import swagger_auto_schema
from oauth2_provider.contrib.rest_framework import TokenHasScope
from utils.swagger_response import ResponseSuccessSerializer
from utils.generate import create_order_number
from myuser.permissions import PatientBasePermission
from order.serializers import QuestionOrderSerializer, MedicineOrderSerializer
from order.models import QuestionOrder, MedicineOrder


class PrescriptionView(viewsets.ModelViewSet):
    """
    - 拍方抓药
    """
    permission_classes = [TokenHasPermission, ]
    serializer_class = PrescriptionSerializer
    queryset = Prescription.objects.order_by('-create_time')

    def get_queryset(self):
        token = self.request.auth

        if token is not None:
            if hasattr(token.user, 'patient'):
                return self.queryset.filter(patient_id=token.user.patient.id)
            if hasattr(token.user, 'doctor'):
                return self.queryset.filter(doctor_id=token.user.doctor.id)

        return self.queryset


class DiaDetailView(viewsets.ModelViewSet):
    """
    - 获取复诊详情列表(可根据姓名、手机号查询)
    """
    permission_classes = [TokenHasPermission, ]
    serializer_class = DiaDetailSerializer
    queryset = DiaDetail.objects.order_by('-create_time')
    filter_backends = [SearchDiaDetail, ]
    model = DiaDetail

    def get_queryset(self):
        token = self.request.auth

        if token is not None:
            if hasattr(token.user, 'patient'):
                return self.queryset.filter(patient_id=token.user.patient.id)
            if hasattr(token.user, 'doctor'):
                return self.queryset.filter(doctor_id=token.user.doctor.id, order_question__business_state='待会诊')

        return self.queryset

    def retrieve(self, request, *args, **kwargs):
        """
        - 获取复诊详情
        """
        user = self.request.auth.user
        response_data = dict()
        instance = self.get_object()

        if hasattr(user, 'patient'):
            patient = user.patient
        else:
            try:
                patient = PatientUser.objects.get(id=instance.patient_id)
            except PatientUser.DoesNotExist:
                raise ValueError('复诊详情的患者账户不存在')

        serializer = self.get_serializer(instance)
        serializer_patient = PatientBaseInfoSerializer(instance=patient)
        response_data['base_info'] = serializer_patient.data
        response_data['review_info'] = serializer.data

        return Response(response_data)


class DiaDetailPatientView(viewsets.ModelViewSet):
    permission_classes = [TokenHasScope, PatientBasePermission]
    required_scopes = ['patient']
    serializer_class = SwaggerPDDSerializer
    queryset = DiaDetail.objects.order_by('-create_time')
    filter_backends = [SearchDiaDetail, ]
    lookup_field = 'doctor_id'
    model = DiaDetail

    def valid_doctor_info(self, pk):
        try:
            doctor = DoctorUser.objects.get(id=pk)
        except DoctorUser.DoesNotExist:
            raise Http404

        return doctor

    def create(self, request, doctor_id, *args, **kwargs):
        """
        - 复诊患者创建病情描述(同时创建咨询订单)
        """
        data = request.data
        doctor = self.valid_doctor_info(doctor_id)

        if isinstance(data, QueryDict):
            data = data.dict()

        order_data = dict()
        diadetail_data = dict()
        for key, value in data.items():
            if not value:
                continue

            if hasattr(QuestionOrder, key):
                order_data[key] = value

            if hasattr(DiaDetail, key):
                diadetail_data[key] = value

        try:
            patient = PatientUser.objects.get(owner=request.auth.user)
        except PatientUser.DoesNotExist:
            raise ValueError('不存在')

        # 支付接口更改状态 pay_state
        # 订单默认信息
        order_default_info = {
            'order_num': 'orde_' + create_order_number(QuestionOrder, 'orde_'),
            'pay_state': '未支付',   # 订单状态
            'question_order_form': '复诊',
            'business_state': '待支付',   # 复诊的状态
            'patient_id': patient.id,
            'doctor_id': doctor.id
        }
        order_data.update(order_default_info)

        with transaction.atomic():
            point = transaction.savepoint()

            try:
                q = QuestionOrderSerializer(data=order_data)
                q_valid = q.is_valid()
                if not q_valid:
                    transaction.savepoint_rollback(point)
                    return JsonResponse(q.errors, status=400)

                q_obj = q.save()
                diadetail_data.update({
                    'patient_id': patient.id,
                    'doctor_id': doctor.id,
                    'room_number': int('{}{}{}'.format(patient.id, doctor.id, q_obj.id))
                })
                s = PatientDiaDetailSerializer(data=diadetail_data)
                s_valid = s.is_valid()
                if not s_valid:
                    transaction.savepoint_rollback(point)
                    return JsonResponse(s.errors, status=400)

                s.save(order_question=q_obj)
            except Exception as e:
                transaction.savepoint_rollback(point)
                raise e
            transaction.savepoint_commit(point)

        response_data = s.data
        response_data.update(
            {'order_id': q_obj.id}
        )

        return Response(response_data)


class HistoryView(viewsets.ModelViewSet):
    permission_classes = [TokenHasPermission, DoctorCreatePermission,
                          DoctorBasePermission, DoctorVisitPermission]

    queryset = History.objects.order_by('-history_create_time')
    serializer_class = CreateHistorySerializer
    lookup_field = 'patient_id'
    model = History

    def valid_patient_info(self, patient_id):
        try:
            patient = PatientUser.objects.get(id=patient_id)
        except PatientUser.DoesNotExist:
            patient = None
        return patient

    def valid_diadetail_info(self, diagdetail_id):
        try:
            diadetail = DiaDetail.objects.get(id=diagdetail_id)
        except DiaDetail.DoesNotExist:
            diadetail = None
        return diadetail

    def valid_prep_info(self, prep_id):
        try:
            prep = Prescription.objects.get(id=prep_id)
        except Prescription.DoesNotExist:
            prep = None
        return prep

    def valiad_info(self, dia, patient, doctor):
        if not any([dia, patient, doctor]):
            return False

        if not all([dia.patient_id == patient.id, dia.doctor_id == doctor.id]):
            return False

        return True

    def prep_create(self, request, patient_id, prep_id, *args, **kwargs):
        """
        - 医生创建病历(开方抓药)
        """
        doctor = DoctorUser.objects.get(owner=request.auth.user)
        patient = self.valid_patient_info(patient_id)
        prep = self.valid_prep_info(prep_id)

        if not prep:
            return Http404

        data = {
            'patient_id': patient.id,
            'doctor_id': doctor.id,
            'history_create_time': timezone.localtime(timezone.now())
        }
        data.update(**request.data)
        s = HistorySerializer(data=data)
        s.is_valid(raise_exception=True)
        his = s.save()

        prep.history_id = his.id
        prep.save()
        return Response(s.data)

    def create(self, request, patient_id, diagdetail_id, *args, **kwargs):
        """
        - 医生为患者创建病历
        """
        doctor = DoctorUser.objects.get(owner=request.auth.user)

        # 患者基本信息
        patient = self.valid_patient_info(patient_id)
        diadetail = self.valid_diadetail_info(diagdetail_id)
        if not self.valiad_info(diadetail, patient, doctor):
            return Response(
                {'detail': '无法匹配到对应的复诊信息'},
                status=status.HTTP_404_NOT_FOUND
            )

        data = {
            'patient_id': patient.id,
            'doctor_id': doctor.id,
            'history_create_time': timezone.localtime(timezone.now())
        }
        data.update(**request.data)
        s = HistorySerializer(data=data)
        s.is_valid(raise_exception=True)
        s.save()

        diadetail.order_question.business_state = '会诊完成'
        diadetail.order_question.save()

        # 同时更新当前医生/患者的复诊次数
        doctor.server_times = doctor.server_times + 1
        doctor.save()
        patient.referral_count = patient.referral_count + 1
        patient.save()

        return Response(s.data)

    @swagger_auto_schema(responses={'200': SwaggerHistorySerializer})
    def user_history(self, request, patient_id, *args, **kwargs):
        """
        - 患者的病历（返回数据包含基本信息、病历列表）
        """
        # 患者基本信息
        patient = self.valid_patient_info(patient_id)
        serializer_patient = PatientBaseInfoSerializer(instance=patient)

        # 所有病例
        all_history = self.model.objects.filter(patient_id=patient_id)
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
    permission_classes = [TokenHasPermission, DoctorCreatePermission,
                          DoctorBasePermission, DoctorVisitPermission]
    queryset = Recipe.objects.order_by('-pk')
    # serializer_class = RecipeSerializer
    lookup_field = 'history_id'
    model = Recipe

    def get_serializer_class(self):
        if self.action == 'create':
            return RecipeSerializer
        return RecipeRetrieveSerializer
        # return RecipeSerializer

    def get_object(self):
        id = self.kwargs.get(self.lookup_field)
        try:
            history = History.objects.get(pk=id)
        except History.DoesNotExist:
            raise Http404
        else:
            recipe = history.recipe

            if not recipe:
                raise Http404

        self.check_object_permissions(self.request, recipe)
        return recipe

    def retrieve(self, request, *args, **kwargs):
        response_data = dict()
        instance = self.get_object()
        serializer = self.get_serializer(instance)

        dia = DiaMedicineSerializer(DiaMedicine.objects.filter(owner=instance), many=True)
        response_data['medicine_list'] = dia.data
        response_data.update(serializer.data)
        return Response(response_data)

    @swagger_auto_schema(responses={'200': ResponseSuccessSerializer})
    def create(self, request, history_id, *args, **kwargs):
        """
        - 医生为患者根据病历ID进行创建处方
        """
        data = request.data
        try:
            history = History.objects.get(pk=history_id)
        except History.DoesNotExist:
            return Response({'detail': '病历未创建'}, status=status.HTTP_404_NOT_FOUND)
        else:
            try:
                patient = PatientUser.objects.get(pk=history.patient_id)
            except PatientUser.DoesNotExist:
                return Response({'detail': '患者不存在'}, status=status.HTTP_404_NOT_FOUND)
            # 生成药品订单
            order_info = {
                'order_num': 'prep_' + create_order_number(MedicineOrder, 'prep_'),
                'pay_state': '未支付',   # 订单状态
                'medicine_order_form': '处方',
                'patient_id': history.patient_id,
                'doctor_id': history.doctor_id,
                'order_price': data.get('total_price'),
                # 仅保存两位小数
                'discount_price': format(float(data.get('total_price')) * float(patient.level_discount) * 0.1, '.2f')
            }

            with transaction.atomic():
                point = transaction.savepoint()
                try:
                    m_order = MedicineOrderSerializer(data=order_info)
                    m_valid = m_order.is_valid()
                    if not m_valid:
                        transaction.savepoint_rollback(point)
                        return JsonResponse(m_order.errors, status=400)

                    order = m_order.save()
                    recipe_serializer = RecipeSerializer(data=data)
                    r_valid = recipe_serializer.is_valid()
                    if not r_valid:
                        transaction.savepoint_rollback(point)
                        return JsonResponse(recipe_serializer.errors, status=400)

                    recipe = recipe_serializer.save()

                    # 生成药品订单
                    recipe.order = order
                    recipe.save()

                    history.recipe = recipe
                    history.save()
                except Exception as e:
                    transaction.savepoint_rollback(point)
                    raise e
                transaction.savepoint_commit(point)

        return Response({'detail': '处方提交成功'})
