# pdf_utils.py

import pdfplumber

def extract_text_from_pdf(pdf_path):
  text = ""
  with pdfplumber.open(pdf_path) as pdf:
    for page in pdf.pages:
      page_text = page.extract_text(x_tolerance=1)
      text += page_text + "\n"
  return text
