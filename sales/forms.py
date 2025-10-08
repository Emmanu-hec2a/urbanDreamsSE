from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import MenuItem, Sale, SaleItem
import pytz
from django.utils import timezone


class MenuItemForm(forms.ModelForm):
    class Meta:
        model = MenuItem
        fields = ['name', 'category', 'unit_price', 'description', 'image', 'is_available']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'unit_price': forms.NumberInput(attrs={'step': '0.01'}),
        }


class SaleForm(forms.ModelForm):
    class Meta:
        model = Sale
        fields = ['sale_date', 'payment_method', 'notes']
        widgets = {
            'sale_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        eat_tz = pytz.timezone('Africa/Nairobi')
        current_time = timezone.now().astimezone(eat_tz).strftime('%Y-%m-%dT%H:%M')
        self.fields['sale_date'].initial = current_time
        print("EAT current time:", current_time)



class SaleItemForm(forms.ModelForm):
    class Meta:
        model = SaleItem
        fields = ['menu_item', 'quantity']
        widgets = {
            'quantity': forms.NumberInput(attrs={'min': 1}),
        }


class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    is_staff = forms.BooleanField(required=False, label='Admin User')

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'is_staff', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.is_staff = self.cleaned_data['is_staff']
        if commit:
            user.save()
