from django.contrib import admin

from django.contrib.auth.admin import UserAdmin
from users.forms import CustomUserChangeForm, CustomUserCreationForm
from users.models import CustomUser

class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = ('email', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_active', 'is_superuser')
    ordering = ('email',)
    search_fields = ('email',)
    fieldsets = (
        ( "Основная информация",{'fields':('email','password')}),
        ("Права пользователя", {'fields':('is_staff','is_active','groups','user_permissions')}),
    )

admin.site.register(CustomUser, CustomUserAdmin)
