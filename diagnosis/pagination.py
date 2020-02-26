from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from myuser.models import PatientUser
from myuser.serializers import PatientBaseInfoSerializer

from collections import OrderedDict


class UserHistoryCustomPagination(PageNumberPagination):
    """
    - 患者获取病例列表和基础信息
    """
    def get_paginated_response(self, data):

        return Response(OrderedDict([
            # ('base_info', {}),s
            ('count', self.page.paginator.count),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('results', data)
        ]))
