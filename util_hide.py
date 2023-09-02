import glob

import torch
import torch.nn as nn
import torch.optim as optim
from transformers import BertTokenizer
import pdfplumber
from PIL import Image
import pytesseract
import spacy

model_path = "bert-base-uncased"
tokenizer = BertTokenizer.from_pretrained(model_path)

__model = None

# Define model parameters
vocab_size = tokenizer.vocab_size
embedding_dim = 128
hidden_dim = 256
max_length = 128


# Define your RedactionModel
class RedactionModel(nn.Module):
    def __init__(self, vocab_size, embedding_dim, hidden_dim):
        super(RedactionModel, self).__init__()
        self.embedding = nn.Embedding(vocab_size, embedding_dim)
        self.decoder = nn.LSTM(embedding_dim, hidden_dim, batch_first=True)
        self.output_layer = nn.Linear(hidden_dim, vocab_size)

    def forward(self, input_ids, attention_mask, decoder_hidden=None):
        embedded_decoder_input = self.embedding(input_ids[:, :-1])
        if decoder_hidden is None:
            batch_size = input_ids.size(0)
            decoder_hidden = (
                torch.zeros(1, batch_size, self.decoder.hidden_size).to(
                    input_ids.device
                ),
                torch.zeros(1, batch_size, self.decoder.hidden_size).to(
                    input_ids.device
                ),
            )
        decoder_output, _ = self.decoder(embedded_decoder_input, decoder_hidden)
        output = self.output_layer(decoder_output)
        return output


def data_hide():
    file_path_dir = r"static/files/hide/*.pdf"

    for file_path in glob.glob(file_path_dir, recursive=True):
        with pdfplumber.open(file_path) as pdf:
            text = ""
            for page in pdf.pages:
                text += page.extract_text()

    # Tokenize and preprocess the text
    encoding = tokenizer(
        text,
        padding="max_length",
        truncation=True,
        max_length=max_length,
        return_tensors="pt",
    )
    input_ids = encoding["input_ids"]
    attention_mask = encoding["attention_mask"]

    with torch.no_grad():
        redacted_output = __model(input_ids, attention_mask)
        redacted_tokens = torch.argmax(redacted_output, dim=-1)
        redacted_text = tokenizer.decode(redacted_tokens[0], skip_special_tokens=True)

    print("Redacted Text:", redacted_text)

    # Load text from PDF or image file
    def load_text_from_file(file_path):
        if file_path.endswith(".pdf"):
            with pdfplumber.open(file_path) as pdf:
                text = ""
                for page in pdf.pages:
                    text += page.extract_text()
        elif file_path.endswith((".jpg", ".jpeg", ".png", ".bmp")):
            image = Image.open(file_path)
            text = pytesseract.image_to_string(image)
        else:
            raise ValueError("Unsupported file format")
        return text

    # Replace redacted portions with placeholders
    redacted_tokens = torch.argmax(redacted_output, dim=-1)
    redacted_text = tokenizer.decode(redacted_tokens[0], skip_special_tokens=True)

    for file_path in glob.glob(file_path_dir, recursive=True):
        # Get the original text from the PDF file
        with open(file_path, "rb") as pdf_file:
            original_pdf_text = load_text_from_file(file_path)

    # Load spaCy NER model
    nlp = spacy.load("en_core_web_sm")

    def redact_pii_text(text):
        # Process the text with spaCy
        doc = nlp(text)

        # Define a set of entity labels to redact
        pii_labels = {"PERSON", "GPE", "DATE", "PHONE", "EMAIL", "EmailAddress"}

        # Redact identified PII entities from the text
        redacted_text = text
        for ent in doc.ents:
            if ent.label_ in pii_labels:
                redacted_text = redacted_text.replace(ent.text, "[REDACTED]")

        return redacted_text

    def process_file(file_path):
        if file_path.endswith((".pdf")):
            with pdfplumber.open(file_path) as pdf:
                original_text = ""
                for page in pdf.pages:
                    original_text += page.extract_text()

        elif file_path.endswith((".jpg", ".jpeg", ".png", ".bmp")):
            image = Image.open(file_path)
            original_text = pytesseract.image_to_string(image)

        else:
            print("Unsupported file format")
            return

        redacted_text = redact_pii_text(original_text)
        return redacted_text

    for file_path in glob.glob(file_path_dir, recursive=True):
        redacted_text = process_file(file_path)

    return redacted_text


def load_saved_artifacts():
    print("loading saved artifacts...start")

    global __model
    if __model is None:
        __model = RedactionModel(vocab_size, embedding_dim, hidden_dim)
        __model.load_state_dict(torch.load("models/Data Hidden/redaction_model.pth"))

    print("loading saved artifacts...done")


if __name__ == "__main__":
    load_saved_artifacts()
    print(data_hide())
