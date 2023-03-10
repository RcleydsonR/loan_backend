
from core.consts.interestType import SIMPLE_INTEREST, COMPOUND_INTEREST
from core.tests.recipes import user as user_recipe

from decimal import Decimal
from datetime import timedelta

from django.test import TestCase
from django.utils import timezone
from core.tests.mixin import APITestMixin
from rest_framework.reverse import reverse_lazy

from loan.models import Loan
from loan.tests.recipes import loan as loan_recipe

from payment.tests.recipes import payment as payment_recipe

from parameterized import parameterized

NOT_FOUND_MESSAGE = 'Não encontrado.'
DATE_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"


class LoanAPIViewTest(APITestMixin, TestCase):
    url = reverse_lazy("loan-create-list")

    def _payload(self):
        return {
            "nominalValue": Decimal("120"),
            "interestRate": Decimal("0.45"),
            "interestType": SIMPLE_INTEREST,
            "solicitationDate": "2022-04-23T18:25:43.511Z",
            "bank": "mock_bank",
            "client": "mock_client"
        }

    def test_create_loan(self):
        payload = self._payload()

        response = self.client.post(self.url, data=payload)
        self.assertEqual(response.status_code, 201, response.json())
        self.assertEqual(Loan.objects.count(), 1)

        loan = Loan.objects.first()
        self.assertEqual(loan.nominalValue, payload["nominalValue"])
        self.assertEqual(loan.interestRate, payload["interestRate"])
        self.assertEqual(loan.interestType, payload["interestType"])
        self.assertIsInstance(loan.solicitationDate, timezone.datetime)
        self.assertEqual(loan.bank, payload["bank"])
        self.assertEqual(loan.client, payload["client"])

    @parameterized.expand([
        'nominalValue', 'interestRate', 'interestType',
        'solicitationDate', 'bank', 'client'
    ])
    def test_fail_to_create_loan_required_field(self, field):
        payload = self._payload()
        del payload[field]

        response = self.client.post(self.url, data=payload)

        self.assertEqual(response.status_code, 400, response.json())
        self.assertIn('Este campo é obrigatório.', response.json()[field])

    @parameterized.expand([
        ("nominalValue", "0.0", "0.01"),
        ("interestRate", "0.0", "0.0001"),
    ])
    def test_fail_to_create_loan_interest_rate_and_nominal_value_less_than_0_1(self, field, value, min_value):
        payload = self._payload()
        payload[field] = value

        response = self.client.post(self.url, data=payload)

        self.assertEqual(response.status_code, 400, response.json())
        self.assertIn(f'Certifque-se de que este valor seja maior ou igual a {min_value}.', response.json()[field])

    def test_fail_to_create_loan_interest_rate_greater_than_1(self):
        payload = self._payload()
        payload["interestRate"] = "1.1"

        response = self.client.post(self.url, data=payload)

        self.assertEqual(response.status_code, 400, response.json())
        self.assertIn('Certifique-se de que este valor seja inferior ou igual a 1.0000.', response.json()["interestRate"])

    def test_list_loan_from_user_should_success(self):
        loan_recipe.make(user=self.user)
        loan_recipe.make(user=self.user)

        response = self.client.get(self.url, format="json")

        self.assertEqual(response.status_code, 200, response.json())
        self.assertEqual(2, len(response.json()))

    def test_list_loan_from_user_should_return_empty_data_for_user_without_created_loan(self):
        loan_recipe.make()

        response = self.client.get(self.url, format="json")

        self.assertEqual(response.status_code, 200, response.json())
        self.assertEqual(0, len(response.json()))

    def test_list_loan_from_unauthorized_user_should_fail(self):
        self.client.credentials()

        response = self.client.get(self.url, format="json")

        self.assertEqual(response.status_code, 401, response.json())
        self.assertIn('As credenciais de autenticação não foram fornecidas.', response.json()['detail'])


