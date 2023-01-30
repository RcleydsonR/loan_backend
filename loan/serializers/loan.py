
from loan.models import Loan

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
