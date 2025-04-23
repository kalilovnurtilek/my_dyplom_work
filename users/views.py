from django.views.generic.edit import FormView
from django.contrib.auth import logout
from django.urls import reverse_lazy
from django.shortcuts import render
from .forms import UserRegistrationForms
from django.contrib.auth.models import User

class UserRegisterView(FormView):
    template_name = 'registration/register.html'
    form_class = UserRegistrationForms
    success_url = reverse_lazy('register_done')

    def form_valid(self, form):
        # Создаём пользователя, но не сохраняем сразу
        new_user = form.save(commit=False)
        # Хешируем пароль
        new_user.set_password(form.cleaned_data['password'])
        new_user.save()
        # Можно передать пользователя в шаблон, если хочешь отрендерить, а не редиректить
        return render(self.request, "registration/register_done.html", {"user": new_user})


def logout_view(request):
    logout(request)
    return render(request, "registration/logged_out.html")  # шаблон после выхода