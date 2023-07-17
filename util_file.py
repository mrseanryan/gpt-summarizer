import util_pdf

def read_text_from_file(filepath):
    if util_pdf.is_pdf(filepath):
        return util_pdf.extract_text_from_pdf(filepath)
    with open(filepath, encoding='utf-8') as file:
        return file.read()
