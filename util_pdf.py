import fitz

def extract_text_from_pdf(filepath):
    with fitz.open(filepath) as doc:
        FORM_FEED = 12
        text = chr(FORM_FEED).join([page.get_text() for page in doc])
        return text

def is_pdf(filepath):
    return filepath[-4:] == ".pdf"
