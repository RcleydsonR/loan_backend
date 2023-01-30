# Generated by Django 4.1.5 on 2023-01-30 14:03

from decimal import Decimal
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('loan', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='loan',
            name='interestRate',
            field=models.DecimalField(decimal_places=4, max_digits=5, validators=[django.core.validators.MinValueValidator(Decimal('0.0001')), django.core.validators.MaxValueValidator(Decimal('1.0000'))]),
        ),
    ]
