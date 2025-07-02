from fpdf import FPDF
from io import BytesIO

def generate_pdf(data, output_path=None):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(200, 10, txt="GHG Emission Prediction Report", ln=True, align="C")
    pdf.ln(10)

    for key, value in data.items():
        pdf.cell(200, 10, txt=f"{key}: {value}", ln=True)

    if output_path:
        # Save to file for download
        pdf.output(output_path)
        return None
    else:
        # Return PDF in-memory for email
        buffer = BytesIO()
        pdf.output(buffer)
        buffer.seek(0)
        return buffer.read()
