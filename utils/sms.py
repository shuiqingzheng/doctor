from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.request import CommonRequest


def aliyun_send_sms_common_api(action, query_param_dict):
    """
    阿里云短信服务公用接口
    :param action: 指明短信相关的哪些接口
    :param query_param_dict: 短信相关接口的参数（字典形式）
    :return:
    """
    # client = AcsClient('<accessKeyId>', '<accessSecret>', 'default')
    client = AcsClient('LTAI9V9D3ixqyDwB', 'Wg8NPITDXdyKmDAcd8aSOSBsE0OoxB', "cn-hangzhou")
    request = CommonRequest()
    request.set_accept_format('json')
    request.set_domain('dysmsapi.aliyuncs.com')
    request.set_method('POST')
    request.set_protocol_type('https')
    request.set_version('2017-05-25')
    request.set_action_name(action)

    for k, v in query_param_dict.items():
        if type(v) == "enum":
            return
        request.add_query_param(k, v)
    response = client.do_action_with_exception(request)
    response = str(response, encoding='utf-8')
    return response


# if __name__ == "__main__":
#     action = "SendSms"
#     query_param_dict = {
#         "PhoneNumbers": "17630975001",
#         'RegionId': 'cn-hangzhou',
#         'SignName': '汉典云健康',
#         'TemplateCode': 'SMS_138060419',
#         'TemplateParam': '{code:ASDWDS}'
#     }    # 接口中需要的参数，注意字典中的key要和接口文档中的一样，不能忽略大小写
#     response = aliyun_send_sms_common_api(action, query_param_dict)
#     print(response)
