import spacy
import PyPDF2
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

# Function to extract text from PDF
def extract_text_from_pdf(pdf_path):
    with open(pdf_path, "rb") as file:
        reader = PyPDF2.PdfFileReader(file)
        text = ""
        for page_num in range(reader.numPages):
            page = reader.getPage(page_num)
            text += page.extract_text()
    return text

# Function to extract key details from resume
def extract_details(resume_text):
    doc = nlp(resume_text)
    skills = []
    experience = []
    education = []
    for ent in doc.ents:
        if ent.label_ == "SKILL":
            skills.append(ent.text)
        elif ent.label_ == "WORK_EXPERIENCE":
            experience.append(ent.text)
        elif ent.label_ == "EDUCATION":
            education.append(ent.text)
    return skills, experience, education

# Function to preprocess text
def preprocess_text(text):
    tokens = word_tokenize(text)
    tokens = [word.lower() for word in tokens if word.isalpha()]
    tokens = [word for word in tokens if word not in stopwords.words("english")]
    return " ".join(tokens)

# Function to calculate similarity
def calculate_similarity(candidate_details, job_description):
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform([candidate_details, job_description])
    similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
    return similarity[0][0]

# Main function to screen resumes
def screen_resumes(pdf_resumes, job_description):
    ranked_candidates = []
    for pdf_resume in pdf_resumes:
        resume_text = extract_text_from_pdf(pdf_resume)
        skills, experience, education = extract_details(resume_text)
        candidate_details = " ".join(skills + experience + education)
        preprocessed_candidate_details = preprocess_text(candidate_details)
        preprocessed_job_description = preprocess_text(job_description)
        similarity_score = calculate_similarity(preprocessed_candidate_details, preprocessed_job_description)
        ranked_candidates.append((pdf_resume, similarity_score))
    ranked_candidates.sort(key=lambda x: x[1], reverse=True)
    return ranked_candidates

# Example usage
pdf_resumes = ["resume1.pdf", "resume2.pdf", "resume3.pdf"]
job_description = "We are looking for a Python developer with experience in machine learning and data science."
ranked_candidates = screen_resumes(pdf_resumes, job_description)
for candidate, score in ranked_candidates:
    print(f"Candidate: {candidate}, Similarity Score: {score}")