from core.consts.interestType import INTEREST_TYPE

from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator

from decimal import Decimal
import uuid


class Loan(models.Model):
    idLoan = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nominalValue = models.DecimalField(
        max_digits=6, decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))])
    interestRate = models.DecimalField(
        max_digits=6, decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01')), MaxValueValidator(Decimal('1.00'))])
    interestType = models.CharField(max_length=8, choices=INTEREST_TYPE)
    ipAddress = models.GenericIPAddressField()
    solicitationDate = models.DateTimeField()
    bank = models.CharField(max_length=50)
    client = models.CharField(max_length=80)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
