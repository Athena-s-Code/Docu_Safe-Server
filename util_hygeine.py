import glob
import numpy as np
import joblib
import fitz  # PyMuPDF
import re
from collections import defaultdict
import easyocr
from PIL import Image

__model = None
__vectorizer = None


def preprocess_text(text):
    cleaned_text = text.lower()
    cleaned_text = re.sub(r"[^\w\s]", "", cleaned_text)
    return cleaned_text


def data_hygeineer():
    # Initialize the easyocr reader
    reader = easyocr.Reader(lang_list=["en"])

    # Dictionary to store preprocessed_text and their corresponding file paths
    file_path_mapping = defaultdict(list)

    test_file_path_dir = r"static/files/hygeine/*.*"

    for test_file_path in glob.glob(test_file_path_dir, recursive=True):
        if test_file_path.lower().endswith(".pdf"):
            with open(test_file_path, "rb") as file:
                pdf = fitz.open(stream=file.read(), filetype="pdf")
                text = ""
                for page_num in range(pdf.page_count):
                    page = pdf[page_num]
                    text += page.get_text()
        elif test_file_path.lower().endswith((".png", ".jpg", ".jpeg")):
            image = Image.open(test_file_path)
            image_np = np.array(image)
            results = reader.readtext(image_np)
            text = " ".join(result[1] for result in results)
        else:
            text = ""

        preprocessed_text = preprocess_text(text)
        document_vec = __vectorizer.transform([preprocessed_text])
        prediction = __model.predict(document_vec)

        file_path_mapping[preprocessed_text].append(test_file_path)

        if prediction == 1:
            print(f"PII Data Detected in {test_file_path}")

    # Find duplicated preprocessed_text (PII data)
    duplicated_pii_data = {
        preprocessed_text: file_paths
        for preprocessed_text, file_paths in file_path_mapping.items()
        if len(file_paths) > 1
    }

    # Create a text content for the TXT file
    output_text = ""
    for preprocessed_text, file_paths in duplicated_pii_data.items():
        output_text += f"Duplicated PII Data:\n"
        output_text += f"PII Data: {preprocessed_text}\n"
        output_text += f"Duplicated in Files:\n"
        output_text += ", ".join(file_paths) + "\n"
        output_text += "=" * 40 + "\n\n"

    if not output_text:
        output_text = "No Dulpicated PII Data detected."
        print("No Dulpicated PII Data detected.")

    # Save the text content to a TXT file
    output_file_path = "static/outputs/hygeine/duplicate_pii_data.txt"
    with open(output_file_path, "w", encoding="utf-8") as output_file:
        output_file.write(output_text)

    return f"Duplicate PII data details saved as {output_file_path}"


def load_saved_artifacts():
    print("loading saved artifacts...start")

    global __model
    if __model is None:
        __model = joblib.load("models/Data Hygeine/svm_model.pkl")
        print(type(__model))

    global __vectorizer
    if __vectorizer is None:
        __vectorizer = joblib.load("models/Data Hygeine/vectorizer.pkl")
        print(type(__vectorizer))

    print("loading saved artifacts...done")


if __name__ == "__main__":
    load_saved_artifacts()
    print(data_hygeineer())
