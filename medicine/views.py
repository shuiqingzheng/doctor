from rest_framework import viewsets
# from rest_framework.permissions import AllowAny
from medicine.models import Medicine
from medicine.serializers import Medicineserializer
from medicine.permissions import TokenHasPermission
# from oauth2_provider.contrib.rest_framework import TokenHasScope


# class MedicineBaseView(viewsets.ModelViewSet):
#     permission_classes = [TokenHasScope, ]
#     # required_scopes = ['doctor']
#     serializer_class = Medicineserializer
#     model = Medicine


# class MedicineDoctorView(MedicineBaseView):
#     required_scopes = ['doctor']
#     queryset = Medicine.objects.all()


# class MedicinePatientView(MedicineBaseView):
#     required_scopes = ['patient']
#     queryset = Medicine.objects.filter(product_state=True)


class MedicineView(viewsets.ModelViewSet):
    permission_classes = [TokenHasPermission]
    required_any_scopes = ['doctor', 'patient']
    serializer_class = Medicineserializer

    def get_queryset(self):
        auth = self.request.auth
        # 患者：返回已上架商品
        if hasattr(auth.user, 'patient'):
            return Medicine.objects.filter(product_state=True)

        return Medicine.objects.order_by('-pk')
