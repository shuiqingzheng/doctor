from celery_tasks.celery import app
# aliyun sms API
from utils.sms import aliyun_send_sms_common_api

@app.task(name='register_task')
def register_task(phone, sms_code):
    action = "SendSms"
    query_param_dict = {
        "PhoneNumbers": "{}".format(phone),
        'RegionId': 'cn-hangzhou',
        'SignName': '汉典云健康',
        'TemplateCode': 'SMS_138060419',
        'TemplateParam': '{"code":"%s"}' % sms_code
    }
    # 线上
    # response = aliyun_send_sms_common_api(action, query_param_dict)
    # 开发
    response = '{"Message":"OK","RequestId":"4B1A507E-A5D9-435C-A3A2-AAAA83832FDD","BizId":"381423182509765473^0","Code":"OK"}'
    return response
