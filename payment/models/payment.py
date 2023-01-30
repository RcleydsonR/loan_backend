
from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal

from loan.models import Loan
import uuid


class Payment(models.Model):
    idPayment = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    value = models.DecimalField(
        max_digits=6, decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))])
    paymentDate = models.DateTimeField()
    loan = models.ForeignKey(Loan, on_delete=models.PROTECT, related_name='payments')
