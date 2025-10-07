from models import GeneralInfo
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from reportlab.lib import colors
from reportlab.graphics.barcode import qr
from reportlab.graphics.shapes import Drawing
from reportlab.graphics import renderPDF
import arabic_reshaper
from bidi.algorithm import get_display
import os
from datetime import datetime

def header(canvas, doc, info, class_name, semester):
    canvas.setFont("Arabic-Bold", 12)

    directorate = info.directorate if info else "غير محدد"
    institution = info.institution if info else "غير محدد"
    subject = info.subject if info else "غير محدد"
    teacher = info.teacher if info else "غير محدد"

    # المديرية
    text = get_display(arabic_reshaper.reshape(f"مديرية التربية لولاية: {directorate}"))
    canvas.drawRightString(530, 800, text)

    # المؤسسة
    text = get_display(arabic_reshaper.reshape(f"المؤسسة: {institution}"))
    canvas.drawCentredString(120, 800, text)

    # المادة + الأستاذ
    text = get_display(arabic_reshaper.reshape(f"المادة: {subject}"))
    canvas.drawString(460, 780, text)
    text = get_display(arabic_reshaper.reshape(f"الأستاذ: {teacher}"))
    canvas.drawString(110, 780, text)

    # الفصل + القسم
    text = get_display(arabic_reshaper.reshape(f"{semester}"))
    canvas.drawString(480, 760, text)
    text = get_display(arabic_reshaper.reshape(f"القسم: {class_name}"))
    canvas.drawString(145, 760, text)

def footer(canvas, doc, info, class_name, semester, class_average):
    canvas.saveState()

    institution = info.institution if info else "غير محدد"

    # النص الذي نريد تشفيره داخل QR
    qr_text = f"{institution} | {class_name} | {semester} |{class_average}"

    # إنشاء QR
    qr_code = qr.QrCodeWidget(qr_text)
    bounds = qr_code.getBounds()
    size = 60  # حجم QR
    width = bounds[2] - bounds[0]
    height = bounds[3] - bounds[1]
    d = size / max(width, height)

    drawing = Drawing(size, size, transform=[d, 0, 0, d, 0, 0])
    drawing.add(qr_code)

    # مكان QR أسفل الصفحة
    x, y = 450, 20
    renderPDF.draw(drawing, canvas, x, y)

    # خط أصفر تحت QR
    canvas.setStrokeColorRGB(1, 1, 0)
    canvas.setLineWidth(2)
    canvas.line(40, y - 5, A4[0] - 40, y - 5)

    # Page number
    page_num = canvas.getPageNumber()
    page_text = get_display(arabic_reshaper.reshape(f"الصفحة {page_num}"))
    canvas.setFont("Arabic", 10)
    canvas.drawString(40, 20, page_text)

    canvas.restoreState()

