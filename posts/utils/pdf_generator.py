# posts/utils/pdf_generator.py

# -*- coding: utf-8 -*-
import os
from django.conf import settings

# Сначала регистрируем шрифт — до любых импортов platypus!
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

fonts_folder = os.path.join(settings.BASE_DIR, 'posts', 'utils', 'fonts')
dejavu_path   = os.path.join(fonts_folder, 'DejaVuSans.ttf')

# DEBUG: убедимся, что файл найдён
print("Font folder exists:", os.path.isdir(fonts_folder))
print("DejaVuSans.ttf exists:", os.path.isfile(dejavu_path))

# Регистрируем DejaVuSans ТОЛЬКО ЗДЕСЬ
pdfmetrics.registerFont(TTFont('DejaVuSans', dejavu_path))

# Теперь можно импортировать остальное
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle


def generate_post_pdf(post):
    """
    Генерирует PDF-протокол для объекта post,
    сохраняет в MEDIA_ROOT/protocols и возвращает путь.
    """
    # Папка для протоколов
    protocols_folder = os.path.join(settings.MEDIA_ROOT, 'protocols')
    os.makedirs(protocols_folder, exist_ok=True)

    # Файл
    file_path = os.path.join(protocols_folder, f'post_{post.id}_protocol.pdf')
    doc = SimpleDocTemplate(file_path, pagesize=A4)
    elements = []

    # Стили с вашим шрифтом
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name='ProtocolTitle',
        fontName='DejaVuSans',
        fontSize=16,
        leading=20,
        spaceAfter=12,
    ))
    styles.add(ParagraphStyle(
        name='TableCell',
        fontName='DejaVuSans',
        fontSize=12,
        leading=14,
    ))

    # Заголовок
    elements.append(Paragraph(f'Протокол по заявлению: {post.title}', styles['ProtocolTitle']))
    elements.append(Spacer(1, 12))

    # Таблица
    data = [['№', 'Название предмета', 'Кредиты']]
    for i, ps in enumerate(post.post_subjects.select_related('subject'), start=1):
        data.append([
            Paragraph(str(i), styles['TableCell']),
            Paragraph(ps.subject.name, styles['TableCell']),
            Paragraph(str(ps.credits), styles['TableCell']),
        ])

    table = Table(data, colWidths=[40, 350, 100])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('GRID',       (0, 0), (-1, -1), 1, colors.black),
        ('ALIGN',      (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME',   (0, 0), (-1, -1), 'DejaVuSans'),
        ('FONTSIZE',   (0, 0), (-1, -1), 12),
    ]))
    elements.append(table)

    # Собираем PDF
    doc.build(elements)
    return file_path
