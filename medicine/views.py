from rest_framework import viewsets, status
from rest_framework.filters import SearchFilter
from rest_framework.response import Response
# from rest_framework.permissions import AllowAny
from medicine.models import Medicine, MedicineType
from medicine.serializers import (
    Medicineserializer, MedicineTypeSerializer
)
from medicine.permissions import TokenHasPermission
# from oauth2_provider.contrib.rest_framework import TokenHasScope


class MedicineView(viewsets.ModelViewSet):
    permission_classes = [TokenHasPermission]
    # required_any_scopes = ['doctor', 'patient']
    serializer_class = Medicineserializer
    filter_backends = [SearchFilter]
    search_fields = ['type_one', 'type_two', 'type_three', 'good_for',
                     'officical_name', 'price', 'product_source', ]

    def get_queryset(self):
        auth = self.request.auth
        # 患者：返回已上架商品
        if hasattr(auth.user, 'patient'):
            return Medicine.objects.filter(product_state=True)

        return Medicine.objects.order_by('-pk')


class MedicineTypeView(viewsets.ModelViewSet):
    """
    - 分类级别
    """
    permission_classes = [TokenHasPermission]
    serializer_class = MedicineTypeSerializer
    queryset = MedicineType.objects.all()

    def medicineType(self, request, type_level, *args, **kwargs):
        """
        - 返回药品类型列表
        """
        allowd_level = ['one', 'two', 'three']

        if type_level not in allowd_level:
            return Response({'detail': '查询类别请选择{}、{}或者{}'.format(*allowd_level)}, status=status.HTTP_404_NOT_FOUND)

        response_data = None
        one_level = self.queryset.filter(father_id=None)
        one_level_id_list = [obj.id for obj in one_level]
        two_level = self.queryset.filter(father_id__in=one_level_id_list)
        two_level_id_list = [obj.id for obj in two_level]
        three_level = self.queryset.filter(father_id__in=two_level_id_list)

        if type_level == allowd_level[0]:
            one_serializer = self.get_serializer(one_level, many=True)
            response_data = one_serializer.data
        elif type_level == allowd_level[1]:
            two_serializer = self.get_serializer(two_level, many=True)
            response_data = two_serializer.data
        else:
            three_serializer = self.get_serializer(three_level, many=True)
            response_data = three_serializer.data

        return Response(response_data)
