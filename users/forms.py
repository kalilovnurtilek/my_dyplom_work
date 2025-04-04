from django.contrib.auth.models import User
from django import forms

class UserRegistrationForms(forms.ModelForm):
    password = forms.CharField(label="Пароль",widget=forms.PasswordInput)
    password2 = forms.CharField(label="Подтверждение пароля",widget=forms.PasswordInput)
    
    
    
    def clean_password2(self):
        cd = self.cleaned_data
        if cd['password']!=cd['password2']:
            raise forms.ValidationError('Пароли не совпадают')
        
        return cd['password2']
    
    
    class Meta:
        model = User
        fields= ("username", "first_name", "email")

  