
import requests
import hashlib
import xmltodict
import time
import random
import string
from django.conf import settings


requests.DEFAULT_RETRIES = 5
requests.adapters.DEFAULT_RETRIES = 5
# s = requests.session()
s = requests.Session()
s.keep_alive = False
APPID = settings.APPID
MCHID = settings.MCHID
AppSecret = settings.APPSECRET
KEY = settings.KEY
NOTIFY_URL = settings.NOTIFY_URL


# 生成nonce_str
def generate_randomStr():
    num = ''.join(random.sample(string.ascii_letters + string.digits, 32))
    return num


# 生成签名
def generate_sign(param):
    stringA = ''

    ks = sorted(param.keys())
    # 参数排序
    for k in ks:
        stringA += k + "=" + str(param[k]) + "&"
    # 拼接商户KEY
    stringSignTemp = stringA + "key=" + KEY

    # md5加密
    hash_md5 = hashlib.md5(stringSignTemp.encode('utf-8'))
    sign = hash_md5.hexdigest().upper()

    return sign


# 发送xml请求
def send_xml_request(url, param):
    # dict 2 xml
    param = {'root': param}
    xml = xmltodict.unparse(param)
    response = s.post(url, data=xml, headers={'Content-Type': 'application/xml'})
    # xml 2 dict
    response.encoding = 'utf-8'
    msg = response.text
    xmlmsg = xmltodict.parse(msg)
    return xmlmsg


# 统一下单
def generate_bill(pay_order_num, fee, openid):
    """
    pay_order_num:支付单号，只能使用一次，不可重复支付
    fee:总价格(单位分)
    openid:对应的openid
    """
    url = "https://api.mch.weixin.qq.com/pay/unifiedorder"
    nonce_str = generate_randomStr()        # 订单中加nonce_str字段记录（回调判断使用）

    param = {
        "appid": APPID,
        "mch_id": MCHID,
        "nonce_str": nonce_str,
        "body": 'test1',
        "out_trade_no": pay_order_num,
        "total_fee": fee,
        "spbill_create_ip": '127.0.0.1',
        "notify_url": NOTIFY_URL,
        "trade_type": 'JSAPI',
        "openid": openid,
    }
    sign = generate_sign(param)
    param["sign"] = sign
    xmlmsg = send_xml_request(url, param)

    if xmlmsg['xml']['return_code'] == 'SUCCESS':
        if xmlmsg['xml']['result_code'] == 'SUCCESS':
            prepay_id = xmlmsg['xml']['prepay_id']

            timeStamp = str(int(time.time()))
            # 根据文档，六个参数，否则app提示签名验证失败，https://pay.weixin.qq.com/wiki/doc/api/app/app.php?chapter=9_12
            data = {
                "appid": APPID,
                "partnerid": MCHID,
                "prepayid": prepay_id,
                "package": "Sign=WXPay",
                "noncestr": nonce_str,
                "timestamp": timeStamp,
            }
            paySign = generate_sign(data)
            data["paySign"] = paySign
            # 传给前端的签名后的参数
            return data
        else:
            err_msg = xmlmsg['xml']['err_code_des']
            err_code = xmlmsg['xml']['err_code']
            return {'detail': '{}: {}'.format(err_code, err_msg)}


# generate_bill(generate_current_day(), 1, 'oPP9p5FO1SZeBA7Zah9xdC0nDAig')