class LoanRetrieveUpdateAPIViewTest(APITestMixin, TestCase):
    loan_create_date = '2022-12-12T10:20:00.1234Z'

    def setUp(self):
        self.loan = loan_recipe.make(
            user=self.user, solicitationDate=timezone.datetime.strptime(self.loan_create_date, DATE_FORMAT))
        self.url = self.get_url()

    def _payload(self):
        return {
            "nominalValue": Decimal("455.98"),
            "interestRate": Decimal("0.32"),
            "interestType": COMPOUND_INTEREST,
            "solicitationDate": "2022-12-23T19:00:00.113Z",
            "bank": "mock_bank",
            "client": "mock_client"
        }

    def get_url(self, idLoan=None):
        if idLoan is None:
            idLoan = self.loan.idLoan
        return reverse_lazy("loan-detail-update", kwargs={'pk': idLoan})

    def test_detail_loan_should_success(self):
        payment_recipe.make(loan=self.loan)
        payment_recipe.make()
        response = self.client.get(self.url, format="json")

        self.assertEqual(response.status_code, 200, response.json())
        self.assertEqual(self.loan.nominalValue, Decimal(response.json()["nominalValue"]))
        self.assertEqual(self.loan.interestRate, Decimal(response.json()["interestRate"]))
        self.assertEqual(self.loan.interestType, response.json()["interestType"])
        self.assertEqual(self.loan.bank, response.json()["bank"])
        self.assertEqual(self.loan.client, response.json()["client"])
        self.assertEqual(1, len(response.json()["payments"]))

    def test_detail_loan_should_return_correct_debit_balance_for_simple_interest_type(self):
        loan = loan_recipe.make(
            user=self.user, solicitationDate=(timezone.datetime.now() - timedelta(days=31)),
            nominalValue=Decimal("400"), interestRate=Decimal("0.06"),
            interestType=SIMPLE_INTEREST
        )
        payment = payment_recipe.make(loan=loan, value=Decimal("300"))

        url = self.get_url(idLoan=loan.idLoan)
        response = self.client.get(url, format="json")

        debitBalance = (loan.nominalValue + (loan.nominalValue * loan.interestRate)) - payment.value
        self.assertEqual(response.status_code, 200, response.json())
        self.assertEqual(loan.nominalValue, Decimal(response.json()["nominalValue"]))
        self.assertEqual(loan.interestRate, Decimal(response.json()["interestRate"]))
        self.assertEqual(loan.interestType, response.json()["interestType"])
        self.assertEqual(loan.bank, response.json()["bank"])
        self.assertEqual(loan.client, response.json()["client"])
        self.assertEqual(debitBalance, response.json()["debitBalance"])

    def test_detail_loan_should_404_fail(self):
        url = self.get_url('00000000-0000-4000-8000-000000000000')

        response = self.client.get(url, format="json")

        self.assertEqual(response.status_code, 404, response.json())
        self.assertIn(NOT_FOUND_MESSAGE, response.json()['detail'])

    def test_detail_loan_should_fail_when_loan_is_from_other_user(self):
        user = user_recipe.make()
        new_loan = loan_recipe.make(user=user)
        url = self.get_url(new_loan.idLoan)

        response = self.client.get(url, format="json")

        self.assertEqual(response.status_code, 404, response.json())
        self.assertIn(NOT_FOUND_MESSAGE, response.json()['detail'])

    def test_update_loan_with_success(self):
        payload = self._payload()

        response = self.client.patch(self.url, data=payload, format="json")

        self.assertEqual(response.status_code, 200, response.json())
        self.assertEqual(Loan.objects.count(), 1)

        self.loan.refresh_from_db()
        self.assertEqual(self.loan.nominalValue, payload["nominalValue"])
        self.assertEqual(self.loan.interestRate, payload["interestRate"])
        self.assertEqual(self.loan.interestType, payload["interestType"])
        self.assertEqual(self.loan.bank, payload["bank"])
        self.assertEqual(self.loan.client, payload["client"])

    @parameterized.expand([
        ("nominalValue", "0.0", "0.01"),
        ("interestRate", "0.0", "0.0001"),
    ])
    def test_update_loan_interest_rate_and_nominal_value_fail_less_than_0_1(self, field, value, min_value):
        payload = self._payload()
        payload[field] = value

        response = self.client.patch(self.url, data=payload, format="json")

        self.assertEqual(response.status_code, 400, response.json())
        self.assertIn(f'Certifque-se de que este valor seja maior ou igual a {min_value}.', response.json()[field])

    def test_update_loan_interest_rate_fail_greater_than_1(self):
        payload = self._payload()
        payload["interestRate"] = "1.1"

        response = self.client.patch(self.url, data=payload, format="json")

        self.assertEqual(response.status_code, 400, response.json())
        self.assertIn('Certifique-se de que este valor seja inferior ou igual a 1.0000.', response.json()["interestRate"])

    def test_update_loan_should_fail_404(self):
        url = self.get_url('00000000-0000-4000-8000-000000000000')
        payload = self._payload()

        response = self.client.patch(url, data=payload, format="json")

        self.assertEqual(response.status_code, 404, response.json())
        self.assertIn(NOT_FOUND_MESSAGE, response.json()['detail'])

    def test_update_loan_should_fail_when_loan_is_from_other_user(self):
        payload = self._payload()
        user = user_recipe.make()
        new_loan = loan_recipe.make(user=user)
        url = self.get_url(new_loan.idLoan)

        response = self.client.patch(url, data=payload, format="json")

        self.assertEqual(response.status_code, 404, response.json())
        self.assertIn(NOT_FOUND_MESSAGE, response.json()['detail'])
