# forms.py

from django import forms
from posts.models import Post, Comment

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'content', 'status', 'pdf_file']

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
