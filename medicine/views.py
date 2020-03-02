from rest_framework import viewsets
from medicine.models import Medicine
from medicine.serializers import Medicineserializer
from oauth2_provider.contrib.rest_framework import TokenHasScope


class MedicineBaseView(viewsets.ModelViewSet):
    permission_classes = [TokenHasScope, ]
    # required_scopes = ['doctor']
    serializer_class = Medicineserializer
    model = Medicine


class MedicineDoctorView(MedicineBaseView):
    required_scopes = ['doctor']
    queryset = Medicine.objects.all()


class MedicinePatientView(MedicineBaseView):
    required_scopes = ['patient']
    queryset = Medicine.objects.filter(product_state=True)
