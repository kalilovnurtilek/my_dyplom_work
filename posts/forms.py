from django import forms
from .models import PDFPost
from posts.models import Comment, Post

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields =("name","text")

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ("title", "content")


class PDFPostForm(forms.ModelForm):
    class Meta:
        model = PDFPost
        fields = ['title', 'pdf_file', 'allowed_users']
        widgets = {
            'allowed_users': forms.CheckboxSelectMultiple
        }