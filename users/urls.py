from django.urls import path
from .views import UserRegisterView, logout_view

urlpatterns = [
path("register/", UserRegisterView.as_view(), name='register'),
path('logout/', logout_view, name='logout'),

]