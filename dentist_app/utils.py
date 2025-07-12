# utils.py
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import landscape, A4
from reportlab.lib.units import mm
import os
from django.conf import settings
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import stringWidth

def split_text_words(text, max_width, font_name, font_size):
    words = text.split()
    lines = []
    current_line = ""

    for word in words:
        test_line = current_line + (" " if current_line else "") + word
        test_line_width = stringWidth(test_line, font_name, font_size)
        if test_line_width <= max_width:
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line)
            current_line = word
    if current_line:
        lines.append(current_line)
    return lines

def generate_invoice_pdf(appointment):
    file_name = f"qaime_{appointment.patient.fin_code}_{appointment.appointment_date.strftime('%Y%m%d')}.pdf"
    pdf_dir = os.path.join(settings.MEDIA_ROOT, 'pdf')
    os.makedirs(pdf_dir, exist_ok=True)
    file_path = os.path.join(pdf_dir, file_name)

    font_regular_path = os.path.join(settings.BASE_DIR, 'static', 'fonts', 'DejaVuSans.ttf')
    font_bold_path = os.path.join(settings.BASE_DIR, 'static', 'fonts', 'DejaVuSans-Bold.ttf')

    pdfmetrics.registerFont(TTFont('DejaVuSans', font_regular_path))
    pdfmetrics.registerFont(TTFont('DejaVuSans-Bold', font_bold_path))

    c = canvas.Canvas(file_path, pagesize=landscape(A4))
    width, height = landscape(A4)

    section_width = width / 3
    margin = 10 * mm
    text_max_width = section_width - 2 * margin - 60 * mm

    logo_path = os.path.join(settings.BASE_DIR, 'static', 'img', 'logo.png')

    for i in range(3):
        left = i * section_width + margin
        top = height - 40 * mm

        # Başlıq
        c.setFont('DejaVuSans-Bold', 28)
        c.drawString(left, top + 5 * mm, "MedXDent")

        label_x = left
        value_x = left + 30 * mm

        # Etiketlər
        c.setFont('DejaVuSans-Bold', 16)
        c.drawString(label_x, top - 30 * mm, "Həkim:")
        c.drawString(label_x, top - 45 * mm, "Xidmət:")
        c.drawString(label_x, top - 80 * mm, "Pasiyent:")
        c.drawString(label_x, top - 95 * mm, "Tarix:")
        c.drawString(label_x, top - 110 * mm, "Məbləğ:")

        # Məlumatlar
        c.setFont('DejaVuSans', 16)
        c.drawString(value_x, top - 30 * mm, str(appointment.doctor))
        c.drawString(value_x, top - 80 * mm, str(appointment.patient))

        service_lines = split_text_words(appointment.service.name, text_max_width, 'DejaVuSans', 14)
        y_pos = top - 45 * mm
        for idx, line in enumerate(service_lines):
            c.drawString(value_x, y_pos - idx * 15, line)

        date_str = appointment.appointment_date.strftime('%d.%m.%Y')
        time_str = appointment.appointment_time.strftime('%H:%M') if hasattr(appointment, 'appointment_time') and appointment.appointment_time else ''
        datetime_str = f"{date_str} {time_str}".strip()
        c.drawString(value_x, top - 95 * mm, datetime_str)

        c.drawString(value_x, top - 110 * mm, f"{appointment.paid_amount} AZN")

        c.setFont('DejaVuSans-Bold', 16)
        c.drawString(left, 35 * mm, "İmza:")

        # 🔽 Araya qara xətt (yalnız 1-ci və 2-ci nüsxədən sonra)
        if i < 2:
            x_cut = (i + 1) * section_width
            c.setStrokeColorRGB(0, 0, 0)  # qara rəng
            c.setLineWidth(1)
            c.line(x_cut, 15 * mm, x_cut, height - 15 * mm)

    c.showPage()
    c.save()

    return f'pdf/{file_name}'
