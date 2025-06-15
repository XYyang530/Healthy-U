from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
import os
import subprocess

def create_pdf_report():
    # Create a new PDF document
    pdf_filename = "example_report.pdf"
    doc = SimpleDocTemplate(pdf_filename, pagesize=letter)
    styles = getSampleStyleSheet()

    # Define content for the report
    report_content = [
    Paragraph("Report Title", styles["Title"]),
    Paragraph("This is a sample report created using ReportLab.", styles["Normal"]),
    # Add more content as needed
    ]

# Add content to the PDF document
    doc.build(report_content)

    return pdf_filename

def display_pdf(filename):
    if os.name == 'nt': # For Windows
        os.startfile(filename)
    elif os.name == 'posix': # For Linux
        subprocess.call(['xdg-open', filename])
    elif os.name == 'darwin': # For macOS
        subprocess.call(['open', filename])

    if __name__ == "__main__":
    # Create PDF report
        pdf_filename = create_pdf_report()

    # Display PDF
    display_pdf(pdf_filename)