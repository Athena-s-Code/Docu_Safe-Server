import joblib
import fitz
import re
import glob

__model = None
__vectorizer = None

def highlight_payment_and_numeric_values(pdf_file_path, output_pdf_path, loaded_model, tfidf_vectorizer):
    pdf_document = fitz.open(pdf_file_path)
    numeric_pattern = r'\d[\d,.]*'

    for page in pdf_document:
        page_text = page.get_text()
        processed_page_text = page_text.lower()
        page_text_vectorized = tfidf_vectorizer.transform([processed_page_text])
        prediction = loaded_model.predict(page_text_vectorized)

        if prediction == 1:
            numeric_values = re.finditer(numeric_pattern, page_text)

            for match in numeric_values:
                start = match.start()
                end = match.end()

                numeric_value = match.group(0)
                highlight = page.add_highlight_annot(page.search_for(numeric_value))
                highlight.update()

    # Save the modified PDF
    pdf_document.save(output_pdf_path)
    pdf_document.close()

    print(f"Highlighted Payment Detail PDF file created as {output_pdf_path}")

def highlight_payment_details():
    file_path_dir = r"static/files/highlight/*.pdf"

    for file_path in glob.glob(file_path_dir, recursive=True):
        output_pdf_path = 'static/outputs/highlights/highlighted_payment_and_numeric_values.pdf'
        highlight_payment_and_numeric_values(file_path, output_pdf_path, __model, __vectorizer)
def load_saved_artifacts():
    print("loading saved artifacts...start")

    global __model
    if __model is None:
        __model = joblib.load("models/Data Highlight/best_payment_model.pkl")
        print(type(__model))

    global __vectorizer
    if __vectorizer is None:
        __vectorizer = joblib.load("models/Data Highlight/tfidf_vectorizer.pkl")
        print(type(__vectorizer))

    print("loading saved artifacts...done")

if __name__ == "__main__":
    load_saved_artifacts()
    highlight_payment_details()