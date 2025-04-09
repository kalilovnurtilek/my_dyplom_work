from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import gettext_lazy

class CustomUserManager(BaseUserManager):
    """
    Кастомный менеджер модели юзера в котором используется email вместо id и username
    """
    def create_user(self, email, password, **extra_fields ):
        if not email :
            raise ValueError("email должен быть задан обязательно" )
        email = self.normalize_email(email)
        user = self.model(email= email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser (self, email, password, **extra_fields ):
        """
        Создание и сохранение суперпользователя
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_active", True)        
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Суперюзер иметь is_staff =True")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Суперюзер иметь is_superuser =True")
        return self.create_user(email, password , **extra_fields)