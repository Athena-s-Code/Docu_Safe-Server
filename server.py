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

app = Flask(__name__)
CORS(app)

CORS(app, resources={
     r"*": {"origins": "https://deploy-preview-32--beautiful-pegasus-9a5f30.netlify.app"}})

FOLDER_CLASSIFICATION = "static/files/classification"
FOLDER_ENCRYPTION = "static/files/encryption"
FOLDER_HIGHLIGHT = "static/files/highlight"
FOLDER_HYGIENE = "static/files/hygeine"
FOLDER_HIDE = "static/files/hide"
FOLDER_OUTPUTS = "static/outputs"


app.config["FOLDER_CLASSIFICATION"] = FOLDER_CLASSIFICATION
app.config["FOLDER_ENCRYPTION"] = FOLDER_ENCRYPTION
app.config["FOLDER_HIGHLIGHT"] = FOLDER_HIGHLIGHT
app.config["FOLDER_HYGIENE"] = FOLDER_HYGIENE
app.config["FOLDER_HIDE"] = FOLDER_HIDE
app.config["FOLDER_OUTPUTS"] = FOLDER_OUTPUTS


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
        response = jsonify(
            {"message": "No selected file", "status": "fail"})
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response

    folder_path = app.config["FOLDER_CLASSIFICATION"]
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    else:
        clean_directory(folder_path)

    file_path = os.path.join(folder_path, file.filename)
    file.save(file_path)

    response = jsonify(
        {"classification": util_classifier.get_confidentiality(), "status": "success"})
    response.headers.add("Access-Control-Allow-Origin", "*")
    print("classifications response:", response)
    return response


@app.route("/encrypt", methods=["POST"])
def encryption():
    if "file" not in request.files:
        return "No file part", 400

    file = request.files["file"]

    if file.filename == "":
        response = jsonify(
            {"message": "No selected file", "status": "fail"})
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response

    folder_path = app.config["FOLDER_ENCRYPTION"]
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    else:
        clean_directory(folder_path)

    file.save(os.path.join(app.config["FOLDER_ENCRYPTION"], file.filename))

    response = jsonify(
        {"encrypted": str(util_encryption.get_encrypted()), "status": "success"})
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response


@app.route("/decrypt", methods=["POST"])
def decryption():
    if "file" not in request.files:
        return "No file part", 400

    file = request.files["file"]

    if file.filename == "":
        response = jsonify(
            {"message": "No selected file", "status": "fail"})
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response

    folder_path = app.config["FOLDER_ENCRYPTION"]
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    else:
        clean_directory(folder_path)

    file.save(os.path.join(app.config["FOLDER_ENCRYPTION"], file.filename))

    response = jsonify(
        {"decrypted": str(util_encryption.get_decrypted()), "status": "success"})
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response


@app.route("/hygeine", methods=["POST"])
def hygeiner():
    if "files" not in request.files:
        return "No file part", 400

    files = request.files.getlist("files")

    if not files:
        response = jsonify(
            {"message": "No selected files", "status": "fail"})
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

    response = jsonify(
        {"hygeine_txt": util_hygeine.data_hygeineer(), "status": "success"})
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response


@app.route("/highlight", methods=["POST"])
def highlight():
    if "file" not in request.files:
        return "No file part", 400

    file = request.files["file"]

    if file.filename == "":
        response = jsonify(
            {"message": "No selected file", "status": "fail"})
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response

    folder_path = app.config["FOLDER_HIGHLIGHT"]
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    else:
        clean_directory(folder_path)

    file.save(os.path.join(app.config["FOLDER_HIGHLIGHT"], file.filename))

    output_folder_path = app.config["FOLDER_OUTPUTS"]
    if not os.path.exists(output_folder_path):
        os.makedirs(output_folder_path)
    else:
        clean_directory(output_folder_path)

    util_highlight.data_highlight()

    pdf_filename = "highlighted.pdf"
    pdf_path = os.path.join(app.config["FOLDER_OUTPUTS"], pdf_filename)

    response = send_file(pdf_path, as_attachment=True,
                         download_name=pdf_filename)
    return response


@app.route("/hide", methods=["POST"])
def hide():
    if "file" not in request.files:
        return "No file part", 400

    file = request.files["file"]

    if file.filename == "":
        response = jsonify(
            {"message": "No selected file", "status": "fail"})
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response

    folder_path = app.config["FOLDER_HIDE"]
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    else:
        clean_directory(folder_path)

    file.save(os.path.join(app.config["FOLDER_HIDE"], file.filename))

    response = jsonify(
        {"redacted": util_hide.data_hide(), "status": "success"})
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response


if __name__ == "__main__":
    util_classifier.load_saved_artifacts()
    util_encryption.load_saved_artifacts()
    util_hygeine.load_saved_artifacts()
    util_hide.load_saved_artifacts()
    app.run(debug=True)
