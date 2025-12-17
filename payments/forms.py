from django import forms

class PaymentForm(forms.Form):
    phone_number = forms.CharField(
        max_length=15,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '254712345678'})
    )
    amount = forms.DecimalField(
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': '1'})
    )