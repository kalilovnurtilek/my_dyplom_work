import os
from django.conf import settings
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

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

    # Стиль
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

    # Заголовок протокола
    elements.append(Paragraph(f'Протокол по заявлению: {post.title}', styles['ProtocolTitle']))
    elements.append(Spacer(1, 12))

    # Добавляем таблицу с предметами и кредитами
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

    # Добавляем маршрут согласования
    elements.append(Spacer(1, 24))
    elements.append(Paragraph('Маршрут согласования:', styles['ProtocolTitle']))
    elements.append(Spacer(1, 12))

    approval_steps = post.approval_steps.all()  # Список всех шагов согласования для поста

    # Формируем список участников согласования
    approver_names = []
    for idx, step in enumerate(approval_steps, start=1):
        status = "Согласовано" if step.is_approved else "Не согласовано"
        reviewed_at = step.reviewed_at.strftime('%Y-%m-%d %H:%M:%S') if step.reviewed_at else "Не проверено"
        
        # Вместо email выводим имя и фамилию
        approver_names.append(f"{idx}. {step.user.first_name} {step.user.last_name} - {status} ( {reviewed_at})")

    # Добавляем в PDF
    for approver in approver_names:
        elements.append(Paragraph(approver, styles['TableCell']))

    # Создание документа
    doc.build(elements)
    print(f"PDF для поста {post.id} успешно создан по пути: {file_path}")  # Добавляем вывод в консоль
    return file_path
