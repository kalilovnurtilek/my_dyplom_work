from django import forms
from posts.models import Post, Comment, Specialty, Subject, Cours, PostSubject
from django.forms import inlineformset_factory

class SubjectForm(forms.ModelForm):
    class Meta:
        model = PostSubject
        fields = ['subject', 'earned_credits']
        widgets = {
            'subject': forms.Select(attrs={'class': 'form-select w-75'}),
            'earned_credits': forms.NumberInput(attrs={
                'class': 'form-control w-25', 'step': 0.5, 'min': 0
            }),
        }

# Формсет для PostSubject
PostSubjectFormSet = inlineformset_factory(
    Post,
    PostSubject,
    form=SubjectForm,
    extra=1,
    can_delete=True
)

class PostForm(forms.ModelForm):
    cours = forms.ModelChoiceField(queryset=Cours.objects.all(), required=False)
    subjects = forms.ModelMultipleChoiceField(
        queryset=Subject.objects.none(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label='Предметтер'
    )

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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Настройка queryset для subjects в зависимости от выбранной specialty
        if 'specialty' in self.data:
            try:
                spec_id = int(self.data.get('specialty'))
                self.fields['subjects'].queryset = Subject.objects.filter(specialty_id=spec_id)
            except (ValueError, TypeError):
                self.fields['subjects'].queryset = Subject.objects.none()
        elif self.instance.pk and self.instance.specialty:
            self.fields['subjects'].queryset = Subject.objects.filter(specialty=self.instance.specialty)
        else:
            self.fields['subjects'].queryset = Subject.objects.none()

    def save(self, commit=True):
        post = super().save(commit=False)
        if commit:
            post.save()
            selected_subjects = self.cleaned_data.get('subjects') or []
            # Сбрасываем старые связи
            PostSubject.objects.filter(post=post).delete()
            # Создаем новые
            for subj in selected_subjects:
                PostSubject.objects.create(post=post, subject=subj, earned_credits=0)
        return post

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
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Адистиктин толук аты'
            }),
            'short_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Кыскача аты'
            }),
            'code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Адистик коду'
            }),
            'curriculum_file': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'application/pdf'
            }),
        }
