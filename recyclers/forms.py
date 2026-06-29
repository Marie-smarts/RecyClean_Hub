from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import RecyclingCompany
from .services import SUBSCRIPTION_FEATURES


class RecyclerRegistrationStep1Form(forms.Form):
    company_name = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )
    registration_number = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )
    kra_pin = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )
    kra_pin_certificate = forms.FileField(
        widget=forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf,.jpg,.png'}),
    )
    nema_permit = forms.FileField(
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf,.jpg,.png'}),
    )
    website = forms.URLField(
        required=False,
        widget=forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://'}),
    )
    company_email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control'}),
    )
    facility_photo = forms.ImageField(
        widget=forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
    )
    physical_address = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
    )
    latitude = forms.DecimalField(
        max_digits=9,
        decimal_places=6,
        widget=forms.HiddenInput(),
    )
    longitude = forms.DecimalField(
        max_digits=9,
        decimal_places=6,
        widget=forms.HiddenInput(),
    )


class RecyclerRegistrationStep2Form(forms.Form):
    MATERIAL_CHOICES = [
        ('plastic', 'Plastic'),
        ('metal', 'Metal'),
        ('paper', 'Paper'),
        ('glass', 'Glass'),
        ('aluminium', 'Aluminium'),
    ]

    contact_name = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )
    contact_title = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )
    contact_phone = forms.CharField(
        max_length=15,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '2547XXXXXXXX'}),
    )
    contact_national_id = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )
    materials_accepted = forms.MultipleChoiceField(
        choices=MATERIAL_CHOICES,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
    )
    weekly_capacity_tonnes = forms.FloatField(
        min_value=0.1,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
    )
    price_per_kg_plastic = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        min_value=0,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
    )
    price_per_kg_metal = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        min_value=0,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
    )
    price_per_kg_paper = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        min_value=0,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
    )
    price_per_kg_glass = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        min_value=0,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
    )
    price_per_kg_aluminium = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        min_value=0,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
    )
    subscription_plan = forms.ChoiceField(
        choices=RecyclingCompany.SUBSCRIPTION_PLAN_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
    )


class RecyclerRegistrationStep3Form(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control'}),
    )
    first_name = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )
    last_name = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )
    confirm_submission = forms.BooleanField(
        required=True,
        label='I confirm the information provided is accurate.',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control'})


class AdminRejectForm(forms.Form):
    rejection_reason = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        label='Reason for rejection',
    )


def subscription_plan_context():
    return {
        'subscription_features': SUBSCRIPTION_FEATURES,
        'plan_prices': {'basic': 500, 'standard': 1000, 'premium': 1500},
    }
