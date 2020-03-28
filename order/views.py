from django.http import Http404, JsonResponse
from rest_framework import views, generics, status, viewsets
from rest_framework.response import Response
from utils.wxopenid import get_openid
from order.serializers import (
    PaySerializer, OrderQuestionOrderSerializer,
)
from order.models import QuestionOrder
from celery_tasks.tasks import wx_pay
from myuser.models import PatientUser
from diagnosis.serializers import (
    DiaDetailSerializer, VideoDetailSerializer, ImageDetailSerializer
)
from oauth2_provider.contrib.rest_framework import TokenHasScope
import xmltodict


class QuestionOrderView(viewsets.ModelViewSet):
    permission_classes = [TokenHasScope, ]
    required_scopes = ['patient']
    serializer_class = OrderQuestionOrderSerializer

    def get_queryset(self):
        auth = self.request.auth

        if hasattr(auth, 'user'):
            user = auth.user
            try:
                patient = PatientUser.objects.get(owner=user)
            except PatientUser.DoesNotExist:
                raise Http404
            return QuestionOrder.objects.filter(patient_id=patient.id).order_by('-create_time')
        else:
            return QuestionOrder.objects.order_by('-create_time')

    def retrieve(self, request, *args, **kwargs):
        """
        - 获取订单详情
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

    def post(self, request, *args, **kwargs):
        s = self.get_serializer(data=request.data)
        s.is_valid(raise_exception=True)
        order_id = s.validated_data['order_id']
        openid = s.validated_data['openid']
        question_order = QuestionOrder.objects.get(id=order_id)
        price_fee = int(question_order.order_price * 100)
        # 异步向微信发起统一支付请求
        pay = wx_pay.delay('{}'.format(question_order.order_num), price_fee, openid)
        return_msg = pay.get()
        if not return_msg:
            return Response({'detail': '未知错误, 支付失败'}, status=status.HTTP_400_BAD_REQUEST)

        if return_msg.get('detail'):
            return Response(return_msg, status=status.HTTP_400_BAD_REQUEST)

        return Response(return_msg)


def callback(request, *args, **kwargs):
    """
    微信统一下单的回调接口
    """
    msg = request.body.decode('utf-8')
    xmlmsg = xmltodict.parse(msg)

    return_code = xmlmsg['xml']['return_code']

    if return_code == 'FAIL':
        return JsonResponse({'detail': '微信官方返回错误'})

    elif return_code == 'SUCCESS':
        out_trade_no = xmlmsg['xml']['out_trade_no']  # 订单号
        q_order = QuestionOrder.objects.get(order_num=out_trade_no)
        if xmlmsg['xml']['nonce_str'] != q_order.nonce_str:
            return JsonResponse({'detail': '订单号不匹配'})

        q_order.pay_state = '已支付'
        q_order.business_state = '待会诊'
        q_order.save()
        return JsonResponse({'detail': '修改成功'})
