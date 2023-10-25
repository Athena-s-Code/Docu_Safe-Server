from flask import Flask, request, send_from_directory, jsonify, send_file
from flask_cors import CORS
import os
import re
import shutil

import util_classifier
import util_encryption
import util_hygeine
import util_highlight
import util_hide
import util_data_validatior
import util_title_predictor
import util_highlight_payments
import util_hide_payments

app = Flask(__name__)
CORS(app)

CORS(
    app,
    resources={r"*": {"origins": "http://localhost:3000"}},
)

FOLDER_CLASSIFICATION = "static/files/classification"
FOLDER_ENCRYPTION = "static/files/encryption"
FOLDER_HIGHLIGHT = "static/files/highlight"
FOLDER_HYGIENE = "static/files/hygeine"
FOLDER_HIDE = "static/files/hide"
CLASSIFICATION_OUTPUTS = "static/outputs/classification"
ENCRYPTION_OUTPUTS = "static/outputs/encryption"
HIGHLIGHT_OUTPUTS = "static/outputs/highlights"
HYGIENE_OUTPUTS = "static/outputs/hygeine"
HIDE_OUTPUTS = "static/outputs/hide"
DECRYPTION_OUTPUTS = "static/outputs/decryption"


app.config["FOLDER_CLASSIFICATION"] = FOLDER_CLASSIFICATION
app.config["FOLDER_ENCRYPTION"] = FOLDER_ENCRYPTION
app.config["FOLDER_HIGHLIGHT"] = FOLDER_HIGHLIGHT
app.config["FOLDER_HYGIENE"] = FOLDER_HYGIENE
app.config["FOLDER_HIDE"] = FOLDER_HIDE
app.config["CLASSIFICATION_OUTPUTS"] = CLASSIFICATION_OUTPUTS
app.config["ENCRYPTION_OUTPUTS"] = ENCRYPTION_OUTPUTS
app.config["HIGHLIGHT_OUTPUTS"] = HIGHLIGHT_OUTPUTS
app.config["HYGIENE_OUTPUTS"] = HYGIENE_OUTPUTS
app.config["HIDE_OUTPUTS"] = HIDE_OUTPUTS
app.config["DECRYPTION_OUTPUTS"] = DECRYPTION_OUTPUTS


def clean_directory(directory):
    for item in os.listdir(directory):
        item_path = os.path.join(directory, item)
        if os.path.isdir(item_path):
            shutil.rmtree(item_path)
        else:
            os.remove(item_path)


# Preprocessing function
def preprocess_text(text):
    cleaned_text = text.lower()
    cleaned_text = re.sub(r"[^\w\s]", "", cleaned_text)
    return cleaned_text


@app.route("/classification", methods=["POST"])
def get_classifications():
    if "file" not in request.files:
        return "No file part", 400

    file = request.files["file"]

    if file.filename == "":
        response = jsonify({"message": "No selected file", "status": "fail"})
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response

    folder_path = app.config["FOLDER_CLASSIFICATION"]
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    else:
        clean_directory(folder_path)

    file_path = os.path.join(folder_path, file.filename)
    file.save(file_path)

    output_folder_path = app.config["CLASSIFICATION_OUTPUTS"]
    if not os.path.exists(output_folder_path):
        os.makedirs(output_folder_path)
    else:
        clean_directory(output_folder_path)

    util_classifier.get_confidentiality()

    filename = "confidentiality.txt"
    pdf_path = os.path.join(app.config["CLASSIFICATION_OUTPUTS"], filename)

    response = send_file(pdf_path, as_attachment=True, download_name=filename)
    return response

@app.route("/predictor", methods=["POST"])
def title_predictor():
    if "file" not in request.files:
        return "No file part", 400

    file = request.files["file"]

    if file.filename == "":
        response = jsonify({"message": "No selected file", "status": "fail"})
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response

    folder_path = app.config["FOLDER_CLASSIFICATION"]
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    else:
        clean_directory(folder_path)

    file_path = os.path.join(folder_path, file.filename)
    file.save(file_path)

    output_folder_path = app.config["CLASSIFICATION_OUTPUTS"]
    if not os.path.exists(output_folder_path):
        os.makedirs(output_folder_path)
    else:
        clean_directory(output_folder_path)

    util_title_predictor.get_job_title()

    filename = "predicted_job_titles.xlsx"
    pdf_path = os.path.join(app.config["CLASSIFICATION_OUTPUTS"], filename)

    response = send_file(pdf_path, as_attachment=True, download_name=filename)
    return response

