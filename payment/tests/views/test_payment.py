from core.tests.recipes import user as user_recipe

from decimal import Decimal
from datetime import timedelta

from django.test import TestCase
from django.utils import timezone
from core.tests.mixin import APITestMixin
from rest_framework.reverse import reverse_lazy

from payment.models import Payment
from payment.tests.recipes import payment as payment_recipe

from loan.tests.recipes import loan as loan_recipe

from parameterized import parameterized

NOT_FOUND_MESSAGE = 'Não encontrado.'
DATE_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"


class PaymentAPIViewTest(APITestMixin, TestCase):
    url = reverse_lazy("payment-create-list")
    loan_create_date = '2023-01-29T10:20:00.1234Z'

    def setUp(self):
        self.loan = loan_recipe.make(
            user=self.user, solicitationDate=timezone.datetime.strptime(self.loan_create_date, DATE_FORMAT))

    def _payload(self):
        return {
            "value": "120",
            "paymentDate": timezone.datetime.now(),
            "loan": self.loan.idLoan
        }

    def test_create_payment(self):
        payload = self._payload()

        response = self.client.post(self.url, data=payload)
        self.assertEqual(response.status_code, 201, response.json())
        self.assertEqual(Payment.objects.count(), 1)

        payment = Payment.objects.first()
        self.assertEqual(payment.value, Decimal(payload["value"]))
        self.assertIsInstance(payment.paymentDate, timezone.datetime)
        self.assertEqual(payment.loan.idLoan, payload["loan"])

    @parameterized.expand([
        'value', 'paymentDate', 'loan'
    ])
    def test_fail_to_create_payment_required_field(self, field):
        payload = self._payload()
        del payload[field]

        response = self.client.post(self.url, data=payload)

        self.assertEqual(response.status_code, 400, response.json())
        self.assertIn('Este campo é obrigatório.', response.json()[field])

    def test_fail_to_create_payment_value_less_than_0_1(self):
        payload = self._payload()
        payload["value"] = "0.0"

        response = self.client.post(self.url, data=payload)

        self.assertEqual(response.status_code, 400, response.json())
        self.assertIn('Certifque-se de que este valor seja maior ou igual a 0.01.', response.json()["value"])

    def test_fail_to_create_payment_not_loan_owner(self):
        user = user_recipe.make()
        self.set_user_on_client(user)
        payload = self._payload()

        response = self.client.post(self.url, data=payload)

        self.assertEqual(response.status_code, 400, response.json())
        self.assertIn('Usuário não é dono do empréstimo referenciado', response.json())

    def test_fail_to_create_payment_loan_date_greater_than_payment_date(self):
        invalid_date = timezone.datetime.strptime(self.loan_create_date, DATE_FORMAT) - timedelta(days=1)
        payload = self._payload()
        payload['paymentDate'] = invalid_date

        response = self.client.post(self.url, data=payload)

        self.assertEqual(response.status_code, 400, response.json())
        self.assertIn('Data de pagamento do empréstimo mais antiga do que a do empréstimo', response.json())

    def test_list_payment_from_user_should_success(self):
        payment_recipe.make(loan=self.loan)
        payment_recipe.make(loan=self.loan)

        payment_recipe.make()
        payment_recipe.make()

        response = self.client.get(self.url, format="json")

        self.assertEqual(response.status_code, 200, response.json())
        self.assertEqual(2, len(response.json()))

    def test_list_payment_from_user_should_return_empty_data_for_user_without_created_payment(self):
        payment_recipe.make()

        response = self.client.get(self.url, format="json")

        self.assertEqual(response.status_code, 200, response.json())
        self.assertEqual(0, len(response.json()))

    def test_list_payment_from_unauthorized_user_should_fail(self):
        self.client.credentials()

        response = self.client.get(self.url, format="json")

        self.assertEqual(response.status_code, 401, response.json())
        self.assertIn('As credenciais de autenticação não foram fornecidas.', response.json()['detail'])


