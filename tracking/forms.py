from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Shipment

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
        fields = ['sender_name', 'receiver_name', 'origin', 'destination']
        widgets = {
            'sender_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., John Doe'}),
            'receiver_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Jane Smith'}),
            'origin': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., New York, NY'}),
            'destination': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Los Angeles, CA'}),
        }