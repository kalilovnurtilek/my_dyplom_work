from django import forms
from posts.models import Post, Comment, Specialty, Subject,Cours

class SubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = ['name']


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = [
            'title',
            'content', 
            'status',
            'specialty',
            'pdf_file',
            'cours',  
        ]
        cours = forms.ModelChoiceField(queryset=Cours.objects.all(), required=False)
        widgets = {
            'specialty': forms.Select(),
        }
class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']

    def clean_text(self):
        text = self.cleaned_data.get('text')
        if not text:
            raise forms.ValidationError("Комментарий не может быть пустым.")
        return text

class SpecialtyForm(forms.ModelForm):
    class Meta:
        model = Specialty
        fields = ['name','short_name', 'code', ]