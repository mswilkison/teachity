from decimal import Decimal

from django import forms
from django.core.exceptions import ValidationError

from projects.forms import CleanedDecimalField

from .models import StripeTransaction


class StripeTransactionForm(forms.ModelForm):
    amount = CleanedDecimalField(max_digits=10,
                                 decimal_places=2,
                                 label='Amount (USD)')

    class Meta:
        model = StripeTransaction
        fields = ('amount',)

    def clean_amount(self):
        """
        Checks that the payment is greater than zero and converts it to cents.
        """
        amount = self.cleaned_data['amount']
        if amount > 0:
            amount = amount * Decimal('100')
            amount = amount.quantize(Decimal('1.'))
            return amount
        else:
            raise ValidationError('Amount must be greater than zero.')
