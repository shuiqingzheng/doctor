from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status
from rest_framework.filters import SearchFilter
from rest_framework.response import Response
# from rest_framework.permissions import AllowAny
from medicine.models import Medicine, MedicineType, MedicineStock
from medicine.serializers import (
    Medicineserializer, MedicineTypeSerializer, MedicineStockSerializer
)
from medicine.permissions import TokenHasPermission
from oauth2_provider.contrib.rest_framework import TokenHasScope


class MedicineStockView(viewsets.ModelViewSet):
    permission_classes = [TokenHasScope]
    required_scopes = ['doctor']
    queryset = MedicineStock.objects.all()
    serializer_class = MedicineStockSerializer


class MedicineView(viewsets.ModelViewSet):
    permission_classes = [TokenHasPermission]
    # required_any_scopes = ['doctor', 'patient']
    serializer_class = Medicineserializer
    filter_backends = [SearchFilter, DjangoFilterBackend]
    search_fields = ['type_one', 'type_two', 'type_three', 'good_for',
                     'officical_name', 'price', 'product_source', ]
    filterset_fields = ('type_one', 'type_two', 'type_three')

    def get_queryset(self):
        auth = self.request.auth
        if hasattr(auth, 'user'):
            user = auth.user
            # 患者：返回已上架商品
            if hasattr(user, 'patient'):
                return Medicine.objects.filter(product_state=True)

        return Medicine.objects.order_by('-pk')


class MedicineTypeView(viewsets.ModelViewSet):
    """
    - 分类级别
    """
    permission_classes = [TokenHasPermission]
    serializer_class = MedicineTypeSerializer
    queryset = MedicineType.objects.all()
    next_type_name = 'next_type'
    allowd_level = ['one', 'two', 'three', 'all']

    def medicineType(self, request, type_level, *args, **kwargs):
        """
        - 返回药品类型列表
        """
        if type_level not in self.allowd_level:
            return Response({'detail': '查询类别请选择{}、{}、{}或{}'.format(*self.allowd_level)}, status=status.HTTP_404_NOT_FOUND)

        response_data = None
        one_level = self.queryset.filter(father_id=None)
        one_level_id_list = [obj.id for obj in one_level]
        two_level = self.queryset.filter(father_id__in=one_level_id_list)
        two_level_id_list = [obj.id for obj in two_level]
        three_level = self.queryset.filter(father_id__in=two_level_id_list)

        if type_level == self.allowd_level[0]:
            one_serializer = self.get_serializer(one_level, many=True)
            response_data = one_serializer.data
        elif type_level == self.allowd_level[1]:
            two_serializer = self.get_serializer(two_level, many=True)
            response_data = two_serializer.data
        elif type_level == self.allowd_level[2]:
            three_serializer = self.get_serializer(three_level, many=True)
            response_data = three_serializer.data
        else:
            response_data = list()
            for one in one_level:
                one_serializer = self.get_serializer(one)
                one_data = one_serializer.data
                one_next_type = list()

                for two in two_level.filter(father_id=one.id):
                    two_serializer = self.get_serializer(two)
                    two_data = two_serializer.data

                    three_objs = three_level.filter(father_id=two.id)
                    three_serializers = self.get_serializer(three_objs, many=True)

                    two_data.update({
                        '{}'.format(self.next_type_name): three_serializers.data
                    })
                    one_next_type.append(two_data)

                one_data.update({
                    '{}'.format(self.next_type_name): one_next_type
                })
                response_data.append(one_data)

        return Response(response_data)
