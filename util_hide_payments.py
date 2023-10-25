import fitz
import re
import glob

def extract_text_from_pdf(pdf_file_path):
    pdf_document = fitz.open(pdf_file_path)

    extracted_text = ""

    for page in pdf_document:
        page_text = page.get_text()
        extracted_text += page_text

    pdf_document.close()

    return extracted_text

def remove_numeric_values(text):
    numeric_pattern = r'\d[\d,.]*'

    modified_text = re.sub(numeric_pattern, '', text)

    return modified_text

def create_modified_text_file(input_pdf_path, output_txt_path):
    pdf_text = extract_text_from_pdf(input_pdf_path)

    modified_text = remove_numeric_values(pdf_text)

    with open(output_txt_path, 'w') as file:
        file.write(modified_text)

def hide_payment_details():
    file_path_dir = r"static/files/hide/*.pdf"
    output_txt_path = 'static/outputs/hide/modified_text.txt'

    for file_path in glob.glob(file_path_dir, recursive=True):
        create_modified_text_file(file_path, output_txt_path)

    print(f"Highlighted Payment Detail PDF file created as {output_txt_path}")

if __name__ == "__main__":
    hide_payment_details()