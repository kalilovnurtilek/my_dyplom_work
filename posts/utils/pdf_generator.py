import os
from django.conf import settings
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
)
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER


# Шрифтти каттоо
fonts_folder = os.path.join(settings.BASE_DIR, 'posts', 'utils', 'fonts')
dejavu_path = os.path.join(fonts_folder, 'DejaVuSans.ttf')
pdfmetrics.registerFont(TTFont('DejaVuSans', dejavu_path))


def generate_post_pdf(post):
    # Создаем папку для протоколов, если нет
    protocols_folder = os.path.join(settings.MEDIA_ROOT, 'protocols')
    os.makedirs(protocols_folder, exist_ok=True)

    # Путь к файлу
    file_path = os.path.join(protocols_folder, f'post_{post.id}_protocol.pdf')
    doc = SimpleDocTemplate(
        file_path,
        pagesize=A4,
        rightMargin=30,
        leftMargin=30,
        topMargin=30,
        bottomMargin=18
    )
    elements = []

    # Стили
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name='ProtocolTitle',
        fontName='DejaVuSans',
        fontSize=12,
        leading=20,
        spaceAfter=12,
        alignment=TA_CENTER,
    ))
    styles.add(ParagraphStyle(
        name='TableCell',
        fontName='DejaVuSans',
        fontSize=11,
        leading=14,
    ))

    # Заголовок протокола
    elements.append(Paragraph(
        'МФТИТ институтунун студенттерин которуу, тикелөө жана окуудан четтетүү боюнча<br/>'
        'түзүлгөн аттестациялык комиссиянын отурумунун',
        styles['ProtocolTitle']
    ))
    elements.append(Paragraph(
        f'ПРОТОКОЛ № {post.protocol_number or post.id}',
        styles['ProtocolTitle']
    ))
    elements.append(Spacer(1, 12))

    # Дата создания
    created_date = post.created.strftime('%d.%m.%Y') if post.created else 'Түзүлгөн күнү белгисиз'
    elements.append(Paragraph(
        f'Протоколдун түзүлгөн күнү: <b>{created_date}</b>',
        styles['TableCell']
    ))
    elements.append(Spacer(1, 12))

    # Информация о студенте
    student_name = post.owner.get_full_name() or post.owner.username
    native_language = getattr(post, 'native_language', 'Белгиленген жок')
    old_course = post.cours.cours if post.cours else 'Белгиленген жок'
    # Если есть поле priority_course, замените post.priority_course
    new_course = old_course
    
    if hasattr(post, 'priority_course') and post.priority_course:
        new_course = post.priority_course.cours

    if post.specialty:
        speciality_text = f"({post.specialty.code}) {post.specialty.name}"
    else:
        speciality_text = 'Белгиленген жок'

    elements.append(Paragraph(
        f'Sтудент: <b>{student_name}</b><br/>'
        f'Туулган тили: <b>{native_language}</b><br/>'
        f'Которулуп жатат: <b>{old_course}-курс</b> -дан <b>{new_course}-курс</b>-ка<br/>'
        f'Адистик (багыт): <b>{speciality_text}</b>',
        styles['TableCell']
    ))
    elements.append(Spacer(1, 12))

    # Решение комиссии
    elements.append(Paragraph(
        f'I. Комиссиялык аттестациялоо негизинде <b>{student_name}</b> '
        f'институттун окуу бөлүмүнүн «{speciality_text}» багытынын профилине тикеленүү мүмкүнчүлүгү бар экендиги аныкталды. '
        f'{student_name} {new_course}-курс багытында окуган дисциплиналардын айырмалары төмөнкүлөр:',
        styles['TableCell']
    ))
    elements.append(Spacer(1, 12))

    # Таблица предметов и кредитов
    data = [['№', 'Предметтин аталышы', 'Кредиттердин саны']]
    total_credits = 0
    post_subjects = post.post_subjects.select_related('subject').all()

    if not post_subjects:
        data.append(['-', 'Предметтер табылган жок', '-'])
    else:
        for i, ps in enumerate(post_subjects, start=1):
            subj_name = ps.subject.name if ps.subject else 'Белгиленген жок'
            credits = ps.earned_credits or 0
            total_credits += credits
            data.append([str(i), subj_name, str(credits)])

    table = Table(data, colWidths=[40, 350, 100])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), 'DejaVuSans'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 12))
    elements.append(Paragraph(
        f'<b>Жалпы кредиттердин суммасы:</b> {total_credits}',
        styles['TableCell']
    ))

    if total_credits > 30:
        elements.append(Spacer(1, 12))
        elements.append(Paragraph(
            '<font color="red"><b>Кредиттердин жалпы саны 30дон ашкандыктан, которулуу мүмкүн эмес.</b></font>',
            styles['TableCell']
        ))

    elements.append(Spacer(1, 24))

    # Подписи согласующих
    elements.append(Paragraph('Согласование багыты (Комиссиянын колдору):', styles['ProtocolTitle']))
    elements.append(Spacer(1, 12))
    approval_steps = post.approval_steps.select_related('user').all()

    if not approval_steps:
        elements.append(Paragraph('Согласование этаптары табылган жок.', styles['TableCell']))
    else:
        for idx, step in enumerate(approval_steps, start=1):
            status = '✅ Макул' if step.is_approved else ('❌ Кайтарылды' if step.is_approved is False else '⏳ Күтүлүүдө')
            reviewed_at = step.reviewed_at.strftime('%d.%m.%Y %H:%M') if step.reviewed_at else 'Текшерилген жок'
            full_name = step.user.get_full_name() if hasattr(step.user, 'get_full_name') else f'{step.user.first_name} {step.user.last_name}'
            position = getattr(step.user, 'position', 'Белгиленген эмес')
            elements.append(Paragraph(
                f"{idx}. {full_name} — {position}<br/>Статус: {status}, Текшерүү убактысы: {reviewed_at}",
                styles['TableCell']
            ))
            elements.append(Spacer(1, 6))

    # Генерация PDF
    doc.build(elements)
    return file_path
