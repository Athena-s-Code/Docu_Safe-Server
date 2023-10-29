import fitz
from pyDes import triple_des, PAD_PKCS5, CBC
import glob

def extract_from_pdf(pdf_file_path):
    pdf_document = fitz.open(pdf_file_path)
    payment_details = []

    for page in pdf_document:
        page_text = page.get_text()
        payment_details.append(page_text)

    pdf_document.close()
    return payment_details

def encrypt_whole_file():
    pdf_path_dir = r"static/files/encryption/*.pdf"
    for pdf_path in glob.glob(pdf_path_dir, recursive=True):
        details = extract_from_pdf(pdf_path)

    key = b"secretpassword1234567890"
    mode = CBC

    encrypted_texts = {}

    for text in details:
        encrypted_text = triple_des(key, mode, padmode=PAD_PKCS5).encrypt(text.encode('utf-8'))
        encrypted_texts[text] = encrypted_text

    output_txt_path = 'static/outputs/encryption/encrypted_details.txt'

    with open(output_txt_path, 'w', encoding='utf-8') as txt_file:
        for text, encrypted_text in encrypted_texts.items():
            txt_file.write(f"{encrypted_text.hex()}\n")

    print(f"Encrypted details saved to {output_txt_path}")

def decrypt_text(encrypted_text, key, mode=CBC):
    try:
        decrypted_text = triple_des(key, mode, padmode=PAD_PKCS5).decrypt(bytes.fromhex(encrypted_text))
        return decrypted_text.decode('utf-8')
    except Exception as e:
        return f"Decryption error: {str(e)}"

def decrypt_whole_file():
    key = b"secretpassword1234567890"
    mode = CBC

    path_dir = r"static/files/decryption/*.txt"
    for file_path in glob.glob(path_dir, recursive=True):
        with open(file_path, 'r', encoding='utf-8') as txt_file:
            encrypted_text = txt_file.read()

    encrypted_lines = encrypted_text.strip().split('\n')

    decrypted_texts = []

    for encrypted_line in encrypted_lines:
        decrypted_line = decrypt_text(encrypted_line, key, mode)
        decrypted_texts.append(decrypted_line)

    output_decrypted_txt_path = 'static/outputs/decryption/decrypted_details.txt'
    with open(output_decrypted_txt_path, 'w', encoding='utf-8') as decrypted_txt_file:
        decrypted_txt_file.write('\n'.join(decrypted_texts))

    print(f"Decrypted details saved to {output_decrypted_txt_path}")

if __name__ == "__main__":
    encrypt_whole_file()
    decrypt_whole_file()
