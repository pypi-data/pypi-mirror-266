# utils.py
from transformers import pipeline
import torch
import pandas as pd
from io import BytesIO
import base64

# Initialize the tokenizer and model globally to avoid reloading them every time the function is called

device = "cuda:0" if torch.cuda.is_available() else "cpu"

pipe = pipeline("token-classification", model="Isotonic/mdeberta-v3-base_finetuned_ai4privacy_v2", max_length=512, device=device)

def process_column(texts):
    processed_texts = []
    for text in texts:
        model_output = pipe(text)
        merged_entities = []
        for i, token in enumerate(model_output):
            if i == 0 or (model_output[i-1]['end'] == token['start'] and model_output[i-1]['entity'] == token['entity']):
                if merged_entities and model_output[i-1]['entity'] == token['entity']:
                    merged_entities[-1]['word'] += text[token['start']:token['end']]
                    merged_entities[-1]['end'] = token['end']
                else:
                    merged_entities.append(token.copy())  # Copy to avoid modifying the original token
                    merged_entities[-1]['word'] = text[token['start']:token['end']]
            else:
                merged_entities.append(token.copy())  # Copy to avoid modifying the original token
                merged_entities[-1]['word'] = text[token['start']:token['end']]

        for entity in merged_entities:
            text = text.replace(entity['word'], f"[REDACTED {entity['entity']}]")

        processed_texts.append(text)

    return processed_texts

def modify_csv(file):
    df = pd.read_csv(file)
    if "Customer Name" in df.columns:
        df["Customer Name"] = process_column(df["Customer Name"])
    if "Customer Email" in df.columns:
        df["Customer Email"] = process_column(df["Customer Email"])

    output = BytesIO()
    df.to_csv(output, index=False)
    output.seek(0)

    return df

def image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')
