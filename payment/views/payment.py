from payment.models import Payment
from payment.serializers import PaymentSerializer

from loan.models import Loan

from rest_framework.authentication import TokenAuthentication

from rest_framework.generics import ListCreateAPIView, RetrieveUpdateAPIView
from rest_framework import permissions


class PaymentAPIView(ListCreateAPIView):
    serializer_class = PaymentSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Payment.objects.filter(loan__in=Loan.objects.filter(user=self.request.user))


class PaymentRetrieveUpdateAPIView(RetrieveUpdateAPIView):
    serializer_class = PaymentSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Payment.objects.filter(loan__in=Loan.objects.filter(user=self.request.user))
