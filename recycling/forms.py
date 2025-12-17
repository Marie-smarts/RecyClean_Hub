from django import forms
from .models import RecyclableItem, PickupRequest
from accounts.models import DropOffCenter

class RecyclableItemForm(forms.ModelForm):
    class Meta:
        model = RecyclableItem
        fields = ['material_type', 'weight', 'description', 'drop_off_center', 'image']
        widgets = {
            'material_type': forms.Select(attrs={'class': 'form-select', 'id': 'id_material_type'}),
            'weight': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0.01', 'id': 'id_weight'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'id': 'id_description'}),
            'drop_off_center': forms.Select(attrs={'class': 'form-select', 'id': 'id_drop_off_center'}),
            'image': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*', 'id': 'id_image'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['drop_off_center'].queryset = DropOffCenter.objects.filter(is_active=True)


class PickupRequestForm(forms.ModelForm):
    class Meta:
        model = PickupRequest
        fields = ['scheduled_date', 'total_weight', 'notes']
        widgets = {
            'scheduled_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'total_weight': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }