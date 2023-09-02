from flask import Flask, request, send_from_directory, jsonify
from flask_cors import CORS
import os
import re

import util_classifier, util_encryption, util_hygeine, util_highlight, util_hide

app = Flask(__name__)
CORS(app)

CORS(app, resources={r"/upload": {"origins": "http://localhost:3000"}})

UPLOAD_FOLDER = "static/files/"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


# Preprocessing function
def preprocess_text(text):
    cleaned_text = text.lower()
    cleaned_text = re.sub(r"[^\w\s]", "", cleaned_text)
    return cleaned_text


@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return "No file part", 400

    file = request.files["file"]

    if file.filename == "":
        return "No selected file", 400

    file.save(os.path.join(app.config["UPLOAD_FOLDER"], file.filename))
    return "File uploaded successfully", 200


@app.route("/get_pdf/<filename>")
def get_pdf(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)


@app.route("/classify")
def get_classifications():
    response = jsonify({"classification": util_classifier.get_confidentiality()})
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response


@app.route("/encrypt")
def encryption():
    response = jsonify({"encrypted": str(util_encryption.get_encrypted())})
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response


@app.route("/decrypt")
def decryption():
    response = jsonify({"decrypted": str(util_encryption.get_decrypted())})
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response


@app.route("/hygeine")
def hygeiner():
    response = jsonify({"hygeine_txt": util_hygeine.data_hygeineer()})
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response


@app.route("/highlight")
def highlight():
    util_highlight.data_highlight()
    # send the pdf file that generated in the static/outputs


@app.route("/hide")
def hide():
    response = jsonify({"redacted": util_hide.data_hide()})
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response


if __name__ == "__main__":
    util_classifier.load_saved_artifacts()
    util_encryption.load_saved_artifacts()
    util_hygeine.load_saved_artifacts()
    util_hide.load_saved_artifacts()
    app.run(debug=True)
