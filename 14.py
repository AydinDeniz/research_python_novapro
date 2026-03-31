import spacy
import openai
import os

# Set up spaCy and OpenAI API
nlp = spacy.load("en_core_web_sm")
openai.api_key = os.getenv("OPENAI_API_KEY")

# Preprocess text using spaCy
def preprocess_text(text):
    doc = nlp(text)
    sentences = [sent.text for sent in doc.sents]
    return sentences

# Generate abstractive summary using GPT-3.5
def generate_abstractive_summary(text, max_tokens=150):
    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=f"Summarize the following text:\n\n{text}\n\nSummary:",
        max_tokens=max_tokens,
        temperature=0.7,
        n=1,
        stop=None,
    )
    return response.choices[0].text.strip()

# Generate extractive summary using spaCy
def generate_extractive_summary(sentences, ratio=0.2):
    doc = nlp(" ".join(sentences))
    summary = " ".join(sent.text for sent in doc.sents if sent.text in sentences[:int(len(sentences) * ratio)])
    return summary

# Main function
def summarize_document(text, method="abstractive"):
    sentences = preprocess_text(text)
    if method == "abstractive":
        summary = generate_abstractive_summary(text)
    elif method == "extractive":
        summary = generate_extractive_summary(sentences)
    else:
        raise ValueError("Invalid summarization method. Choose 'abstractive' or 'extractive'.")
    return summary

# Example usage
text = """
Your large text document goes here.
"""
summary = summarize_document(text, method="abstractive")
print("Abstractive Summary:", summary)

summary = summarize_document(text, method="extractive")
print("Extractive Summary:", summary)