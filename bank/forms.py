from django import forms
from .models import Refill, CashCall


class RefillForm(forms.ModelForm):
    class Meta:
        model = Refill
        fields = ["amount"]


class CashCallForm(forms.ModelForm):
    class Meta:
        model = CashCall
        fields = ["amount"]

    def __init__(self, *args, **kwargs):
        self.user = kwargs['initial']['user']
        super(CashCallForm, self).__init__(*args, **kwargs)

    def clean_amount(self):
        amount = self.cleaned_data['amount']
        balance = self.user.user_balance.get()

        if balance.balance < amount:
            raise forms.ValidationError(
                'You Can Not Withdraw More Than Your Balance.'
            )
        return amount
