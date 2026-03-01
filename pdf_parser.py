import fitz

def extract_text_from_pdf(pdf_file):
    try:
        pdf_stream = pdf_file.read()
        doc = fitz.open(stream=pdf_stream, filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
        return text.strip()
    except Exception as e:
        raise ValueError(f"Failed to parse PDF: {str(e)}")
