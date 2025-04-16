from django import forms
from posts.models import Post, Comment
from users.models import CustomUser
from django.contrib.auth import get_user_model
from django.contrib.auth import get_user_model

User = get_user_model()

class PostForm(forms.ModelForm):
    approval_users = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        widget=forms.SelectMultiple(attrs={'size': 10}),
        label="Маршрут согласования (в порядке сверху вниз)",
        required=True
    )

    class Meta:
        model = Post
        fields = ['title', 'content', 'status', 'pdf_file']

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text'] 