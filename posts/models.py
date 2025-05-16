from django.db import models
from django.conf import settings
from django.utils import timezone


class Cours(models.Model):
    cours = models.CharField(verbose_name="Курс студента")

    def __str__(self):
        return f"{self.cours}"


class Specialty(models.Model):
    name = models.CharField(max_length=255, verbose_name="Специальность")
    short_name = models.CharField(max_length=10, verbose_name="Укороченная название")
    code = models.CharField(max_length=20, verbose_name="Код специальности")

    def __str__(self):
        return f"{self.code} – {self.name}"


class Subject(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class Curriculum(models.Model):
    specialty = models.ForeignKey(Specialty, on_delete=models.CASCADE, related_name='curriculums', verbose_name='Специальность')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, verbose_name='Дисциплина')
    semester = models.PositiveIntegerField(verbose_name='Семестр')
    credits = models.DecimalField(max_digits=4, decimal_places=1, verbose_name='Кредиты')

    def __str__(self):
        return f"{self.specialty.short_name} – {self.subject.name} (Семестр {self.semester})"


class Post(models.Model):
    cours = models.ForeignKey(Cours, on_delete=models.SET_NULL, null=True, blank=True)
    title = models.CharField(max_length=255)
    content = models.TextField()
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    status = models.CharField(
        max_length=20,
        choices=[('draft', 'Черновик'), ('published', 'Опубликован')],
        default='draft'
    )
    pdf_file = models.FileField(
        upload_to='pdfs/',
        null=True,
        blank=True,
        verbose_name='Заявление студента (PDF/скан)'
    )
    created = models.DateTimeField(auto_now_add=True)
    specialty = models.ForeignKey(
        Specialty,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name='Приоритетная специальность'
    )
    protocol_number = models.CharField(
        max_length=20,
        unique=True,
        blank=True,
        null=True,
        verbose_name='Номер протокола'
    )

    def save(self, *args, **kwargs):
        if not self.protocol_number:
            year = timezone.now().year
            count = Post.objects.filter(created__year=year).count() + 1
            self.protocol_number = f"{year}/{count:03d}"
        super().save(*args, **kwargs)

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


class PostSubject(models.Model):
    post = models.ForeignKey(Post, related_name='post_subjects', on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    credits = models.FloatField(verbose_name='Кредиты по заявлению')


class ApprovalStep(models.Model):
    post = models.ForeignKey(Post, related_name='approval_steps', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    order = models.IntegerField()
    is_approved = models.BooleanField(null=True, blank=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.get_full_name()} - Этап {self.order}"


class Comment(models.Model):
    text = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    post = models.ForeignKey('Post', on_delete=models.CASCADE)
    author = models.CharField(max_length=100)

    def __str__(self):
        return self.text
