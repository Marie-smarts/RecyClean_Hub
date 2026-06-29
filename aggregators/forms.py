from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from accounts.models import UserProfile
from recycling.models import PickupRequest

from .models import AggregatorPickupAssignment, AggregatorProfile, CollectionLog


class PasswordToggleUserCreationForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'username' in self.fields:
            del self.fields['username']
        self.fields['password1'].widget = forms.PasswordInput(
            attrs={'class': 'form-control', 'id': 'id_password1', 'autocomplete': 'new-password'},
        )
        self.fields['password2'].widget = forms.PasswordInput(
            attrs={'class': 'form-control', 'id': 'id_password2', 'autocomplete': 'new-password'},
        )


class AggregatorRegistrationForm(PasswordToggleUserCreationForm):
    first_name = forms.CharField(
        required=True,
        label='First name',
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )
    last_name = forms.CharField(
        required=True,
        label='Last name',
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )
    national_id_number = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )
    national_id_photo = forms.ImageField(
        widget=forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
    )
    phone = forms.CharField(
        max_length=15,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '254712345678'}),
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control'}),
    )
    service_area = forms.CharField(
        label='Service area',
        widget=forms.Textarea(
            attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Zones or areas you cover'},
        ),
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'password1', 'password2']


class CollectionLogForm(forms.ModelForm):
    class Meta:
        model = CollectionLog
        fields = ['material_type', 'weight_kg', 'gross_amount', 'notes']
        widgets = {
            'material_type': forms.Select(attrs={'class': 'form-select'}),
            'weight_kg': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0.01'}),
            'gross_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0.01'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class PickupStatusForm(forms.ModelForm):
    class Meta:
        model = AggregatorPickupAssignment
        fields = ['status', 'notes']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class AdminAssignPickupForm(forms.Form):
    aggregator = forms.ModelChoiceField(
        queryset=AggregatorProfile.objects.filter(verification_status='approved'),
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
    pickup_request = forms.ModelChoiceField(
        queryset=PickupRequest.objects.filter(status__in=['pending', 'scheduled']),
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
