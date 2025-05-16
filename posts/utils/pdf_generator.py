import os
from django.conf import settings
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER

# Указываем путь к шрифту
fonts_folder = os.path.join(settings.BASE_DIR, 'posts', 'utils', 'fonts')
dejavu_path = os.path.join(fonts_folder, 'DejaVuSans.ttf')

# Регистрируем шрифт
pdfmetrics.registerFont(TTFont('DejaVuSans', dejavu_path))


def generate_post_pdf(post):
    # Папка для протоколов
    protocols_folder = os.path.join(settings.MEDIA_ROOT, 'protocols')
    os.makedirs(protocols_folder, exist_ok=True)

    # Путь к файлу PDF
    file_path = os.path.join(protocols_folder, f'post_{post.id}_protocol.pdf')
    doc = SimpleDocTemplate(file_path, pagesize=A4)
    elements = []

    # Стили
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name='ProtocolTitle',
        fontName='DejaVuSans',
        fontSize=10,
        leading=20,
        spaceAfter=12,
        alignment=TA_CENTER,
    ))
    styles.add(ParagraphStyle(
        name='TableCell',
        fontName='DejaVuSans',
        fontSize=12,
        leading=14,
    ))

    # Заголовок
    elements.append(Paragraph(
        'МФТИИ институтунун студенттерин которуу, тикелөө жана окуудан четтетүү боюнча<br/>'
        'түзүлгөн аттестациялык комиссиясынын отурумунун',
        styles['ProtocolTitle']
    ))
    elements.append(Paragraph('ПРОТОКОЛУ № ___', styles['ProtocolTitle']))
    elements.append(Spacer(1, 12))

    # Информация о студенте
    full_name = post.title
    speciality = post.content
    course = post.cours

    # Текст с описанием
    elements.append(Paragraph(
        f'I. Комиссиялык аттестациялоонун негизинде <b>{full_name}</b> '
        f'институттун окуу бөлүмүнүн «{speciality}» багытынын профилине тикеленүү мүмкүнчүлүгү бар экендиги аныкталды. '
        f'{full_name} {course}-курстун багытында окуган дисциплиналары төмөнкүдөй:',
        styles['TableCell']
    ))
    elements.append(Spacer(1, 12))

    # Таблица с предметами и кредитами
    data = [['№', 'Название предмета', 'Кредиты']]
    total_credits = 0

    for i, ps in enumerate(post.post_subjects.select_related('subject'), start=1):
        data.append([
            Paragraph(str(i), styles['TableCell']),
            Paragraph(ps.subject.name, styles['TableCell']),
            Paragraph(str(ps.credits), styles['TableCell']),
        ])
        total_credits += ps.credits

    table = Table(data, colWidths=[40, 350, 100])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('GRID',       (0, 0), (-1, -1), 1, colors.black),
        ('ALIGN',      (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME',   (0, 0), (-1, -1), 'DejaVuSans'),
        ('FONTSIZE',   (0, 0), (-1, -1), 12),
    ]))
    elements.append(table)

    # Общая сумма кредитов
    elements.append(Spacer(1, 12))
    elements.append(Paragraph(f'<b>Жалпы кредиттердин суммасы:</b> {total_credits}', styles['TableCell']))
    elements.append(Spacer(1, 24))

    # Маршрут согласования
    elements.append(Paragraph('Маршрут согласования (Подписи комиссии):', styles['ProtocolTitle']))
    elements.append(Spacer(1, 12))

    approval_steps = post.approval_steps.select_related('user').all()
    for idx, step in enumerate(approval_steps, start=1):
        status = "✅ Согласовано" if step.is_approved else ("❌ Отклонено" if step.is_approved is False else "⏳ Ожидает")
        reviewed_at = step.reviewed_at.strftime('%d.%m.%Y %H:%M') if step.reviewed_at else "Не проверено"
        full_name = f"{step.user.first_name} {step.user.last_name}"
        position = getattr(step.user, 'position', '')  # если есть поле "position"
        elements.append(Paragraph(
            f"{idx}. {full_name} — {position}<br/>"
            f"Статус: {status}, Время: {reviewed_at}",
            styles['TableCell']
        ))
        elements.append(Spacer(1, 6))

    # Создание документа
    doc.build(elements)
    print(f"PDF для поста {post.id} успешно создан по пути: {file_path}")
    return file_path
