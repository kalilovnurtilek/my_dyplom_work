import os
from django.conf import settings
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER

# Шрифттин жолу (fonts папкасын "posts/utils/fonts" ичинде түзүү керек)
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

    # Башкы беттеги текст
    elements.append(Paragraph(
        'МФТИТ институтунун студенттерин которуу, тикелөө жана окуудан четтетүү боюнча<br/>'
        'түзүлгөн аттестациялык комиссиянын отурумунун',
        styles['ProtocolTitle']
    ))

    elements.append(Paragraph(f'ПРОТОКОЛ № {post.protocol_number or post.id}', styles['ProtocolTitle']))

    elements.append(Spacer(1, 12))

    created_date = post.created.strftime('%d.%m.%Y') if post.created else "Түүптөлгөн күнү белгисиз"
    elements.append(Paragraph(f'Протоколдун түзүлгөн күнү: <b>{created_date}</b>', styles['TableCell']))
    elements.append(Spacer(1, 12))

    # Студент жөнүндө маалыматтар
    student_name = post.title or "Белгиленген жок"
    native_language = "Белгиленген жок"  # Моделде жок, эгер керек болсо кошуу керек
    old_course = post.cours.cours if post.cours else "Белгиленген жок"
    # Моделде "new_course" жок, керек болсо кошуу керек, азыр "cours" гана колдонобуз
    new_course = old_course

    speciality_code = post.specialty.code if post.specialty else None
    speciality_full = post.specialty.name if post.specialty else None
    if speciality_code and speciality_full:
        speciality_text = f'({speciality_code}) {speciality_full}'
    else:
        speciality_text = "Белгиленген жок"

    elements.append(Paragraph(
        f'Студент: <b>{student_name}</b><br/>'
        f'Туулган тили: <b>{native_language}</b><br/>'
        f'Которулуп жатат: <b>{old_course}-курс</b>-дан <b>{new_course}-курс</b>-ка<br/>'
        f'Адистик (багыт): <b>{speciality_text}</b>',
        styles['TableCell']
    ))
    elements.append(Spacer(1, 12))

    # Комиссия жана дисциплиналар жөнүндө маалымат
    elements.append(Paragraph(
        f'I. Комиссиялык аттестациялоо негизинде <b>{student_name}</b> '
        f'институттун окуу бөлүмүнүн «{speciality_text}» багытынын профилине тикеленүү мүмкүнчүлүгү бар экендиги аныкталды. '
        f'{student_name} {new_course}-курс багытында окуган дисциплиналардын айырмалары төмөнкүлөр:',
        styles['TableCell']
    ))
    elements.append(Spacer(1, 12))

    # Предметтер жана кредиттер таблицасы
    data = [['№', 'Предметтин аталышы', 'Кредиттердин саны']]
    total_credits = 0

    post_subjects = post.post_subjects.select_related('subject').all()
    if not post_subjects:
        data.append(['-', 'Предметтер табылган жок', '-'])
    else:
        for i, ps in enumerate(post_subjects, start=1):
            subj_name = ps.subject.name if ps.subject else "Белгиленген жок"
            credits = ps.credits if ps.credits else 0
            data.append([
                Paragraph(str(i), styles['TableCell']),
                Paragraph(subj_name, styles['TableCell']),
                Paragraph(str(credits), styles['TableCell']),
            ])
            total_credits += credits

    table = Table(data, colWidths=[40, 350, 100])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('GRID',       (0, 0), (-1, -1), 1, colors.black),
        ('ALIGN',      (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME',   (0, 0), (-1, -1), 'DejaVuSans'),
        ('FONTSIZE',   (0, 0), (-1, -1), 11),
    ]))
    elements.append(table)

    elements.append(Spacer(1, 12))
    elements.append(Paragraph(f'<b>Жалпы кредиттердин суммасы:</b> {total_credits}', styles['TableCell']))

    # Кредиттердин саны 30дон ашса эскертүү
    if total_credits > 30:
        elements.append(Spacer(1, 12))
        elements.append(Paragraph(
            '<font color="red"><b>Кредиттердин жалпы саны 30дон ашкандыктан, которулуу мүмкүн эмес.</b></font>',
            styles['TableCell']
        ))

    elements.append(Spacer(1, 24))

    # Согласование багыты
    elements.append(Paragraph('Согласование багыты (Комиссиянын колдору):', styles['ProtocolTitle']))
    elements.append(Spacer(1, 12))

    approval_steps = post.approval_steps.select_related('user').all()
    if not approval_steps:
        elements.append(Paragraph('Согласование этаптары табылган жок.', styles['TableCell']))
    else:
        for idx, step in enumerate(approval_steps, start=1):
            status = "✅ Макул" if step.is_approved else ("❌ Кайтарылды" if step.is_approved is False else "⏳ Күтүлүүдө")
            reviewed_at = step.reviewed_at.strftime('%d.%m.%Y %H:%M') if step.reviewed_at else "Текшерилген жок"
            full_name = step.user.get_full_name() if hasattr(step.user, 'get_full_name') else f"{step.user.first_name} {step.user.last_name}"
            position = getattr(step.user, 'position', '')
            elements.append(Paragraph(
                f"{idx}. {full_name} — {position}<br/>"
                f"Статус: {status}, Текшерүү убактысы: {reviewed_at}",
                styles['TableCell']
            ))
            elements.append(Spacer(1, 6))

    doc.build(elements)
    print(f"Пост №{post.id} үчүн PDF протокол ийгиликтүү түзүлдү: {file_path}")
    return file_path
