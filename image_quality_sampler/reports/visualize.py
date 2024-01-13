import os
from datetime import datetime

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)
from PyQt5.QtWidgets import QFileDialog
from image_quality_sampler import config
from reportlab.lib.pagesizes import landscape


def generate_pdf(data, file_path):
    doc = SimpleDocTemplate(
        file_path,
        pagesize=A4,
        rightMargin=30,
        leftMargin=30,
        topMargin=30,
        bottomMargin=18,
    )
    styles = getSampleStyleSheet()
    font_path = os.path.join(config.FONT_PATH, "DejaVuSans.ttf")
    pdfmetrics.registerFont(TTFont("DejaVuSans", font_path))
    # Set DejaVuSans font for all styles
    # Set DejaVuSans font for each style in the stylesheet
    for style_name in styles.byName:
        styles[style_name].fontName = "DejaVuSans"

    story = []

    # Title, Timestamp and Root Folder
    title = Paragraph("Αναφορά Ποιοτικού Ελέγχου", styles["Title"])
    timestamp = Paragraph(
        f"ΗΜΕΡΟΜΗΝΙΑ ΕΛΕΓΧΟΥ: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        styles["Normal"],
    )
    story.extend([title, Spacer(1, inch), timestamp])

    # General Info
    for key, value in data.items():
        if key not in ["Εικόνες Που Ελέχθηκαν", "Rejected Images", "Status", "Subfolders"]:
            p = Paragraph(f"{key}: {value}", styles["BodyText"])
            story.append(p)
    story.append(PageBreak())

    # Tables
    story.append(Paragraph("Πίνακες", styles["Heading2"]))
    story.append(Spacer(0.5, inch))

    # Add a Table for Subfolders
    if "Subfolders" in data:
        story.append(Paragraph("Τεκμήρια:", styles["Heading3"]))
        subfolder_table_data = [[subfolder] for subfolder in data["Subfolders"]]
        subfolder_table = Table(subfolder_table_data, colWidths=[6 * inch])  # Adjust column width as needed
        subfolder_table.setStyle(TableStyle([
            ("GRID", (0, 0), (-1, -1), 1, (0, 0, 0)),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("WORDWRAP", (0, 0), (-1, -1), "LTR"),  # Enable word wrapping
        ]))
        story.extend([subfolder_table, PageBreak()])

    story.append(Paragraph("Εικόνες που ελέχθηκαν:", styles["Heading3"]))
    checked_table_data = [
        [
            Paragraph(os.path.join(
                os.path.basename(os.path.dirname(img)), os.path.basename(img)
            ), styles["BodyText"])
        ]
        for img in data["Εικόνες Που Ελέχθηκαν"]
    ]
    checked_table = Table(checked_table_data, colWidths=[6 * inch])
    checked_table.setStyle(TableStyle([
            ("GRID", (0, 0), (-1, -1), 1, (0, 0, 0)),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("WORDWRAP", (0, 0), (-1, -1), "LTR"),  # Enable word wrapping
        ]))
    story.extend([checked_table, PageBreak()])

    story.append(Paragraph("Εικόνες που απορρίφθηκαν:", styles["Heading3"]))
    rejected_table_data = [
        [
            Paragraph(os.path.join(
                os.path.basename(os.path.dirname(img)), os.path.basename(img)
            ),
                styles["BodyText"]),
            Paragraph(reason, styles["BodyText"]),
        ]
        for img, reason in data["Rejected Images"]
    ]
    rejected_table = Table(rejected_table_data, colWidths=[4 * inch, 2 * inch])
    rejected_table.setStyle(TableStyle([
            ("GRID", (0, 0), (-1, -1), 1, (0, 0, 0)),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("WORDWRAP", (0, 0), (-1, -1), "LTR"),  # Enable word wrapping
        ]))
    story.extend([rejected_table, PageBreak()])

    # Placeholder Text and Signature
    text1 = "Η ποιότητα των προϊόντων σάρωσης της παρούσας Παρτίδας ελέγχθηκε δειγματοληπτικά από αρμόδια ομάδα δειγματοληπτικού ελέγχου µέσω προκαθορισμένων ελέγχων ποιότητας και σύμφωνα µε τις απαιτήσεις του Έργου Ψηφιοποίησης αρχείου Υποθηκοφυλακείων του Ελληνικού Κτηματολογίου.Οι δειγματοληπτικοί έλεγχοι των εγγράφων που σαρώθηκαν πραγματοποιήθηκαν µε οπτική αντιπαραβολή των πρωτότυπων εγγράφων και των σε ηλεκτρονική μορφή σαρωμένων εγγράφων. ∆ειγματοληπτικά ελέγχθηκε και η σχετική τεκμηρίωση των εγγράφων (µεταδεδοµένα) µε ανάλογο τρόπο."
    text2 = "Αποτελέσματα ελέγχου Παρτίδας: "
    text3 = "Κατόπιν διεκπεραίωσης δειγματοληπτικού ελέγχου, τα αποτελέσματα είναι τα κάτωθι:"
    result = Paragraph(f"{data['Status']}")
    
    story.append(Paragraph(text1, styles["Normal"]))
    story.append(Spacer(1, inch))
    story.append(Paragraph(text2, styles["Normal"]))
    story.append(Spacer(1, inch))
    story.append(Paragraph(text3, styles["Normal"]))
    story.append(Spacer(1, inch))
    story.append(result)
    story.append(Spacer(1, inch))
    
    user1 = Paragraph(
        f"{data['Χρήστης Ανάδοχου']} Υπογραφή: ___________________________",
        styles["Normal"],
    )
    user2 = Paragraph(
        f"{data['Χρήστης Φορέα']} Υπογραφή: ___________________________",
        styles["Normal"],
    )
    story.extend([user1, Spacer(1, inch), user2])

    doc.build(story)


def get_save_file_path(parent):
    options = QFileDialog.Options()
    # options |= QFileDialog.DontUseNativeDialog
    file_name, _ = QFileDialog.getSaveFileName(parent,
                                               "Save Report",
                                               "",
                                               "PDF Files (*.pdf)",
                                               options=options)
    return file_name


def create_report(data, parent=None):
    save_path = get_save_file_path(parent)
    if save_path:
        generate_pdf(data, save_path)
    else:
        print("Save operation cancelled.")
