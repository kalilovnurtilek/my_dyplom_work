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
    protocols_folder = os.path.join(settings.MEDIA_ROOT, 'protocols')
    os.makedirs(protocols_folder, exist_ok=True)

    file_path = os.path.join(protocols_folder, f'post_{post.id}_protocol.pdf')
    doc = SimpleDocTemplate(file_path, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=18)
    elements = []

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='ProtocolTitle', fontName='DejaVuSans', fontSize=12, leading=20, spaceAfter=12, alignment=TA_CENTER))
    styles.add(ParagraphStyle(name='TableCell', fontName='DejaVuSans', fontSize=11, leading=14))

    elements.append(Paragraph('МФТИТ институтунун студенттерин которуу, тикелөө жана окуудан четтетүү боюнча<br/>түзүлгөн аттестациялык комиссиянын отурумунун', styles['ProtocolTitle']))
    elements.append(Paragraph(f'ПРОТОКОЛ № {post.protocol_number or post.id}', styles['ProtocolTitle']))
    elements.append(Spacer(1, 12))

    created_date = post.created.strftime('%d.%m.%Y') if post.created else 'Белгисиз'
    elements.append(Paragraph(f'Протоколдун түзүлгөн күнү: <b>{created_date}</b>', styles['TableCell']))
    elements.append(Spacer(1, 12))

    student_name = post.title
    native_language = getattr(post, 'native_language', 'Белгиленген жок')
    old_course = post.cours.cours if post.cours else 'Белгиленген жок'
    new_course = getattr(post, 'priority_course', post.cours).cours if hasattr(post, 'priority_course') and post.priority_course else old_course

    specialty = post.specialty
    if specialty:
        specialty_info = f'({specialty.code}) {specialty.name} ({specialty.short_name})'
    else:
        specialty_info = 'Белгиленген жок'

    creator = post.owner.get_full_name() or post.owner.username

    elements.append(Paragraph(
        f'Студенттин аты-жөнү: <b>{student_name}</b><br/>'
        f'Туулган тили: <b>{native_language}</b><br/>'
        f'Которулуп жатат: <b>{old_course}-курс</b> -дан <b>{new_course}-курс</b>-ка<br/>'
        f'Адистик (багыт): <b>{specialty_info}</b><br/>'
        f'Протоколду түзгөн: <b>{creator}</b>',
        styles['TableCell']
    ))
    elements.append(Spacer(1, 12))

    elements.append(Paragraph(f'Эмне болгону: {post.content}', styles['TableCell']))
    elements.append(Spacer(1, 18))

    # Айырма предметтер таблицасы
    elements.append(Paragraph('I. Айырма предметтер:', styles['TableCell']))
    diff_data = [['№', 'Предметтин аталышы', 'Кредит']]
    total_diff_credits = 0

    for i, ps in enumerate(post.post_subjects.select_related('subject').all(), 1):
        subject_name = ps.subject.name if ps.subject else 'Белгиленген жок'
        credit = ps.earned_credits or 0
        total_diff_credits += credit
        diff_data.append([str(i), subject_name, str(credit)])

    if len(diff_data) == 1:
        diff_data.append(['-', 'Айырма предметтер табылган жок', '-'])

    diff_table = Table(diff_data, colWidths=[40, 350, 100])
    diff_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), 'DejaVuSans'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
    ]))
    elements.append(diff_table)
    elements.append(Spacer(1, 12))
    elements.append(Paragraph(f'<b>Жалпы кредиттердин суммасы:</b> {total_diff_credits}', styles['TableCell']))
    elements.append(Spacer(1, 18))

    # Таанылган предметтер (эгер бар болсо)
    recognized_subjects = getattr(post, 'recognized_subjects', [])  # Бул тизмени өзүңүз кошуңуз
    if recognized_subjects:
        elements.append(Paragraph('II. Таанылган предметтер:', styles['TableCell']))
        rec_data = [['№', 'Предметтин аталышы', 'Кредиттердин саны']]
        for i, subj in enumerate(recognized_subjects, 1):
            rec_data.append([str(i), subj['name'], str(subj['credits'])])

        rec_table = Table(rec_data, colWidths=[40, 350, 100])
        rec_table.setStyle(diff_table._cellStyles)
        elements.append(rec_table)
        elements.append(Spacer(1, 18))

    # Согласование
    elements.append(Paragraph('Согласование багыты (Комиссиянын колдору):', styles['ProtocolTitle']))
    elements.append(Spacer(1, 12))

    for idx, step in enumerate(post.approval_steps.select_related('user').all(), 1):
        status = '✅ Макул' if step.is_approved else ('❌ Кайтарылды' if step.is_approved is False else '⏳ Күтүлүүдө')
        reviewed_at = step.reviewed_at.strftime('%d.%m.%Y %H:%M') if step.reviewed_at else 'Текшерилген жок'
        full_name = step.user.get_full_name() or f'{step.user.first_name} {step.user.last_name}'
        position = getattr(step.user, 'position', 'Белгиленген эмес')

        elements.append(Paragraph(
            f'{idx}. {full_name} — {position}<br/>Статус: {status}, Текшерүү убактысы: {reviewed_at}',
            styles['TableCell']
        ))
        elements.append(Spacer(1, 6))

    doc.build(elements)
    return file_path
