from django import forms
from posts.models import Post, Comment
from users.models import CustomUser
from django.contrib.auth import get_user_model
from django.contrib.auth import get_user_model

User = get_user_model()

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text'] 


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

    def save(self, commit=True):
        # Сохраняем объект Post, но не сохраняем многие ко многим пока
        post = super().save(commit=False)

        if commit:
            post.save()  # Сохраняем сам пост
            self.save_m2m()  # Сохраняем связи ManyToMany (пользователи для согласования)
        return post

