# models.py

from django.db import models
from django.conf import settings

from django.db import models
from django.conf import settings



class Specialty(models.Model):
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.code} – {self.name}"

class Post(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    status = models.CharField(
        max_length=20,
        choices=[('draft', 'Черновик'), ('published', 'Опубликован')],
        default='draft'
    )
    # Убираем поле pdf_file из формы, но оставляем для генерации протокола
    pdf_file = models.FileField(
        upload_to='pdfs/',  # файлы сохраняются в папке media/pdfs/
        null=True,
        blank=True,
        verbose_name='Заявление студента (PDF/скан)'
    )
    created = models.DateTimeField(auto_now_add=True)

    # Только одна приоритетная специальность
    specialty = models.ForeignKey(
        Specialty,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name='Приоритетная специальность'
    )

    def __str__(self):
        return self.title

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