def export_to_pdf(students, class_name, semester, num_students, class_average, success_percentage, info, filename="report.pdf"):
    # إعداد ملف PDF
    doc = SimpleDocTemplate(
        filename,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=80,
        bottomMargin=60
    )
    story = []

    # تسجيل الخطوط العربية
    font_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "arial.ttf"))
    pdfmetrics.registerFont(TTFont('Arabic', font_path))
    font_path_bold = os.path.abspath(os.path.join(os.path.dirname(__file__), "arialbd.ttf"))
    pdfmetrics.registerFont(TTFont('Arabic-Bold', font_path_bold))

    # الأنماط
    styles = getSampleStyleSheet()
    style_right = ParagraphStyle(name='style_right', parent=styles['Normal'], fontName='Arabic', alignment=TA_RIGHT)
    style_right_bold = ParagraphStyle(name='style_right_bold', parent=styles['Normal'], fontName='Arabic-Bold', alignment=TA_RIGHT)
    style_left_bold = ParagraphStyle(name='style_left_bold', parent=styles['Normal'], fontName='Arabic-Bold', alignment=TA_LEFT)
    style_center = ParagraphStyle(name='style_center', parent=styles['Normal'], fontName='Arabic', alignment=TA_CENTER)
    style_center_bold = ParagraphStyle(name='style_center_bold', parent=styles['Normal'], fontName='Arabic-Bold', alignment=TA_CENTER, fontSize=16)

    # ------------------------
    # محتوى التقرير
    # ------------------------

    story.append(Spacer(1, 6))
    story.append(Paragraph(get_display(arabic_reshaper.reshape("تقرير نتائج التلاميذ")), style_center_bold))
    story.append(Spacer(1, 12))

    header_table = [
        'الملاحظات', 'المعدل', 'الاختبار', 'م التقويم', 'الفرض', 'التقويم', 'الاسم',
    ]
    header_table = [Paragraph(get_display(arabic_reshaper.reshape(cell)), style_center) for cell in header_table]
    data = [header_table]

    for s in students:
        if s.grades_for_semester:
            for g in s.grades_for_semester:
                row = [
                    Paragraph(get_display(arabic_reshaper.reshape(str(g.note))), style_center),
                    Paragraph(get_display(arabic_reshaper.reshape(str(g.average))), style_center),
                    Paragraph(get_display(arabic_reshaper.reshape(str(g.exam))), style_center),
                    Paragraph(get_display(arabic_reshaper.reshape(str(g.avg_controle))), style_center),
                    Paragraph(get_display(arabic_reshaper.reshape(str(g.test))), style_center),
                    Paragraph(get_display(arabic_reshaper.reshape(str(g.assessment))), style_center),
                    Paragraph(get_display(arabic_reshaper.reshape(str(s.fullname))), style_right),
                ]
                data.append(row)
        else:
            row = [
                Paragraph(get_display(arabic_reshaper.reshape("")), style_center),
                Paragraph(get_display(arabic_reshaper.reshape("")), style_center),
                Paragraph(get_display(arabic_reshaper.reshape("")), style_center),
                Paragraph(get_display(arabic_reshaper.reshape("")), style_center),
                Paragraph(get_display(arabic_reshaper.reshape("")), style_center),
                Paragraph(get_display(arabic_reshaper.reshape("")), style_center),
                Paragraph(get_display(arabic_reshaper.reshape(str(s.fullname))), style_right),
            ]
            data.append(row)

    table = Table(data, colWidths=[120, 50, 50, 50, 50, 50, 90])
    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('ALIGN', (6, 1), (6, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Arabic-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ])
    table.setStyle(style)
    story.append(table)
    story.append(Spacer(1, 18))

    success_percentage_text = f"نسبة النجاح: {success_percentage:.2f} %"
    class_average_text = f"معدل القسم: {class_average:.2f}"
    num_students_text = f"عدد التلاميذ: {num_students}"

    p_success = Paragraph(get_display(arabic_reshaper.reshape(success_percentage_text)), style_left_bold)
    p_average = Paragraph(get_display(arabic_reshaper.reshape(class_average_text)), style_center)
    p_num = Paragraph(get_display(arabic_reshaper.reshape(num_students_text)), style_right_bold)

    stats_table = Table([[p_success, p_average, p_num]], colWidths=[150, 230, 100])
    stats_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, 0), 'RIGHT'),
        ('ALIGN', (1, 0), (1, 0), 'CENTER'),
        ('ALIGN', (2, 0), (2, 0), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 0), (-1, -1), 'Arabic-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 14),
        ('LINEABOVE', (0, 0), (-1, 0), 1.5, colors.black),
    ]))
    story.append(stats_table)

    story.append(Spacer(1, 24))
    story.append(Paragraph(get_display(arabic_reshaper.reshape(f"تاريخ الطباعة: {datetime.today().strftime('%Y-%m-%d')}")), style_left_bold))

    # ------------------------
    # بناء PDF
    # ------------------------
    doc.build(
        story,
        onFirstPage=lambda c, d: (header(c, d, info, class_name, semester), footer(c, d, info, class_name, semester, class_average)),
        onLaterPages=lambda c, d: (header(c, d, info, class_name, semester), footer(c, d, info, class_name, semester, class_average))
    )