from django.urls import reverse_lazy
from django import forms
from django.core.exceptions import ValidationError
from .models import Post, Curriculum, Specialty, SpecialtyTranscript, Subject, Comment


class SubjectForm(forms.ModelForm):
    class Meta: 
        model = Subject
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Название дисциплины'
            })
        }

class PostForm(forms.ModelForm):
    curriculum = forms.ModelChoiceField(
        queryset=Curriculum.objects.none(),
        required=False,
        label='Учебный план для сравнения',
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'curriculum-select'
        })
    )

    class Meta:
        model = Post
        fields = [
            'title',
            'content',
            'status',
            'specialty',
            'pdf_file',
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Название заявления'
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Описание...'
            }),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'specialty': forms.Select(attrs={
                'class': 'form-control',
                'id': 'id_specialty',
                'data-transcript-url': reverse_lazy('get_specialty_transcript')
            }),
            'pdf_file': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf',
                'id': 'id_pdf_file'
            }),
        }
        labels = {
            'pdf_file': 'Транскрипт студента (PDF)',
            'specialty': 'Целевая специальность'
        }

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)  # Извлекаем request из kwargs
        super().__init__(*args, **kwargs)  # Передаём оставшиеся аргументы
        
        # Фильтрация данных по пользователю, если нужно
        if self.request and self.request.user.is_authenticated:
            # Пример фильтрации специальностей
            self.fields['specialty'].queryset = Specialty.objects.all()
        
        # Инициализация queryset для curriculum
        if 'specialty' in self.data:
            try:
                specialty_id = int(self.data.get('specialty'))
                self.fields['curriculum'].queryset = Curriculum.objects.filter(
                    specialty_id=specialty_id,
                    is_active=True
                ).order_by('-year')
            except (ValueError, TypeError):
                pass
        elif self.instance.pk and self.instance.specialty:
            self.fields['curriculum'].queryset = Curriculum.objects.filter(
                specialty=self.instance.specialty,
                is_active=True
            ).order_by('-year')
        
        # Автозаполнение транскрипта, если специальность уже выбрана
        if self.instance.pk and self.instance.specialty:
            transcript = SpecialtyTranscript.objects.filter(
                specialty=self.instance.specialty
            ).first()
            if transcript:
                self.initial['pdf_file'] = transcript.transcript_file

    def clean_pdf_file(self):
        pdf_file = self.cleaned_data.get('pdf_file')
        if pdf_file:
            if not pdf_file.name.endswith('.pdf'):
                raise ValidationError('Файл должен быть в формате PDF')
            if pdf_file.size > 10 * 1024 * 1024:  # 10MB limit
                raise ValidationError('Файл слишком большой (максимум 10 МБ)')
        return pdf_file

    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Автозагрузка транскрипта, если не загружен вручную
        if not instance.pdf_file and self.cleaned_data.get('specialty'):
            transcript = SpecialtyTranscript.objects.filter(
                specialty=self.cleaned_data['specialty']
            ).first()
            if transcript:
                instance.pdf_file = transcript.transcript_file
        
        if commit:
            instance.save()
            self.save_m2m()
        
        return instance
class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Ваш комментарий...'
            })
        }

class SpecialtyForm(forms.ModelForm):
    class Meta:
        model = Specialty
        fields = ['name', 'code', 'short_name', 'pdf_file']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'short_name': forms.TextInput(attrs={'class': 'form-control'}),
            'code': forms.TextInput(attrs={'class': 'form-control'}),
            'pdf_file' : forms.TextInput(attrs={'class': 'form-control'}),
        }

class CurriculumUploadForm(forms.ModelForm):
    class Meta:
        model = Curriculum
        fields = ['specialty', 'year', 'pdf_file', 'is_active']
        widgets = {
            'specialty': forms.Select(attrs={'class': 'form-control'}),
            'year': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 2000,
                'max': 2100
            }),
            'pdf_file': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf'
            }),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }
        labels = {
            'pdf_file': 'PDF учебного плана'
        }

    def clean_year(self):
        year = self.cleaned_data['year']
        if year < 2000 or year > 2100:
            raise ValidationError('Некорректный год учебного плана')
        return year