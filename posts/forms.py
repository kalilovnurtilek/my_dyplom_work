from django import forms
from posts.models import Post, Comment, Specialty

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = [
            'title',
            'content',
            'status',
            'specialty',
            'pdf_file',  # исправили на pdf_file
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