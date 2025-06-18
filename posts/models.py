# models.py

from django.db import models
from django.conf import settings
from django.contrib.postgres.fields import JSONField  
from django.db.models import JSONField
from django.core.validators import FileExtensionValidator  



class Specialty(models.Model):
    name = models.CharField(max_length=255, verbose_name="адистиктин аталышы")
    short_name = models.CharField(max_length=10, verbose_name="кыскартылган адистиктин аталышы")
    code = models.CharField(max_length=20, verbose_name="адистиктин коду")
    pdf_file = models.FileField(
        upload_to='pdfs/',  
        null=True,
        blank=True,
        verbose_name='окуу план(PDF/скан)'
    )
    
    def __str__(self):
        return f"{self.code} – {self.name}"
    

class SpecialtyTranscript(models.Model):
    specialty = models.OneToOneField(
        Specialty, 
        on_delete=models.CASCADE,
        related_name='transcript',
        verbose_name="Специальность"
    )
    transcript_file = models.FileField(
        upload_to='specialty_transcripts/',
        validators=[FileExtensionValidator(['pdf'])],
        verbose_name="Файл транскрипта (PDF)"
    )

    def __str__(self):
        return f"Транскрипт для {self.specialty}"



class Post(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    pdf_file = models.FileField(upload_to='post_pdfs/', validators=[FileExtensionValidator(['pdf'])],
        blank=True,null=True)
    status = models.CharField(max_length=20,choices=[('draft', 'Черновик'), ('published', 'Опубликован')],
        default='draft')  
    pdf_file = models.FileField(upload_to='pdfs/', null=True, blank=True,
        verbose_name='Заявление студента (PDF/скан)')
    created = models.DateTimeField(auto_now_add=True)
    specialty = models.ForeignKey(Specialty,null=True,blank=True,
on_delete=models.SET_NULL,
        verbose_name='Приоритетная специальность')

    credit_diff_data = JSONField(
        null=True,
        blank=True,
        verbose_name='Данные сравнения кредитов'
    )
    def __str__(self):
        return self.title

    @property
    def missing_credits(self):
    
        return self.credit_diff_data.get('total_missing', 0) if self.credit_diff_data else 0

    @property
    def status_approval(self):
        if self.approval_steps.filter(is_approved=None).exists():
            return 'in_progress'
        elif self.approval_steps.filter(is_approved=False).exists():
            return 'rejected'
        elif self.approval_steps.filter(is_approved=True).exists():
            return 'approved'
        return 'not_started'

    @property
    def current_approver(self):
        step = self.approval_steps.filter(is_approved=None).order_by('order').first()
        return step.user if step else None

    class Meta:
        ordering = ['-created']
        verbose_name = "Пост"
        verbose_name_plural = "Посты"



class ApprovalStep(models.Model):
    post = models.ForeignKey(Post, related_name='approval_steps', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    order = models.IntegerField()
    is_approved = models.BooleanField(null=True, blank=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.get_full_name()} - Этап {self.order}"

    

class Subject(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class PostSubject(models.Model):
    post = models.ForeignKey(Post, related_name='post_subjects', on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    credits = models.FloatField()  # деканат вводит вручную

class Comment(models.Model):
    text = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    post = models.ForeignKey('Post', on_delete=models.CASCADE)
    author = models.CharField(max_length=100)

    def __str__(self):
        return self.text



class Curriculum(models.Model):
    specialty = models.ForeignKey(
        Specialty,
        on_delete=models.CASCADE,
        related_name='curriculums',
        verbose_name='Специальность'
    )
    year = models.IntegerField(verbose_name='Год плана')
    is_active = models.BooleanField(
        default=True,
        verbose_name='Активный план'
    )
    pdf_file = models.FileField(
        upload_to='curriculum_pdfs/',
        null=True,
        blank=True,
        verbose_name='PDF учебного плана'
    )
    total_credits = models.FloatField(
        default=0,
        verbose_name='Общее количество кредитов'
    )

    def save(self, *args, **kwargs):
        # Автоматический расчет общего количества кредитов при сохранении
        if self.pk:
            self.total_credits = sum(
                cs.credits for cs in self.subjects.all()
            )
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Учебный план {self.specialty} ({self.year} г.)"

class CurriculumSubject(models.Model):
    curriculum = models.ForeignKey(
        Curriculum,
        on_delete=models.CASCADE,
        related_name='subjects'
    )
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        verbose_name='Дисциплина'
    )
    credits = models.FloatField(verbose_name='Кредиты')
    semester = models.PositiveSmallIntegerField(
        default=1,
        verbose_name='Семестр'
    )
    is_required = models.BooleanField(
        default=True,
        verbose_name='Обязательная дисциплина'
    )

    class Meta:
        unique_together = ('curriculum', 'subject')
        ordering = ['semester', 'subject__name']
        verbose_name = 'Дисциплина учебного плана'
        verbose_name_plural = 'Дисциплины учебного плана'

    def __str__(self):
        return f"{self.subject.name} ({self.credits} кредитов)"
