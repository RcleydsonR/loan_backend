
from payment.models import Payment

from rest_framework import serializers


class PaymentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Payment
        fields = (
            'idPayment', 'value', 'paymentDate', 'loan'
        )
        read_only_fields = ['idPayment',]

    def create(self, validated_data):
        loan = validated_data['loan']

        if self.context['request'].user != loan.user:
            raise serializers.ValidationError('Usuário não é dono do empréstimo referenciado')
        if validated_data['paymentDate'] < loan.solicitationDate:
            raise serializers.ValidationError('Data de pagamento do empréstimo mais antiga do que a do empréstimo')

        return super().create(validated_data)

    def update(self, instance, validated_data):
        if validated_data['paymentDate'] < instance.loan.solicitationDate:
            raise serializers.ValidationError('Data de pagamento do empréstimo mais antiga do que a do empréstimo')

        return super().update(instance, validated_data)
