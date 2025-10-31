from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    full_name = forms.CharField(max_length=200)
    phone_number = forms.CharField(max_length=20)
    date_of_birth = forms.DateField(widget=forms.DateInput(attrs={"type": "date"}))
    address = forms.CharField(widget=forms.Textarea(attrs={"rows": 2}))
    national_id = forms.CharField(required=False)
    bvn = forms.CharField(required=False)

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "full_name",
            "phone_number",
            "date_of_birth",
            "address",
            "national_id",
            "bvn",
            "password1",
            "password2",
        ]
