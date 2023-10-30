import glob

import joblib
import re
import nltk
import string
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from pyDes import triple_des, PAD_PKCS5, CBC
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
import PyPDF2

__model = None
__vectorizer = None

text_content = ""
# Regular expressions for PII types
pii_patterns = {
    r"\bSSN\b": "SSN",
    r"\bSocial Security Number\b": "Social Security Number",
    r"\bDOB\b": "DOB",
    r"\bDate of Birth\b": "Date of Birth",
    r"\bName\b": "Name",
    r"\bPhone Number\b": "Phone Number",
    r"\bPhone\b": "Phone",
    r"\bE-mail\b": "E-mail",
    r"\bEmailAddress\b": "EmailAddress",
    r"\bCredit Card Number\b": "Credit Card Number",
    r"\bFullNames\b": "FullNames",
    r"\bIDCardNo\b": "IDCardNo",
    r"\bTelephoneNo\b": "TelephoneNo",
    r"\bContact\b": "Contact",
}


def get_encrypted():
    pdf_path_dir = r"static/files/encryption/*.pdf"

    for pdf_path in glob.glob(pdf_path_dir, recursive=True):
        with open(pdf_path, "rb") as pdf:
            pdf_reader = PyPDF2.PdfReader(pdf)
            global text_content
            for page in pdf_reader.pages:
                text_content += page.extract_text()

    # Preprocess the text content
    def preprocess_text(text):
        # Convert to lowercase
        text = text.lower()

        # Remove punctuation
        text = text.translate(str.maketrans("", "", string.punctuation))

        # Tokenize and remove stopwords
        nltk.download("punkt")
        nltk.download("stopwords")
        stop_words = set(stopwords.words("english"))
        tokens = word_tokenize(text)
        tokens = [token for token in tokens if token not in stop_words]

        preprocessed_text = " ".join(tokens)
        return preprocessed_text

    preprocessed_text = preprocess_text(text_content)

    # Predict if the PDF contains PII data
    tfidf_text = __vectorizer.transform([preprocessed_text])
    prediction = __model.predict(tfidf_text)

    # Encrypt PII using cryptography library if detected
    if prediction == 1:
        key = b"secretpassword1234567890"
        mode = CBC

        pii_mappings = {}
        global pii_patterns

        encrypted_pii_values = {}

        for pattern, pii_type in pii_patterns.items():
            encrypted_value = triple_des(key, mode, padmode=PAD_PKCS5).encrypt(
                pii_type.encode("utf-8")
            )
            encrypted_pii_values[pii_type] = encrypted_value

    story = []

    # styles for normal and highlighted text
    styles = getSampleStyleSheet()
    normal_style = styles["Normal"]
    highlighted_style = normal_style.clone("highlighted")
    highlighted_style.textColor = colors.red

    highlighted_values = []

    for line in text_content.split("\n"):
        for pattern, pii_type in pii_patterns.items():
            line = re.sub(pattern, f"[{pii_type}]", line)
            line = re.sub(
                rf"\[{pii_type}\]", f'<font color="red">[{pii_type}]</font>', line
            )

            # Check if a highlighted value is found
            if f'<font color="red">[{pii_type}]</font>' in line:
                highlighted_values.append(line)

    print("Highlighted PII values:")
    for value in highlighted_values:
        print(value)

    # Encrypt and print the values
    encrypted_values = {}

    for value in highlighted_values:
        pii_type_start = value.find("[")
        pii_type_end = value.find("]")
        pii_type = value[pii_type_start + 1 : pii_type_end]

        # Find the start of the encryption
        encrypted_text_start = value.find("</font>") + len("</font>")

        text_to_encrypt = value[encrypted_text_start:]

        encrypted_text = triple_des(key, mode, padmode=PAD_PKCS5).encrypt(
            text_to_encrypt.encode("utf-8")
        )
        encrypted_values[pii_type] = encrypted_text

        # Replace the original text with the encrypted text
        encrypted_value = f"[{pii_type}: {encrypted_text}]"
        value = value[:encrypted_text_start] + encrypted_value
        # print(value)

    # Save as a file
    output_txt_path = "static/outputs/encryption/encrypted_values.txt"
    with open(output_txt_path, "w", encoding="utf-8") as txt_file:
        for pii_type, encrypted_text in encrypted_values.items():
            txt_file.write(f"{pii_type}: {encrypted_text}\n")

    return f"All encrypted values saved to {output_txt_path}"


def get_decrypted():
    pdf_path_dir = r"static/files/encryption/*.pdf"

    for pdf_path in glob.glob(pdf_path_dir, recursive=True):
        with open(pdf_path, "rb") as pdf:
            pdf_reader = PyPDF2.PdfReader(pdf)
            global text_content
            for page in pdf_reader.pages:
                text_content += page.extract_text()

    # Detect PII values and save to a file
    detected_pii_values = []

    for line in text_content.split("\n"):
        for pattern, pii_type in pii_patterns.items():
            if re.search(pattern, line):
                detected_pii_values.append(f"{pii_type}: {line.strip()}")

    # Save detected PII values to a file
    decrypted_pii_output_path = "static/outputs/decryption/decrypted_pii_values.txt"
    with open(decrypted_pii_output_path, "w", encoding="utf-8") as txt_file:
        for detected_pii_value in detected_pii_values:
            txt_file.write(f"{detected_pii_value}\n")

    return f"All detected PII values saved to {decrypted_pii_output_path}"


def load_saved_artifacts():
    print("loading saved artifacts...start")

    global __model
    if __model is None:
        __model = joblib.load(
            "models/Data Encryption and Decryption/pii_encryption_model.pkl"
        )
        print(type(__model))

    global __vectorizer
    if __vectorizer is None:
        __vectorizer = joblib.load(
            "models/Data Encryption and Decryption/vectorizer.pkl"
        )
        print(type(__vectorizer))

    print("loading saved artifacts...done")


if __name__ == "__main__":
    load_saved_artifacts()
    print(get_encrypted())
    print(get_decrypted())
