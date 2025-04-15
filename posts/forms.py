from django import forms
from posts.models import Post, Comment
from users.models import CustomUser

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text'] 



class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'content', 'pdf_file', 'allowed_users', 'status']
        widgets = {
            'allowed_users': forms.CheckboxSelectMultiple
        }

    allowed_users = forms.ModelMultipleChoiceField(
        queryset=CustomUser.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )

    def clean(self):
        cleaned_data = super().clean()
        # Отладка: выводим очищенные данные для проверки
        print(cleaned_data)
        return cleaned_data