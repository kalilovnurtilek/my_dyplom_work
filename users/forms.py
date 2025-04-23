# from django.contrib.auth.models import User
# from django import forms
# from users.models import CustomUser
# from django.contrib.auth.forms import UserCreationForm, UserChangeForm
# from django.contrib.auth import get_user_model

from django import forms
from django.contrib.auth import get_user_model
from users.models import CustomUser
from django.contrib.auth.forms import UserCreationForm, UserChangeForm

User = get_user_model() 


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ("email","first_name",)




class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ("email",)

User = get_user_model()

class UserRegistrationForms(forms.ModelForm):
    password = forms.CharField(label="Пароль", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Подтверждение пароля", widget=forms.PasswordInput)
    first_name = forms.CharField(label="Имя", max_length=30, required=True)
    last_name = forms.CharField(label="Фамилия", max_length=30, required=True)
    position = forms.CharField(label="Должность", max_length=100, required=True)

    def clean_password2(self):
        cd = self.cleaned_data
        if cd['password'] != cd['password2']:
            raise forms.ValidationError('Пароли не совпадают')
        return cd['password2']

    class Meta:
        model = User
        fields = ("email", "first_name", "last_name", "position") 