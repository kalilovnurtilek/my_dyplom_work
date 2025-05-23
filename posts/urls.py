from django.urls import path
from .views import (
    IndexView,
    AboutView,
    PostCreateView,
    PostUpdateView,
    PostDeleteView,
    PostDetailView,
    SuperuserPostListView,
    CreateSpecialtyView,
    CreateSubjectView,
    get_curriculum_file,
    serve_pdf, 
    
)

urlpatterns = [
    path("", IndexView.as_view(), name="index-page"),
    path("about/", AboutView.as_view(), name="get-about"),
    path("create/", PostCreateView.as_view(), name="post-create"),
    path("post/update/<int:pk>/", PostUpdateView.as_view(), name="post-update"),
    path("post/delete/<int:pk>/", PostDeleteView.as_view(), name="post-delete"),
    path('post/<int:pk>/', PostDetailView.as_view(), name='post-detail'),
    path('admin-posts/', SuperuserPostListView.as_view(), name='admin-posts'),
    path('create-specialty/', CreateSpecialtyView.as_view(), name="create-special"),
    path('create-subject/', CreateSubjectView.as_view(), name="create-subject"),
    path('media/pdf/<str:filename>/', serve_pdf, name='serve_pdf'),
 
    path('get-curriculum/<int:pk>/', get_curriculum_file, name='get-curriculum'),
]
