from fastapi import FastAPI, File, UploadFile, HTTPException
from pydantic import BaseModel
import pdfplumber
import docx
import spacy
from typing import List, Dict

app = FastAPI()

nlp = spacy.load("en_core_web_sm")

class ResumeSummary(BaseModel):
    education: List[str]
    skills: List[str]
    experience: List[str]

def extract_text_from_pdf(file_path):
    text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    return text

def extract_text_from_docx(file_path):
    doc = docx.Document(file_path)
    text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
    return text

def extract_resume_data(text):
    doc = nlp(text)
    
    education = []
    skills = []
    experience = []
    
    for ent in doc.ents:
        if ent.label_ == "EDUCATION":
            education.append(ent.text)
        elif ent.label_ == "SKILL":
            skills.append(ent.text)
        elif ent.label_ == "EXPERIENCE":
            experience.append(ent.text)
    
    return ResumeSummary(education=education, skills=skills, experience=experience)

@app.post("/upload-resume/")
async def upload_resume(file: UploadFile):
    if file.content_type not in ["application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]:
        raise HTTPException(status_code=400, detail="Invalid file type")
    
    file_location = f"uploaded_resumes/{file.filename}"
    with open(file_location, "wb") as f:
        f.write(await file.read())
    
    if file.content_type == "application/pdf":
        text = extract_text_from_pdf(file_location)
    else:
        text = extract_text_from_docx(file_location)
    
    resume_summary = extract_resume_data(text)
    
    return resume_summary

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)