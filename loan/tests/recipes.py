from model_bakery.recipe import Recipe

from decimal import Decimal
from random import randrange

from loan.models import Loan

loan = Recipe(Loan, interestRate=Decimal(str((randrange(1, 2000))/10000)))