class PaymentRetrieveUpdateAPIViewTest(APITestMixin, TestCase):
    loan_create_date = '2023-01-29T10:20:00.1234Z'

    def setUp(self):
        self.loan = loan_recipe.make(
            user=self.user, solicitationDate=timezone.datetime.strptime(self.loan_create_date, DATE_FORMAT))
        self.payment = payment_recipe.make(loan=self.loan)
        self.url = self.get_url()

    def _payload(self):
        return {
            "value": "120",
            "paymentDate": timezone.datetime.now(),
            "loan": self.loan.idLoan
        }

    def get_url(self, idPayment=None):
        if idPayment is None:
            idPayment = self.payment.idPayment
        return reverse_lazy("payment-detail-update", kwargs={'pk': idPayment})

    def test_detail_loan_should_success(self):
        response = self.client.get(self.url, format="json")

        date_without_tz = timezone.datetime.strptime(response.json()["paymentDate"], DATE_FORMAT)
        self.assertEqual(response.status_code, 200, response.json())
        self.assertEqual(self.payment.value, Decimal(response.json()["value"]))
        self.assertEqual(self.payment.paymentDate.replace(tzinfo=None), date_without_tz)
        self.assertEqual(str(self.payment.loan.idLoan), response.json()["loan"])

    def test_detail_payment_should_404_fail(self):
        url = self.get_url('00000000-0000-4000-8000-000000000000')

        response = self.client.get(url, format="json")

        self.assertEqual(response.status_code, 404, response.json())
        self.assertIn(NOT_FOUND_MESSAGE, response.json()['detail'])

    def test_detail_payment_should_fail_when_payment_is_from_other_user(self):
        payment = payment_recipe.make()
        url = self.get_url(payment.idPayment)

        response = self.client.get(url, format="json")

        self.assertEqual(response.status_code, 404, response.json())
        self.assertIn(NOT_FOUND_MESSAGE, response.json()['detail'])

    def test_update_loan_with_success(self):
        payload = self._payload()

        response = self.client.patch(self.url, data=payload, format="json")

        self.assertEqual(response.status_code, 200, response.json())
        self.assertEqual(Payment.objects.count(), 1)

        self.payment.refresh_from_db()
        date_without_tz = timezone.datetime.strptime(response.json()["paymentDate"], DATE_FORMAT)
        self.assertEqual(response.status_code, 200, response.json())
        self.assertEqual(self.payment.value, Decimal(response.json()["value"]))
        self.assertEqual(self.payment.paymentDate.replace(tzinfo=None), date_without_tz)
        self.assertEqual(str(self.payment.loan.idLoan), response.json()["loan"])

    def test_update_payment_should_fail_404(self):
        url = self.get_url('00000000-0000-4000-8000-000000000000')
        payload = self._payload()

        response = self.client.patch(url, data=payload, format="json")

        self.assertEqual(response.status_code, 404, response.json())
        self.assertIn(NOT_FOUND_MESSAGE, response.json()['detail'])

    def test_update_payment_should_fail_when_payment_is_from_other_user(self):
        payload = self._payload()
        payment = payment_recipe.make()
        url = self.get_url(payment.idPayment)

        response = self.client.patch(url, data=payload, format="json")

        self.assertEqual(response.status_code, 404, response.json())
        self.assertIn(NOT_FOUND_MESSAGE, response.json()['detail'])

    def test_fail_to_update_payment_loan_date_greater_than_payment_date(self):
        invalid_date = timezone.datetime.strptime(self.loan_create_date, DATE_FORMAT) - timedelta(days=1)
        payload = self._payload()
        payload['paymentDate'] = invalid_date
        del payload['loan']

        response = self.client.patch(self.url, data=payload)

        self.assertEqual(response.status_code, 400, response.json())
        self.assertIn('Data de pagamento do empréstimo mais antiga do que a do empréstimo', response.json())
