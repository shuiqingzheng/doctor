import random


def create_random_number():
    """
    生成6为随机验证码
    """
    const = '0123456789'
    return_list = random.sample(const, k=6)
    code = ''.join(return_list)
    return code
