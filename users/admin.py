from django.contrib import admin

from django.contrib.auth.admin import UserAdmin
from users.forms import CustomUserChangeForm, CustomUserCreationForm
from users.models import CustomUser

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = ('email', 'get_full_name', 'is_staff', 'is_active')  # Добавляем get_full_name
    list_filter = ('is_staff', 'is_active', 'is_superuser')
    ordering = ('email',)
    search_fields = ('email', 'first_name', 'last_name')  # добавляем поиск по first_name и last_name
    fieldsets = (
        ("Основная информация", {'fields': ('email', 'password', 'first_name', 'last_name')}),
        ("Права пользователя", {'fields': ('is_staff', 'is_active', 'groups', 'user_permissions')}),
    )

    add_fieldsets = (
        ("Создание пользователя", {
            "classes": ("wide",),
            "fields": ('email', 'password1', 'password2', 'first_name', 'last_name', 'is_staff', 'is_active', 'groups', 'user_permissions')
        }),
    )

admin.site.register(CustomUser, CustomUserAdmin)
