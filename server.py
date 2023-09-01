from flask import Flask, request, send_from_directory, jsonify
from flask_cors import CORS
import os
import json

import util_classifier
import util_encryption
import util_hygeine
import util_highlight

app = Flask(__name__)
CORS(app)

CORS(app, resources={r"*": {"origins": "http://localhost:3000"}})

FOLDER_CLASSIFICATION = "static/files/classification"
FOLDER_ENCRYPTION = "static/files/encryption"
FOLDER_HIGHLIGHT = "static/files/highlight"
FOLDER_HYGIENE = "static/files/hygiene"

for folder in [FOLDER_CLASSIFICATION, FOLDER_ENCRYPTION, FOLDER_HIGHLIGHT, FOLDER_HYGIENE]:
    if not os.path.exists(folder):
        os.makedirs(folder)

app.config["FOLDER_CLASSIFICATION"] = FOLDER_CLASSIFICATION
app.config["FOLDER_ENCRYPTION"] = FOLDER_ENCRYPTION
app.config["FOLDER_HIGHLIGHT"] = FOLDER_HIGHLIGHT
app.config["FOLDER_HYGIENE"] = FOLDER_HYGIENE


def upload_file_to_folder(upload_folder_key):
    if "file" not in request.files:
        return "No file part", 400

    file = request.files["file"]

    if file.filename == "":
        return "No selected file", 400

    folder_path = app.config[upload_folder_key]
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    file.save(os.path.join(app.config[upload_folder_key], file.filename))
    return "File uploaded successfully", 200


@app.route("/classify", methods=["POST"])
def upload_classification_file():
    return upload_file_to_folder("FOLDER_CLASSIFICATION")


def get_classifications():
    response = jsonify(
        {"classification": util_classifier.get_confidentiality()})
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response


@app.route("/encrypt", methods=["POST"])
def upload_encryption_file():
    return upload_file_to_folder("FOLDER_ENCRYPTION")


def encryption():
    response = jsonify({"encrypted": str(util_encryption.get_encrypted())})
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response


@app.route("/decrypt", methods=["POST"])
def decryption():
    response = jsonify({"decrypted": str(util_encryption.get_decrypted())})
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response


@app.route("/hygeine", methods=["POST"])
def upload_hygiene_file():
    return upload_file_to_folder("FOLDER_HYGIENE")


def hygeiner():
    response = jsonify({"hygeine_txt": util_hygeine.data_hygeineer()})
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response


@app.route("/highlight", methods=["POST"])
def upload_highlight_file():
    return upload_file_to_folder("FOLDER_HIGHLIGHT")


def highlight():
    util_highlight.data_highlight()
    # send the pdf file that generated in the static/outputs


if __name__ == "__main__":
    util_classifier.load_saved_artifacts()
    util_encryption.load_saved_artifacts()
    app.run(debug=True)
