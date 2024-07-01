from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from django.conf import settings
import os

def generate_certificate(student, course):
    styles = getSampleStyleSheet()
    
    # Custom styles
    certificate_style = ParagraphStyle(
        name='CertificateStyle',
        parent=styles['BodyText'],
        alignment=1,  # Center alignment
        fontSize=14,
        textColor=colors.HexColor('#333333')
    )

    title_style = ParagraphStyle(
        name='TitleStyle',
        parent=styles['Heading1'],
        alignment=1,
        fontSize=36,
        textColor=colors.HexColor('#333333'),
        spaceAfter=20
    )

    subtitle_style = ParagraphStyle(
        name='SubtitleStyle',
        parent=styles['Heading2'],
        alignment=1,
        fontSize=24,
        textColor=colors.HexColor('#666666'),
        spaceAfter=20
    )

    name_style = ParagraphStyle(
        name='NameStyle',
        parent=styles['Heading2'],
        alignment=1,
        fontSize=28,
        textColor=colors.HexColor('#000000'),
        spaceAfter=20
    )

    filename = f'{student.user.username}_{course.title}.pdf'
    file_path = os.path.join(settings.MEDIA_ROOT, 'certificates', filename)

    doc = SimpleDocTemplate(file_path, pagesize=letter)

    elements = []

    # Background Image
    bg_image_path = os.path.join(settings.MEDIA_ROOT, 'images', 'certificate_bg.png')
    c = canvas.Canvas(file_path, pagesize=letter)
    c.drawImage(bg_image_path, 0, 0, width=8.5*inch, height=11*inch)
    c.save()

    # Title
    title = Paragraph("CERTIFICATE OF ACHIEVEMENT", title_style)
    elements.append(Spacer(1, 1*inch))
    elements.append(title)

    # Subtitle
    subtitle = Paragraph("This certificate is presented to", subtitle_style)
    elements.append(Spacer(1, 0.5*inch))
    elements.append(subtitle)

    # Student's name
    student_name = Paragraph(student.user.username, name_style)
    elements.append(Spacer(1, 0.2*inch))
    elements.append(student_name)

    # Description
    description = Paragraph(
        "For outstanding performance and dedication in completing the course requirements.",
        certificate_style
    )
    elements.append(Spacer(1, 0.5*inch))
    elements.append(description)

    # Date
    date = Paragraph(f"Date: {course.date_issued.strftime('%d %B %Y')}", certificate_style)
    elements.append(Spacer(1, 0.5*inch))
    elements.append(date)

    # Signature
    signature = Paragraph("SIGNATURE", certificate_style)
    elements.append(Spacer(1, 1*inch))
    elements.append(signature)

    # Signer's name
    signer_name = Paragraph("Edulearn", certificate_style)
    elements.append(Spacer(1, 0.2*inch))
    elements.append(signer_name)

    doc.build(elements)

    return file_path
