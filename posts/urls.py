from django.urls import path

from posts.views import hello, get_index

urlpatterns = [
path("hello/", hello, name="helo-view"),
path("", get_index, name="index-page"),
]
