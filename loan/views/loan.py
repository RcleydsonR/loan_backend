from loan.models import Loan
from loan.serializers import LoanSerializer
from rest_framework.authentication import TokenAuthentication

from rest_framework.generics import ListCreateAPIView, RetrieveUpdateAPIView
from rest_framework import permissions


class LoanAPIView(ListCreateAPIView):
    serializer_class = LoanSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Loan.objects.filter(user=self.request.user.id)


class LoanRetrieveUpdateAPIView(RetrieveUpdateAPIView):
    serializer_class = LoanSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_anonymous:
            return Loan.objects.none()
        return Loan.objects.filter(user=self.request.user.id)
