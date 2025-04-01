from django.urls import path

from posts.views import hello, IndexView, get_contacts, AboutView, PostCreateView, PostUpdateView, PostDeleteView, PostDetailView

urlpatterns = [
path("hello/", hello, name="helo-view"),
path("", IndexView.as_view(), name="index-page"),
path("contacts/", get_contacts, name="get-contacts"),
path("about/", AboutView.as_view(), name="get-about"),
path("create/", PostCreateView.as_view(), name="post-create"),
path("post/update/<int:pk>/", PostUpdateView.as_view(), name="post-update"),
path("post/delete/<int:pk>/", PostDeleteView.as_view(), name="post-delete"),
path("post/<int:pk>/",PostDetailView.as_view(),name='post-detail'),

]
