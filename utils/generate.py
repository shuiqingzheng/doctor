from django.db.models import Max
# from django.conf import settings

from datetime import datetime


def create_today_number():
    today = datetime.today()
    current_year = today.year
    current_month = today.month
    current_day = today.day
    serial = '%s%02d%02d%04d' % (current_year, current_month, current_day, 1)
    return serial


def generate_current_day():
    today = datetime.today()
    current_year = today.year
    current_month = today.month
    current_day = today.day
    current = '%s%02d%02d' % (current_year, current_month, current_day)
    return current


def create_order_number(model_name, tps):
    """
    : 创建唯一的订单号
    : param model_name:Model名称
    : param tps:前缀(保证数据库中的订单唯一)
    => 例子: 'prep_202003300001' & 'orde_202003300005'
    """
    # 创建订单编号
    s_current_date = generate_current_day()
    # 查询当天的订单编号最大值
    max_questionnaire_id = model_name.objects.filter(order_num__startswith=tps+s_current_date).aggregate(Max('order_num'))

    max_id = max_questionnaire_id.get('order_num__max', None)

    if max_id:
        serial = '{}'.format(int(max_id[5:]) + 1)
    else:
        serial = create_today_number()

    return serial
