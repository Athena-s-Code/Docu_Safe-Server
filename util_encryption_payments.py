import joblib
import glob
import fitz
from pyDes import triple_des, PAD_PKCS5, CBC

__model = None
__vectorizer = None
def extract_payment_details_from_pdf(pdf_file_path):
    pdf_document = fitz.open(pdf_file_path)

    payment_details = []

    for page in pdf_document:
        page_text = page.get_text()
        payment_details.append(page_text)

    pdf_document.close()

    return payment_details

def encrypt_payment_details():
    pdf_path_dir = r"static/files/encryption/*.pdf"

    for pdf_path in glob.glob(pdf_path_dir, recursive=True):
        payment_details = extract_payment_details_from_pdf(pdf_path)
    new_text_data = payment_details

    # Define the encryption key and mode
    key = b"secretpassword1234567890"
    mode = CBC

    encrypted_texts = {}

    new_text_data_vectorized = __vectorizer.transform(new_text_data)

    predictions = __model.predict(new_text_data_vectorized)

    for text, prediction in zip(new_text_data, predictions):
        if prediction == 1:
            encrypted_text = triple_des(key, mode, padmode=PAD_PKCS5).encrypt(text.encode('utf-8'))
            encrypted_texts[text] = encrypted_text

    for text, encrypted_text in encrypted_texts.items():
        txt = encrypted_text.hex()

    output_txt_path = 'static/outputs/encryption/encrypted_payment_details.txt'

    with open(output_txt_path, 'w', encoding='utf-8') as txt_file:
        for text, encrypted_text in encrypted_texts.items():
            txt_file.write(f"{encrypted_text.hex()}\n")

    print(f"Encrypted payment details saved to {output_txt_path}")

    return txt , output_txt_path

def decrypt_payment_details():
    def decrypt_text(encrypted_text, key, mode=CBC):
        try:
            decrypted_text = triple_des(key, mode, padmode=PAD_PKCS5).decrypt(bytes.fromhex(encrypted_text))
            return decrypted_text.decode('utf-8')
        except Exception as e:
            return f"Decryption error: {str(e)}"

    key = b"secretpassword1234567890"
    mode = CBC

    path_dir = r"static/files/decryption/*.txt"

    for file_path in glob.glob(path_dir, recursive=True):
        with open(file_path, 'r', encoding='utf-8') as txt_file:
            encrypted_payment_text = txt_file.read()

    encrypted_lines = encrypted_payment_text.strip().split('\n')

    decrypted_texts = []

    for encrypted_line in encrypted_lines:
        decrypted_line = decrypt_text(encrypted_line, key, mode)
        decrypted_texts.append(decrypted_line)

    output_decrypted_txt_path = 'static/outputs/decryption/decrypted_payment_details.txt'
    with open(output_decrypted_txt_path, 'w', encoding='utf-8') as decrypted_txt_file:
        decrypted_txt_file.write('\n'.join(decrypted_texts))

    print(f"Decrypted payment details saved to {output_decrypted_txt_path}")

    return output_decrypted_txt_path

def load_saved_artifacts():
    print("loading saved artifacts...start")

    global __model
    if __model is None:
        __model = joblib.load("models/Data Encryption and Decryption/best_payment_model.pkl")
        print(type(__model))

    global __vectorizer
    if __vectorizer is None:
        __vectorizer = joblib.load(
            "models/Data Encryption and Decryption/tfidf_vectorizer.pkl"
        )
        print(type(__vectorizer))

    print("loading saved artifacts...done")

if __name__ == "__main__":
    # load_saved_artifacts()
    # txt, path = encrypt_payment_details()
    # decrypt_payment_details()