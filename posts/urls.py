from django.urls import path

from .views import IndexView,  AboutView ,PostCreateView, PostUpdateView, PostDeleteView, PostDetailView,SuperuserPostListView,CreateSpecialtyView, CreateSubjectView, calculate_credits_api, get_curriculums, CurriculumCreateView, get_specialty_transcript




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
    path('api/calculate-credits/', calculate_credits_api, name='calculate-credits'),
    path('api/get-curriculums/', get_curriculums, name='get-curriculums'),
    path('curriculum/create/', CurriculumCreateView.as_view(), name='curriculum-create'),
    path('api/get_specialty_transcript/', get_specialty_transcript, name='get_specialty_transcript'),
    
]