@app.route("/encrypt", methods=["POST"])
def encryption():
    if "file" not in request.files:
        return "No file part", 400

    file = request.files["file"]

    if file.filename == "":
        response = jsonify({"message": "No selected file", "status": "fail"})
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response

    folder_path = app.config["FOLDER_ENCRYPTION"]
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    else:
        clean_directory(folder_path)

    file.save(os.path.join(app.config["FOLDER_ENCRYPTION"], file.filename))

    output_folder_path = app.config["ENCRYPTION_OUTPUTS"]
    if not os.path.exists(output_folder_path):
        os.makedirs(output_folder_path)
    else:
        clean_directory(output_folder_path)

    util_encryption.get_encrypted()

    filename = "encrypted_values.txt"
    pdf_path = os.path.join(app.config["ENCRYPTION_OUTPUTS"], filename)

    response = send_file(pdf_path, as_attachment=True, download_name=filename)
    return response


@app.route("/decrypt", methods=["POST"])
def decryption():
    if "file" not in request.files:
        return "No file part", 400

    file = request.files["file"]

    if file.filename == "":
        response = jsonify({"message": "No selected file", "status": "fail"})
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response

    folder_path = app.config["FOLDER_ENCRYPTION"]
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    else:
        clean_directory(folder_path)

    file.save(os.path.join(app.config["FOLDER_ENCRYPTION"], file.filename))

    output_folder_path = app.config["DECRYPTION_OUTPUTS"]
    if not os.path.exists(output_folder_path):
        os.makedirs(output_folder_path)
    else:
        clean_directory(output_folder_path)

    util_encryption.get_decrypted()

    filename = "decrypted_pii_values.txt"
    pdf_path = os.path.join(app.config["DECRYPTION_OUTPUTS"], filename)

    response = send_file(pdf_path, as_attachment=True, download_name=filename)
    return response


@app.route("/hygeine", methods=["POST"])
def hygeiner():
    if "files" not in request.files:
        return "No file part", 400

    files = request.files.getlist("files")

    if not files:
        response = jsonify({"message": "No selected files", "status": "fail"})
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response

    folder_path = app.config["FOLDER_HYGIENE"]
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    else:
        clean_directory(folder_path)

    for file in files:
        if file.filename == "":
            continue  # Skip empty file fields

        file.save(os.path.join(app.config["FOLDER_HYGIENE"], file.filename))

    output_folder_path = app.config["HYGIENE_OUTPUTS"]
    if not os.path.exists(output_folder_path):
        os.makedirs(output_folder_path)
    else:
        clean_directory(output_folder_path)

    util_hygeine.data_hygeineer()

    pdf_filename = "duplicate_pii_data.txt"
    pdf_path = os.path.join(app.config["HYGIENE_OUTPUTS"], pdf_filename)

    response = send_file(pdf_path, as_attachment=True, download_name=pdf_filename)
    return response


@app.route("/highlight", methods=["POST"])
def highlight():
    if "file" not in request.files:
        return "No file part", 400

    file = request.files["file"]

    if file.filename == "":
        response = jsonify({"message": "No selected file", "status": "fail"})
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response

    folder_path = app.config["FOLDER_HIGHLIGHT"]
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    else:
        clean_directory(folder_path)

    file.save(os.path.join(app.config["FOLDER_HIGHLIGHT"], file.filename))

    output_folder_path = app.config["HIGHLIGHT_OUTPUTS"]
    if not os.path.exists(output_folder_path):
        os.makedirs(output_folder_path)
    else:
        clean_directory(output_folder_path)

    util_highlight.data_highlight()

    pdf_filename = "highlighted.pdf"
    pdf_path = os.path.join(app.config["HIGHLIGHT_OUTPUTS"], pdf_filename)

    response = send_file(pdf_path, as_attachment=True, download_name=pdf_filename)
    return response


