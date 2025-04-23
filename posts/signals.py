from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Post, PostSubject, ApprovalStep
from .utils.pdf_generator import generate_post_pdf  # Импорт функции генерации PDF
import logging

logger = logging.getLogger(__name__)



@receiver(post_save, sender=PostSubject)
def update_pdf_on_subject_change(sender, instance, created, **kwargs):
    generate_post_pdf(instance.post)


@receiver(post_save, sender=ApprovalStep)
def update_pdf_on_approval_change(sender, instance, created, **kwargs):
    generate_post_pdf(instance.post)



@receiver(post_save, sender=Post)
def update_post_protocol(sender, instance, created, **kwargs):
    if not created:  # Если пост был обновлен (не новый)
        logger.info(f"Обновлен пост {instance.id}, генерируем PDF...")
        generate_post_pdf(instance)  # Генерация нового PDF
    else:
        logger.info(f"Создан новый пост {instance.id}")
