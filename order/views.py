from django.http import Http404, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import views, generics, status, viewsets
from rest_framework.response import Response
from utils.wxopenid import get_openid
from order.serializers import (
    PaySerializer, OrderQuestionOrderSerializer, OrderMedicineOrderSerializer
)
from order.models import QuestionOrder, MedicineOrder
from celery_tasks.tasks import wx_pay
from myuser.models import PatientUser
from diagnosis.serializers import (
    DiaDetailSerializer, VideoDetailSerializer, ImageDetailSerializer,
    RecipeRetrieveSerializer, DiaMedicineSerializer
)
from oauth2_provider.contrib.rest_framework import TokenHasScope
import xmltodict

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET


class MedicineOrderView(viewsets.ModelViewSet):
    permission_classes = [TokenHasScope, ]
    required_scopes = ['patient']
    serializer_class = OrderMedicineOrderSerializer
    model_name = MedicineOrder

    def get_queryset(self):
        auth = self.request.auth

        if hasattr(auth, 'user'):
            user = auth.user
            try:
                patient = PatientUser.objects.get(owner=user)
            except PatientUser.DoesNotExist:
                raise Http404
            return self.model_name.objects.filter(patient_id=patient.id).order_by('-create_time')
        else:
            return self.model_name.objects.order_by('-create_time')

    def retrieve(self, request, *args, **kwargs):
        """
        - 获取订单详情(处方详情)
        """
        response_data = dict()
        order = self.get_object()
        serializer_order = self.get_serializer(order)
        response_data.update(serializer_order.data)

        if hasattr(order, 'recipe'):
            recipe = order.recipe
            medicine_queryset = recipe.diamedicine.all()
            serializer_medicine = DiaMedicineSerializer(medicine_queryset, many=True)
            response_data['medicine_info'] = serializer_medicine.data

            serializer_recipe = RecipeRetrieveSerializer(recipe)
            response_data['recipe_info'] = serializer_recipe.data

        return Response(response_data)


class QuestionOrderView(viewsets.ModelViewSet):
    permission_classes = [TokenHasScope, ]
    required_scopes = ['patient']
    serializer_class = OrderQuestionOrderSerializer
    model_name = QuestionOrder

    def get_queryset(self):
        auth = self.request.auth

        if hasattr(auth, 'user'):
            user = auth.user
            try:
                patient = PatientUser.objects.get(owner=user)
            except PatientUser.DoesNotExist:
                raise Http404
            return self.model_name.objects.filter(patient_id=patient.id).order_by('-create_time')
        else:
            return self.model_name.objects.order_by('-create_time')

    def retrieve(self, request, *args, **kwargs):
        """
        - 获取订单详情(复诊详情)
        """
        response_data = dict()
        order = self.get_object()
        order_type = {
            'imagedetail': ImageDetailSerializer,
            'videodetail': VideoDetailSerializer,
            'diadetail': DiaDetailSerializer
        }
        for key, model_serializer in order_type.items():
            if hasattr(order, key):
                detail_obj = getattr(order, key)
                s_model = model_serializer(detail_obj)
                response_data['detail_info'] = s_model.data

        s_order = self.get_serializer(order)
        response_data['order_info'] = s_order.data
        return Response(response_data)


class OpenIDView(views.APIView):
    permission_classes = [TokenHasScope, ]
    required_scopes = ['patient']

    def get(self, request, jscode, *args, **kwargs):
        """
        - 获取openid
        """
        response_msg = get_openid(jscode)
        if not response_msg.get('openid', None):
            return Response({'detail': '微信官方返回的错误码errcode:{}'.format(response_msg.get('errcode'))}, status=status.HTTP_400_BAD_REQUEST)
        openid = response_msg['openid']
        session_key = response_msg['session_key']
        return Response({'openid': openid, 'session_key': session_key})


class PayView(generics.GenericAPIView):
    serializer_class = PaySerializer
    permission_classes = [TokenHasScope, ]
    required_scopes = ['patient']

    def validate_order(self, order, start_str):
        order_num = order.order_num
        if not order_num.startswith(start_str):
            return False

        return True

    def post(self, request, *args, **kwargs):
        s = self.get_serializer(data=request.data)
        s.is_valid(raise_exception=True)
        order_id = s.validated_data['order_id']
        openid = s.validated_data['openid']
        order_type = s.validated_data['order_type']
        if order_type == 'question':
            order = QuestionOrder.objects.get(id=order_id)
            valid = self.validate_order(order, 'orde')
        else:
            order = MedicineOrder.objects.get(id=order_id)
            valid = self.validate_order(order, 'prep')

        if not valid:
            return Response({'detail': '订单号存在问题, 请查看'}, status=status.HTTP_400_BAD_REQUEST)

        price_fee = int(order.order_price * 100)
        # 异步向微信发起统一支付请求
        pay = wx_pay.delay('{}'.format(order.order_num), price_fee, openid, order_type)
        return_msg = pay.get()
        if not return_msg:
            return Response({'detail': '未知错误, 支付失败'}, status=status.HTTP_400_BAD_REQUEST)

        if return_msg.get('detail'):
            return Response(return_msg, status=status.HTTP_400_BAD_REQUEST)

        return Response(return_msg)


@csrf_exempt
def callback(request, *args, **kwargs):
    """
    微信统一下单的回调接口
    """
    msg = request.body
    tree = ET.ElementTree(msg)
    root = tree.getroot()
    xmlmsg = xmltodict.parse(root.decode('utf-8'))
    xml_info = xmlmsg.get('xml')
    if not xml_info:
        xml_info = xmlmsg.get('root')

    return_code = xml_info['return_code']

    if return_code == 'FAIL':
        return JsonResponse({'detail': '微信官方返回错误'})
    elif return_code == 'SUCCESS':
        out_trade_no = xml_info['out_trade_no']  # 订单号
        # 订单号分类
        try:
            if str(out_trade_no).startswith('orde'):
                order = QuestionOrder.objects.get(order_num=out_trade_no)
                order.business_state = '待会诊'
            else:
                order = MedicineOrder.objects.get(order_num=out_trade_no)
        except Exception:
            return JsonResponse({'detail': '订单不存在'})

        if xml_info['nonce_str'] != order.nonce_str:
            return JsonResponse({'detail': '订单号不匹配'})

        order.pay_state = '已支付'
        order.save()
        return JsonResponse({'detail': '修改成功'})
