import glob
import pandas as pd
import re
import nltk
from PyPDF2 import PdfReader
import joblib
from json import loads, dumps

__model = None
__vectorizer = None
__label_encorder = None


def get_job_title():
    def extract_text_from_pdf(pdf_file_path):
        pdf_text = ""
        try:
            pdf_reader = PdfReader(pdf_file_path)
            for page in pdf_reader.pages:
                pdf_text += page.extract_text()
        except Exception as e:
            print(f"Error reading PDF: {e}")

        return pdf_text

    # preprocess the text
    def preprocess_text(text):
        text = text.lower()
        text = re.sub(r"\s+", " ", text)
        text = re.sub(r"[^a-zA-Z\s]", "", text)
        text = nltk.word_tokenize(text)
        text = " ".join(text)
        return text

    def predict_job_title_from_pdf(pdf_file_path):
        pdf_text = extract_text_from_pdf(pdf_file_path)
        pdf_text = preprocess_text(pdf_text)
        pdf_text_tfidf = __vectorizer.transform([pdf_text])
        prediction = __model.predict(pdf_text_tfidf)
        predicted_job_title = __label_encorder.inverse_transform(prediction)
        return predicted_job_title[0]

    file_path_dir = r"static/files/classification/*.*"

    results = []
    for pdf_file_path in glob.glob(file_path_dir, recursive=True):
        predicted_job_title = predict_job_title_from_pdf(pdf_file_path)
        results.append(
            {"File Path": pdf_file_path, "Predicted Job Title": predicted_job_title}
        )

    # Create a DataFrame from the results
    results_df = pd.DataFrame(results)

    # Specify the path where you want to save the Excel file
    excel_file_path = "static/outputs/classification/predicted_job_titles.xlsx"

    # Save the results to an Excel file
    results_df.to_excel(excel_file_path, index=False)

    result = results_df.to_json(orient="records")

    print(f"Results saved to {excel_file_path}")

    return result


def load_saved_artifacts():
    print("loading saved artifacts...start")

    global __model
    if __model is None:
        __model = joblib.load("models/Data Classification/title-pred-model.pkl")
        print(type(__model))

    global __vectorizer
    if __vectorizer is None:
        __vectorizer = joblib.load(
            "models/Data Classification/title-pred-tfidf_vectorizer.pkl"
        )
        print(type(__vectorizer))

    global __label_encorder
    if __label_encorder is None:
        __label_encorder = joblib.load("models/Data Classification/label_encoder.pkl")
        print(type(__label_encorder))

    print("loading saved artifacts...done")


if __name__ == "__main__":
    load_saved_artifacts()
    print(get_job_title())
