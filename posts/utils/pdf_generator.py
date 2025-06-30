import os
import qrcode
from io import BytesIO
from django.conf import settings
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

# Шрифттин жолун көрсөтөбүз
fonts_folder = os.path.join(settings.BASE_DIR, 'posts', 'utils', 'fonts')
dejavu_path = os.path.join(fonts_folder, 'DejaVuSans.ttf')

# Шрифтти каттайбыз
pdfmetrics.registerFont(TTFont('DejaVuSans', dejavu_path))

def generate_post_pdf(post):
    # Протоколдор сакталуучу папка
    protocols_folder = os.path.join(settings.MEDIA_ROOT, 'protocols')
    os.makedirs(protocols_folder, exist_ok=True)

    # PDF файлынын жолу
    file_path = os.path.join(protocols_folder, f'post_{post.id}_protocol.pdf')
    doc = SimpleDocTemplate(file_path, pagesize=A4)
    elements = []

    # Стильдер
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name='CustomTitle',
        fontName='DejaVuSans',
        fontSize=16,
        leading=20,
        spaceAfter=12,
        alignment=1  # ортого чыгаруу
    ))
    styles.add(ParagraphStyle(
        name='NormalText',
        fontName='DejaVuSans',
        fontSize=12,
        leading=14,
    ))

    # Протокол номери (жогору жагына)
    elements.append(Paragraph("Протокол № ___________", styles['CustomTitle']))
    elements.append(Spacer(1, 24))

    # Студенттин аты-жөнү (бул жерде post.title)
    elements.append(Paragraph(f'Студент: {post.title}', styles['NormalText']))
    elements.append(Spacer(1, 12))

    # Ким түздү (owner)
    owner_full_name = f"{post.owner.first_name} {post.owner.last_name}" if post.owner else "Көрсөтүлгөн эмес"
    elements.append(Paragraph(f'Түзгөн кызматкер: {owner_full_name}', styles['NormalText']))

    # Түзүлгөн дата
    created_str = post.created.strftime('%Y-%m-%d %H:%M:%S') if post.created else "Көрсөтүлгөн эмес"
    elements.append(Paragraph(f'Түзүлгөн датасы: {created_str}', styles['NormalText']))

    # Адистик
    specialty_name = post.specialty.name if post.specialty else "Көрсөтүлгөн эмес"
    elements.append(Paragraph(f'Кайсыл адистикке которулу жатат: {specialty_name}', styles['NormalText']))

    # Статус
    elements.append(Paragraph(f'Статусу: {post.get_status_display()}', styles['NormalText']))
    elements.append(Spacer(1, 12))

    # Сабактар таблицасы
    elements.append(Paragraph("Сабактар жана кредиттердин айырмасы:", styles['CustomTitle']))
    data = [['№', 'Сабактын аталышы', 'Кредиттер']]
    for i, ps in enumerate(post.post_subjects.select_related('subject'), start=1):
        data.append([
            Paragraph(str(i), styles['NormalText']),
            Paragraph(ps.subject.name, styles['NormalText']),
            Paragraph(str(ps.credits), styles['NormalText']),
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

    # Макулдашуу маршруту
    elements.append(Spacer(1, 24))
    elements.append(Paragraph('Макулдашуу этаптары:', styles['CustomTitle']))
    elements.append(Spacer(1, 12))

    approval_steps = post.approval_steps.all()

    for idx, step in enumerate(approval_steps, start=1):
        status = "Макулдашылды" if step.is_approved else "Макулдашылган жок"
        reviewed_at = step.reviewed_at.strftime('%Y-%m-%d %H:%M:%S') if step.reviewed_at else "Карала элек"
        approver_name = f"{step.user.first_name} {step.user.last_name}" if step.user else "Белгисиз"
        elements.append(Paragraph(
            f"{idx}. {approver_name} - {status} ({reviewed_at})",
            styles['NormalText']
        ))

    # QR код кошуу (мисалы: протоколдун ID же URL)
    qr_data = f"https://example.com/post/{post.id}/"  # Мына ушул жерге өз URL'иңди киргиз
    qr_img = qrcode.make(qr_data)
    buffer = BytesIO()
    qr_img.save(buffer, format='PNG')
    buffer.seek(0)
    qr_reportlab_image = Image(buffer, 80, 80)  # 80x80 пиксель өлчөмүндө

    # QR кодду документтин ылдыйкы оң бурчуна чыгарабыз
    elements.append(Spacer(1, 50))
    elements.append(Paragraph(" ", styles['NormalText']))  # Бош орун
    elements.append(qr_reportlab_image)

    # PDF түзөбүз
    doc.build(elements)
    print(f"PDF {post.id} ийгиликтүү түзүлдү: {file_path}")
    return file_path
