from django import forms
from posts.models import Post, Comment, Specialty, Subject, Cours

class SubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = ['name']


class PostForm(forms.ModelForm):
    cours = forms.ModelChoiceField(queryset=Cours.objects.all(), required=False)

    class Meta:
        model = Post
        fields = [
            'title',
            'content',
            'status',
            'specialty',
            'pdf_file',         
            'transcript_file',
            'cours',
        ]
        widgets = {
            'specialty': forms.Select(attrs={'class': 'form-control'}),
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']

    def clean_text(self):
        text = self.cleaned_data.get('text')
        if not text:
            raise forms.ValidationError("Комментарий бош болбошу керек.")
        return text


class SpecialtyForm(forms.ModelForm):
    class Meta:
        model = Specialty
        fields = ['name', 'short_name', 'code', 'curriculum_file']
