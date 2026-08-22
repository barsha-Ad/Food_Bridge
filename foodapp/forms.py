from django import forms
from .models import FoodDonation
from .models import HelpSupport
from django.contrib.auth.models import User

CATEGORY_CHOICES = [
    ('Cooked Food', 'Cooked Food'),
    ('Vegetarian', 'Vegetarian'),
    ('Non-Vegetarian', 'Non-Vegetarian'),
    ('Snacks', 'Snacks'),
    ('Fruits', 'Fruits'),
    ('Beverages', 'Beverages'),
    ('Bakery', 'Bakery'),
    ('Dairy', 'Dairy'),
]


class FoodDonationForm(forms.ModelForm):
    class Meta:
        model = FoodDonation
        exclude = ['status']

        widgets = {
            'donor_name': forms.TextInput(attrs={'class': 'w-full border rounded-lg p-3'}),
            'phone': forms.TextInput(attrs={'class': 'w-full border rounded-lg p-3'}),
            'email': forms.EmailInput(attrs={'class': 'w-full border rounded-lg p-3'}),
            'food_name': forms.TextInput(attrs={'class': 'w-full border rounded-lg p-3'}),
            'category': forms.Select(
                 choices=CATEGORY_CHOICES,
                 attrs={'class': 'w-full border rounded-lg p-3'}
            ),           
            'quantity': forms.TextInput(attrs={'class': 'w-full border rounded-lg p-3'}),
            'pickup_address': forms.Textarea(attrs={'class': 'w-full border rounded-lg p-3', 'rows': 3}),
            'city': forms.TextInput(attrs={'class': 'w-full border rounded-lg p-3'}),
            'expiry_time': forms.TimeInput(attrs={'class': 'w-full border rounded-lg p-3', 'type': 'time'}),
            'food_image': forms.ClearableFileInput(attrs={'class': 'w-full border rounded-lg p-3'}),
        }



class HelpSupportForm(forms.ModelForm):
    class Meta:
        model = HelpSupport
        fields = "__all__"

        widgets = {
            'name': forms.TextInput(attrs={'class':'w-full border rounded-lg p-3'}),
            'email': forms.EmailInput(attrs={'class':'w-full border rounded-lg p-3'}),
            'subject': forms.TextInput(attrs={'class':'w-full border rounded-lg p-3'}),
            'message': forms.Textarea(attrs={'class':'w-full border rounded-lg p-3','rows':5}),
        }

from django import forms
from django.contrib.auth.models import User

class SignupForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']