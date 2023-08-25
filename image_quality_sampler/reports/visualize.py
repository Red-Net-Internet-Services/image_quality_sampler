import os
from datetime import datetime
from io import BytesIO

import matplotlib.pyplot as plt
from PIL import Image as PILImage
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    Image,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from image_quality_sampler import config


def generate_charts(data):
    plt.rcParams["figure.figsize"] = (8, 6)

    # Pie chart for Lot vs Sample
    pie_buffer = BytesIO()
    labels = ["Lot Size", "Rejected Images"]
    sizes = [data["Lot"], len(data["Rejected Images"])]
    plt.pie(sizes, labels=labels, autopct="%1.1f%%", startangle=90)
    plt.axis("equal")
    plt.title("Lot Size vs Rejected Images")
    plt.tight_layout()
    plt.savefig(pie_buffer, format="png")
    pie_buffer.seek(0)

    # Rejections vs Lot Size
    bar_buffer = BytesIO()
    plt.figure()
    plt.bar(
        ["Rejections", "Lot Size"], [len(data["Rejected Images"]), data["Lot"]]
    )
    plt.title("Rejections vs Lot Size")
    plt.tight_layout()
    plt.savefig(bar_buffer, format="png")
    bar_buffer.seek(0)

    return pie_buffer, bar_buffer


def generate_pdf(data):
    doc = SimpleDocTemplate(
        "report.pdf",
        pagesize=A4,
        rightMargin=30,
        leftMargin=30,
        topMargin=30,
        bottomMargin=18,
    )
    styles = getSampleStyleSheet()
    font_path = os.path.join(config.FONT_PATH, "DejaVuSans.ttf")
    pdfmetrics.registerFont(TTFont("DejaVuSans", font_path))
    styles["Normal"].fontName = "DejaVuSans"
    styles["BodyText"].fontName = "DejaVuSans"
    styles["Heading1"].fontName = "DejaVuSans"
    styles["Heading2"].fontName = "DejaVuSans"
    styles["Heading3"].fontName = "DejaVuSans"

    story = []

    # Title, Timestamp and Root Folder
    title = Paragraph("Image Quality Sampling Report", styles["Title"])
    timestamp = Paragraph(
        f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        styles["Normal"],
    )
    root_folder = Paragraph(
        f"Root Folder: {data['Batch Name']}", styles["Normal"]
    )
    story.extend([title, Spacer(1, inch), timestamp, root_folder])

    # General Info
    for key, value in data.items():
        if key not in ["Checked Images", "Rejected Images"]:
            p = Paragraph(f"{key}: {value}", styles["BodyText"])
            story.append(p)
    story.append(PageBreak())

    # Tables
    story.append(Paragraph("Πίνακες", styles["Heading2"]))
    story.append(Spacer(0.5, inch))
    story.append(Paragraph("Εικόνες που ελέχθηκαν:", styles["Heading3"]))
    checked_table_data = [["Checked Images"]] + [
        [
            os.path.join(
                os.path.basename(os.path.dirname(img)), os.path.basename(img)
            )
        ]
        for img in data["Checked Images"]
    ]
    checked_table = Table(checked_table_data, colWidths=[6 * inch])
    checked_table.setStyle(
        TableStyle([("GRID", (0, 0), (-1, -1), 1, (0, 0, 0))])
    )
    story.extend([checked_table, PageBreak()])

    story.append(Paragraph("Εικόνες που απορρίφθηκαν:", styles["Heading3"]))
    rejected_table_data = [["Rejected Image", "Reason"]] + [
        [
            os.path.join(
                os.path.basename(os.path.dirname(img)), os.path.basename(img)
            ),
            reason,
        ]
        for img, reason in data["Rejected Images"]
    ]
    rejected_table = Table(rejected_table_data, colWidths=[4 * inch, 2 * inch])
    rejected_table.setStyle(
        TableStyle([("GRID", (0, 0), (-1, -1), 1, (0, 0, 0))])
    )
    story.extend([rejected_table, PageBreak()])

    # Graphs
    pie_buffer, bar_buffer = generate_charts(data)
    story.append(Paragraph("Graphs", styles["Heading2"]))
    story.append(Spacer(1, inch))

    # Adjust pie image size without stretching
    pie_image = PILImage.open(pie_buffer)
    pie_aspect_ratio = pie_image.width / pie_image.height
    pie_width = 6 * inch
    pie_height = pie_width / pie_aspect_ratio
    pie = Image(pie_buffer, width=pie_width, height=pie_height)

    # Adjust bar image size without stretching
    bar_image = PILImage.open(bar_buffer)
    bar_aspect_ratio = bar_image.width / bar_image.height
    bar_width = 6 * inch
    bar_height = bar_width / bar_aspect_ratio
    bar = Image(bar_buffer, width=bar_width, height=bar_height)

    story.extend([pie, Spacer(1, inch), bar, PageBreak()])

    # Placeholder Text and Signature
    lorem_text = "Lorem ipsum dolor sit amet, consectetur adipiscing elit."
    story.append(Paragraph(lorem_text, styles["Normal"]))
    story.append(Spacer(1, inch))
    user1 = Paragraph(
        f"{data['User 1']} Υπογραφή: ___________________________",
        styles["Normal"],
    )
    user2 = Paragraph(
        f"{data['User 2']} Υπογραφή: ___________________________",
        styles["Normal"],
    )
    story.extend([user1, Spacer(1, inch), user2])

    doc.build(story)


def create_report(data):
    generate_pdf(data)
