from django import forms
from posts.models import Post, Comment, Specialty

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = [
            'title',
            'content',
            'status',
            'application_file',  # поле для загрузки заявления
            'specialty',         # единичный выбор специальности
        ]
        widgets = {
            'specialty': forms.Select(),
        }
class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']

class SpecialtyForm(forms.ModelForm):
    class Meta:
        model = Specialty
        fields = ['name','code']