@app.route("/hide", methods=["POST"])
def hide():
    if "file" not in request.files:
        return "No file part", 400

    file = request.files["file"]

    if file.filename == "":
        response = jsonify({"message": "No selected file", "status": "fail"})
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response

    folder_path = app.config["FOLDER_HIDE"]
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    else:
        clean_directory(folder_path)

    file.save(os.path.join(app.config["FOLDER_HIDE"], file.filename))

    output_folder_path = app.config["HIDE_OUTPUTS"]
    if not os.path.exists(output_folder_path):
        os.makedirs(output_folder_path)
    else:
        clean_directory(output_folder_path)

    util_hide.data_hide()

    filename = "non_redacted_text.txt"
    pdf_path = os.path.join(app.config["HIDE_OUTPUTS"], filename)

    response = send_file(pdf_path, as_attachment=True, download_name=filename)
    return response

@app.route("/validate", methods=["POST"])
def validate():
    if "file" not in request.files:
        return "No file part", 400

    file = request.files["file"]

    if file.filename == "":
        response = jsonify({"message": "No selected file", "status": "fail"})
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response

    folder_path = app.config["FOLDER_HYGIENE"]
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    else:
        clean_directory(folder_path)

    file.save(os.path.join(app.config["FOLDER_HYGIENE"], file.filename))

    output_folder_path = app.config["HYGIENE_OUTPUTS"]
    if not os.path.exists(output_folder_path):
        os.makedirs(output_folder_path)
    else:
        clean_directory(output_folder_path)

    util_data_validatior.get_validator()

    response = jsonify({"message": "Valiation Successful", "status": "success"})
    response.headers.add("Access-Control-Allow-Origin", "*")

    return response

@app.route("/validate", methods=["GET"])
def get_validation():
    filename = "data_validation.txt"
    pdf_path = os.path.join(app.config["HYGIENE_OUTPUTS"], filename)

    response = send_file(pdf_path, as_attachment=True, download_name=filename)

    return response

@app.route("/highlight_payment", methods=["POST"])
def highlight_payment():
    if "file" not in request.files:
        return "No file part", 400

    file = request.files["file"]

    if file.filename == "":
        response = jsonify({"message": "No selected file", "status": "fail"})
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response

    folder_path = app.config["FOLDER_HIGHLIGHT"]
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    else:
        clean_directory(folder_path)

    file.save(os.path.join(app.config["FOLDER_HIGHLIGHT"], file.filename))

    output_folder_path = app.config["HIGHLIGHT_OUTPUTS"]
    if not os.path.exists(output_folder_path):
        os.makedirs(output_folder_path)
    else:
        clean_directory(output_folder_path)

    util_highlight_payments.highlight_payment_details()

    pdf_filename = "highlighted_payment_and_numeric_values.pdf"
    pdf_path = os.path.join(app.config["HIGHLIGHT_OUTPUTS"], pdf_filename)

    response = send_file(pdf_path, as_attachment=True, download_name=pdf_filename)
    return response

@app.route("/hide_payments", methods=["POST"])
def hide_payments():
    if "file" not in request.files:
        return "No file part", 400

    file = request.files["file"]

    if file.filename == "":
        response = jsonify({"message": "No selected file", "status": "fail"})
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response

    folder_path = app.config["FOLDER_HIDE"]
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    else:
        clean_directory(folder_path)

    file.save(os.path.join(app.config["FOLDER_HIDE"], file.filename))

    output_folder_path = app.config["HIDE_OUTPUTS"]
    if not os.path.exists(output_folder_path):
        os.makedirs(output_folder_path)
    else:
        clean_directory(output_folder_path)

    util_hide_payments.hide_payment_details()

    filename = "modified_text.txt"
    pdf_path = os.path.join(app.config["HIDE_OUTPUTS"], filename)

    response = send_file(pdf_path, as_attachment=True, download_name=filename)
    return response

if __name__ == "__main__":
    util_classifier.load_saved_artifacts()
    util_encryption.load_saved_artifacts()
    util_hygeine.load_saved_artifacts()
    util_hide.load_saved_artifacts()
    util_title_predictor.load_saved_artifacts()
    util_data_validatior.load_saved_artifacts()
    util_highlight_payments.load_saved_artifacts()
    app.run(debug=True)
