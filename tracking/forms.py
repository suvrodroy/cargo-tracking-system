from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Shipment, ShipmentUpdate

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ['username', 'email']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

class ShipmentForm(forms.ModelForm):
    class Meta:
        model = Shipment
        fields = [
            'sender_name', 'receiver_name', 'origin', 'destination',
            'package_type', 'weight', 'quantity',
            'priority', 'estimated_delivery_date'
        ]
        widgets = {
            # Shipment Information
            'sender_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., John Doe'}),
            'receiver_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Jane Smith'}),
            'origin': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., New York, NY'}),
            'destination': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Los Angeles, CA'}),
            
            # Package Information
            'package_type': forms.Select(attrs={'class': 'form-select'}),
            'weight': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            
            # Delivery Information
            'priority': forms.Select(attrs={'class': 'form-select'}),
            'estimated_delivery_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Define fieldsets to allow easy iteration in templates
        self.fieldsets = {
            'Shipment Information': [
                self['sender_name'], self['receiver_name'], 
                self['origin'], self['destination']
            ],
            'Package Information': [
                self['package_type'], self['weight'], self['quantity']
            ],
            'Delivery Information': [
                self['priority'], self['estimated_delivery_date']
            ]
        }
        
        # Add custom data attributes to widgets for CSS/JS targeting if needed
        for field in ['sender_name', 'receiver_name', 'origin', 'destination']:
            self.fields[field].widget.attrs['data-group'] = 'shipment-info'
            
        for field in ['package_type', 'weight', 'quantity']:
            self.fields[field].widget.attrs['data-group'] = 'package-info'
            
        for field in ['priority', 'estimated_delivery_date']:
            self.fields[field].widget.attrs['data-group'] = 'delivery-info'

class ShipmentUpdateForm(forms.ModelForm):
    status = forms.ChoiceField(
        choices=Shipment.StatusChoices.choices, 
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    class Meta:
        model = ShipmentUpdate
        fields = ['update_message', 'location']
        widgets = {
            'update_message': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Arrived at sorting facility'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Dhaka, Bangladesh'}),
        }