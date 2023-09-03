import glob

from fuzzywuzzy import fuzz
import re
import spacy
import fitz
import easyocr
from fuzzywuzzy import fuzz
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
import PyPDF2


def data_highlight():
    pii_keywords = [
        "SSN",
        "Social Security Number",
        "DOB",
        "Date of Birth",
        "Name",
        "Address",
        "Phone Number",
        "Phone",
        "TelephoneNo",
        "E-mail",
        "EmailAddress",
        "Credit Card Number",
        "FullNames",
        "IDCardNo",
        "Contact",
        "PostalAddress",
    ]

    def check_for_pii(text):
        found_keywords = []
        for keyword in pii_keywords:
            pattern = re.compile(r"\b{}\b".format(re.escape(keyword)), re.IGNORECASE)
            if pattern.search(text):
                found_keywords.append(keyword)
        return found_keywords

    # Initialize the easyocr reader
    reader = easyocr.Reader(lang_list=["en"])

    def extract_text_from_image(image_path):
        result = reader.readtext(image_path)
        text = " ".join(result[1] for result in result)
        return text

    # File path
    file_path_dir = r"static/files/highlight/*.*"

    for file_path in glob.glob(file_path_dir, recursive=True):
        if file_path.lower().endswith(".pdf"):
            # PDF handling logic
            with open(file_path, "rb") as pdf:
                pdf_reader = PyPDF2.PdfReader(pdf)
                text_content = ""
                for page in pdf_reader.pages:
                    text_content += page.extract_text()
            if text_content:
                pii_detected = check_for_pii(text_content)
                if pii_detected:
                    print("PII keywords detected:", ", ".join(pii_detected))
                    print("Potential Personally Identifiable Information found.")

                    doc = fitz.open(file_path)
                    num_pages = len(doc)

                    for page_num in range(num_pages):
                        page = doc.load_page(page_num)
                        page_text = page.get_text()

                        # Search for PII data using fuzzy matching
                        for keyword in pii_detected:
                            matches = re.finditer(
                                rf"\b{re.escape(keyword)}\b",
                                page_text,
                                flags=re.IGNORECASE,
                            )
                            for match in matches:
                                start_pos = match.start()
                                end_pos = match.end()
                                text_slice = page_text[start_pos:end_pos]

                                match_score = fuzz.partial_ratio(
                                    text_slice.lower(), keyword.lower()
                                )

                                if match_score >= 80:
                                    instances = page.search_for(text_slice)
                                    for instance in instances:
                                        highlight = page.add_rect_annot(instance)
                                        highlight.set_colors({"fill": (1, 0, 1)})

                    # Save the modified PDF file
                    output_file = "static/outputs/highlights/highlighted.pdf"
                    doc.save(output_file)
                    doc.close()

                    return "Highlighted PDF file created:", output_file
                else:
                    return "No PII keywords detected."
            else:
                return "Error: Unable to extract text from the PDF."

        elif file_path.lower().endswith((".jpg", ".jpeg", ".png", ".bmp")):
            # Image handling logic
            extracted_text = extract_text_from_image(file_path)
            if extracted_text:
                pii_detected = check_for_pii(extracted_text)
                if pii_detected:
                    print("PII keywords detected:", ", ".join(pii_detected))
                    print("Potential Personally Identifiable Information found.")

                    # Create a PDF document
                    output_pdf_path = "static/outputs/highlights/highlighted_text.pdf"
                    doc = SimpleDocTemplate(output_pdf_path, pagesize=letter)
                    styles = getSampleStyleSheet()

                    # Create a list of paragraphs with highlighted PII data
                    paragraphs = []
                    for keyword in pii_detected:
                        modified_text = re.sub(
                            rf"\b{re.escape(keyword)}\b",
                            f'<font color="red">[{keyword}]</font>',
                            extracted_text,
                            flags=re.IGNORECASE,
                        )
                        paragraph = Paragraph(modified_text, style=styles["Normal"])
                        paragraphs.append(paragraph)

                    doc.build(paragraphs)

                    return "Modified PDF file created:", output_pdf_path
                else:
                    return "No PII keywords detected in the image."
            else:
                return "Error: Unable to extract text from the image."
        else:
            return "Unsupported file format."


if __name__ == "__main__":
    print(data_highlight())
