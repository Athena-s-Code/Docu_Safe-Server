import easyocr
import PyPDF2
import joblib

__model = None
__vectorizer = None


def get_confidentiality():
    # Initialize EasyOCR reader
    reader = easyocr.Reader(["en"])

    def extract_text_from_pdf(pdf_path):
        with open(pdf_path, "rb") as pdf_file:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
            return text

    def extract_text_from_image(image_path):
        result = reader.readtext(image_path)
        text = " ".join([res[1] for res in result])
        return text

    def contains_pii(text):
        pii_keywords = [
            "SSN",
            "Social Security Number",
            "DOB",
            "Date of Birth",
            "Name",
            "Address",
            "Phone Number",
            "Phone",
            "E-mail",
            "EmailAddress",
            "Credit Card Number",
            "FullNames",
            "IDCardNo",
            "TelephoneNo",
            "Contact",
        ]
        for keyword in pii_keywords:
            if keyword.lower() in text.lower():
                return True
        return False

    def predict_confidentiality(text):
        features = __vectorizer.transform([text])
        prediction = __model.predict(features)
        return prediction[0]

    file_path = "static/files/classification/Invoice_1304755949.pdf"

    if file_path.lower().endswith(".pdf"):
        extracted_text = extract_text_from_pdf(file_path)
        prediction = predict_confidentiality(extracted_text)
    elif file_path.lower().endswith((".jpg", ".jpeg", ".png", ".bmp")):
        extracted_text = extract_text_from_image(file_path)
        print("Extracted Text:", extracted_text)

        prediction = (
            "Confidential" if contains_pii(extracted_text) else "Non-Confidential"
        )

    else:
        raise ValueError("Unsupported file format")

    return prediction


def load_saved_artifacts():
    print("loading saved artifacts...start")

    global __model
    if __model is None:
        __model = joblib.load("models/Data Classification/RF_model.pkl")
        print(type(__model))

    global __vectorizer
    if __vectorizer is None:
        __vectorizer = joblib.load("models/Data Classification/vectorizer.pkl")
        print(type(__vectorizer))

    print("loading saved artifacts...done")


if __name__ == "__main__":
    load_saved_artifacts()
    print(get_confidentiality())
