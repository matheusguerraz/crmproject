from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    name = forms.CharField(required=True)
    date_of_birth = forms.DateField(required=True)

    class Meta:
        model = CustomUser
        fields = ('email', 'name', 'date_of_birth', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.name = self.cleaned_data['name']
        user.date_of_birth = self.cleaned_data['date_of_birth']
        if commit:
            user.save()
        return user
