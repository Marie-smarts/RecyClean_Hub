from django import forms
from django.contrib.auth.forms import PasswordResetForm, UserCreationForm
from django.contrib.auth.models import User

from .models import DropOffCenter, RecyclerApplication, UserProfile


def apply_modern_field(form_field, css_class='form-control'):
    attrs = form_field.widget.attrs
    attrs['class'] = css_class
    if isinstance(form_field.widget, forms.CheckboxInput):
        attrs['class'] = 'form-check-input'


class EmailPasswordResetForm(PasswordResetForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].widget.attrs.update(
            {
                'class': 'form-control form-control-lg',
                'placeholder': 'you@example.com',
                'autocomplete': 'email',
            }
        )


class PasswordToggleUserCreationForm(UserCreationForm):
    """UserCreationForm with password fields styled for toggle UI."""

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


class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    first_name = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))

    role = forms.ChoiceField(
        choices=[c for c in UserProfile.ROLE_CHOICES if c[0] not in ('aggregator', 'user')],
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
    phone = forms.CharField(
        max_length=15,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '254712345678'}),
    )
    address = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}))
    profile_image = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
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


class HouseholdUserRegistrationForm(PasswordToggleUserCreationForm):
    first_name = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First name'}),
    )
    last_name = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last name'}),
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'you@example.com'}),
    )
    phone = forms.CharField(
        max_length=15,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '254712345678'}),
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'password1', 'password2']


class HostRegistrationForm(PasswordToggleUserCreationForm):
    BUSINESS_TYPE_CHOICES = DropOffCenter.BUSINESS_TYPE_CHOICES
    MATERIAL_CHOICES = [
        ('plastic', 'Plastic'),
        ('paper', 'Paper'),
        ('metal', 'Metal'),
        ('glass', 'Glass'),
        ('aluminium', 'Aluminium'),
    ]

    first_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    phone = forms.CharField(max_length=15, widget=forms.TextInput(attrs={'class': 'form-control'}))
    business_name = forms.CharField(max_length=200, widget=forms.TextInput(attrs={'class': 'form-control'}))
    business_type = forms.ChoiceField(
        choices=BUSINESS_TYPE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
    physical_address = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}))
    operating_hours_open = forms.TimeField(widget=forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}))
    operating_hours_close = forms.TimeField(widget=forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}))
    materials_accepted = forms.MultipleChoiceField(
        choices=MATERIAL_CHOICES,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
    )
    mpesa_number = forms.CharField(max_length=15, widget=forms.TextInput(attrs={'class': 'form-control'}))
    national_id_number = forms.CharField(max_length=20, widget=forms.TextInput(attrs={'class': 'form-control'}))
    national_id_photo = forms.ImageField(widget=forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}))
    shopfront_photo = forms.ImageField(widget=forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}))

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'password1', 'password2']


class RecyclerPartnerRegistrationForm(PasswordToggleUserCreationForm):
    company_name = forms.CharField(max_length=200, widget=forms.TextInput(attrs={'class': 'form-control'}))
    contact_name = forms.CharField(max_length=200, widget=forms.TextInput(attrs={'class': 'form-control'}))
    phone = forms.CharField(max_length=15, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    physical_address = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}))
    vehicle_info = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}))
    proof_document = forms.FileField(
        widget=forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf,.jpg,.png'}),
    )

    class Meta:
        model = User
        fields = ['email', 'password1', 'password2']


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['phone', 'address', 'profile_image']
        widgets = {
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'profile_image': forms.FileInput(attrs={'class': 'form-control'}),
        }


class DropOffCenterForm(forms.ModelForm):
    class Meta:
        model = DropOffCenter
        fields = [
            'name',
            'address',
            'phone',
            'latitude',
            'longitude',
            'image',
            'is_active',
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'latitude': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'step': 'any',
                    'placeholder': 'e.g. -1.2921',
                }
            ),
            'longitude': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'step': 'any',
                    'placeholder': 'e.g. 36.8219',
                }
            ),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
