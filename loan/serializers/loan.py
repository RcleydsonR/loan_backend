
from loan.models import Loan

from payment.models import Payment
from payment.serializers import PaymentSerializer

from decimal import Decimal
from datetime import timedelta
from django.utils import timezone

from rest_framework import serializers


class LoanSerializer(serializers.ModelSerializer):

    class Meta:
        model = Loan
        fields = (
            'idLoan', 'nominalValue', 'interestRate',
            'interestType', 'ipAddress', 'solicitationDate',
            'bank', 'client', 'user'
        )
        read_only_fields = ('idLoan', 'ipAddress', 'user')

    def create(self, validated_data):
        validated_data['ipAddress'] = self.context.get('request').META.get("REMOTE_ADDR")
        validated_data['user'] = self.context.get('request').user
        return Loan.objects.create(**validated_data)


class LoanDetailSerializer(LoanSerializer):
    payments = serializers.SerializerMethodField()
    debitBalance = serializers.SerializerMethodField()

    class Meta:
        model = Loan
        fields = LoanSerializer.Meta.fields + ('payments', 'debitBalance',)
        read_only_fields = fields

    def get_payments(self, loan):
        return PaymentSerializer(loan.payments, many=True).data

    def get_debitBalance(self, loan):
        month_charge = loan.solicitationDate + timedelta(days=30)  # Consider default month with 30 days
        debitBalance = loan.nominalValue

        while (month_charge < timezone.now()):
            month_payments = Payment.objects.filter(
                paymentDate__date__range=(loan.solicitationDate, month_charge), loan=loan).values()
            for payment in month_payments:
                debitBalance -= payment['value']

            debitBalance += loan.nominalValue * loan.interestRate
            last_month_charge = month_charge
            month_charge += timedelta(days=30)

        last_month_payments = Payment.objects.filter(
            paymentDate__date__range=(last_month_charge, timezone.now()), loan=loan).values()

        for payment in last_month_payments:
            debitBalance -= payment['value']

        return Decimal(str(debitBalance))
