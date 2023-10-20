import glob
import re
import PyPDF2
import pandas as pd
import joblib

__model = None


def get_validator():
    # Function to extract emails from text
    def extract_emails(text):
        return re.findall(r"\S+@\S+", text)

    # Function to extract phone numbers from text
    def extract_phone_numbers(text):
        return re.findall(r"\b\d{10}\b|\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b", text)

    # Function to extract addresses from text
    def extract_addresses(text):
        return re.findall(r"\d{1,5}\s\w+.*?(?=\d{5}|\Z)", text)

    # Feature extraction functions
    def extract_email_features(data):
        return data.str.contains("@", regex=False).astype(int)

    def extract_phone_features(data):
        return data.str.match(r"^\d{10}$").astype(int)

    def extract_address_features(data):
        pattern = r"(Street|Avenue|Road)"
        return data.str.contains(pattern, regex=True, case=False).astype(int)

    test_file_path_dir = r"static/files/hygeine/*.*"

    for test_file_path in glob.glob(test_file_path_dir, recursive=True):
        if test_file_path.lower().endswith(".pdf"):
            # Load the PDF file
            with open(test_file_path, "rb") as pdf_file:
                pdf_reader = PyPDF2.PdfReader(pdf_file)
                pdf_text = ""
                for page in pdf_reader.pages:
                    pdf_text += page.extract_text()

        # Extract emails, phone numbers, and addresses from the text
        emails = extract_emails(pdf_text)
        phone_numbers = extract_phone_numbers(pdf_text)
        addresses = extract_addresses(pdf_text)

        # Ensure the same number of data values and data types
        max_length = max(len(emails), len(phone_numbers), len(addresses))
        emails.extend([""] * (max_length - len(emails)))
        phone_numbers.extend([""] * (max_length - len(phone_numbers)))
        addresses.extend([""] * (max_length - len(addresses)))

        # Create the DataFrame with extracted data and data types
        data_values = emails + phone_numbers + addresses
        data_types = (
            ["Email"] * max_length + ["Phone"] * max_length + ["Address"] * max_length
        )

        new_data = pd.DataFrame({"Data": data_values, "Data Type": data_types})

        # Apply the same preprocessing and feature extraction to the new data
        new_data["Data"] = new_data["Data"].apply(str)
        new_data["Email Features"] = extract_email_features(new_data["Data"])
        new_data["Phone Features"] = extract_phone_features(new_data["Data"])
        new_data["Address Features"] = extract_address_features(new_data["Data"])

        # Make predictions
        predictions = __model.predict(
            new_data[["Email Features", "Phone Features", "Address Features"]]
        )

        label_map = {0: "Invalid", 1: "Valid"}

        results = []

        for data_type, data_value, prediction in zip(
            new_data["Data Type"], new_data["Data"], predictions
        ):
            data_label = label_map[prediction]
            results.append(
                {"Data Type": data_type, "Data": data_value, "Predictions": data_label}
            )

        # Create a DataFrame from the results
        results_df = pd.DataFrame(results)

        # Save the text content
        output_file_path = f"static/outputs/hygeine/data_validation.xlsx"

        # Save the results to an Excel file
        results_df.to_excel(output_file_path, index=False)

        return f"Data validation details saved as {output_file_path}"


def load_saved_artifacts():
    print("loading saved artifacts...start")

    global __model
    if __model is None:
        __model = joblib.load("models/Data Hygeine/data-val-model.pkl")
        print(type(__model))

    print("loading saved artifacts...done")


if __name__ == "__main__":
    load_saved_artifacts()
    print(get_validator())
