import os
from fpdf import FPDF
from datetime import datetime
import pandas as pd

def generate_pdf(data):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.set_fill_color(30, 30, 30)  # dark header
    pdf.set_text_color(0, 255, 0)
    pdf.cell(200, 10, txt="🌿 GHG Emission Prediction Report", ln=True, align='C')

    pdf.set_text_color(255, 255, 255)
    pdf.set_fill_color(60, 60, 60)
    pdf.set_font("Arial", size=11)

    pdf.ln(10)
    for key, value in data.items():
        pdf.cell(60, 10, f"{key.capitalize()}:", border=0)
        pdf.cell(100, 10, str(value), ln=True)

    pdf.set_font("Arial", size=10)
    pdf.set_text_color(180, 180, 180)
    pdf.ln(5)
    pdf.cell(0, 10, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True)

    output_dir = "generated_pdfs"
    os.makedirs(output_dir, exist_ok=True)
    filename = os.path.join(output_dir, f"report_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf")
    pdf.output(filename)

    return filename


def generate_history_pdf(df):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.set_fill_color(30, 30, 30)
    pdf.set_text_color(0, 255, 255)
    pdf.cell(200, 10, txt="📊 GHG Emission History Report", ln=True, align='C')

    pdf.set_text_color(0, 0, 0)
    pdf.set_fill_color(220, 220, 220)
    pdf.set_font("Arial", size=10)

    pdf.ln(10)

    cols = ["Industry", "Substance", "Unit", "Source", "Prediction", "Level", "Timestamp"]
    for col in cols:
        pdf.cell(28, 8, col, border=1)

    pdf.ln()

    for _, row in df.iterrows():
        for col in cols:
            value = str(row[col])[:15] if col in row else "-"
            pdf.cell(28, 8, value, border=1)
        pdf.ln()

    pdf.set_font("Arial", size=9)
    pdf.ln(5)
    pdf.cell(0, 10, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True)

    output_dir = "generated_pdfs"
    os.makedirs(output_dir, exist_ok=True)
    filename = os.path.join(output_dir, f"history_report_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf")
    pdf.output(filename)

    return filename
