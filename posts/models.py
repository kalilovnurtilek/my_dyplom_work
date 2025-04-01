from django.db import models

class Post(models.Model):
    title = models.CharField(
        max_length=300,
        verbose_name="Заголовок")
    content = models.TextField(
        verbose_name="Содержание"
    )
    created = models.DateTimeField(
        auto_now=True,
        verbose_name="Дата создание")
    status = models.BooleanField(
        default=True,
        verbose_name="Статус публикации")

    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ('-created',)
        verbose_name = "Пост"
        verbose_name_plural = "Посты"