from fastapi import FastAPI, Query
from pydantic import BaseModel
from typing import List
import os
import concurrent.futures
import pythoncom
from docx import Document
from PyPDF2 import PdfFileReader
import magic

app = FastAPI()

class DocumentMetadata(BaseModel):
    title: str
    author: str
    creation_date: str
    file_path: str

documents_metadata = []

def extract_metadata_from_docx(file_path):
    doc = Document(file_path)
    core_properties = doc.core_properties
    return DocumentMetadata(
        title=core_properties.title,
        author=core_properties.author,
        creation_date=str(core_properties.created),
        file_path=file_path
    )

def extract_metadata_from_pdf(file_path):
    with open(file_path, 'rb') as f:
        pdf = PdfFileReader(f)
        document_info = pdf.getDocumentInfo()
        return DocumentMetadata(
            title=document_info.get('/Title', ''),
            author=document_info.get('/Author', ''),
            creation_date=str(document_info.get('/CreationDate', '')),
            file_path=file_path
        )

def extract_metadata(file_path):
    file_type = magic.from_file(file_path, mime=True)
    if file_type == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
        return extract_metadata_from_docx(file_path)
    elif file_type == 'application/pdf':
        return extract_metadata_from_pdf(file_path)
    else:
        return None

def scan_folder(folder_path):
    pythoncom.CoInitialize()
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []
        for root, _, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                futures.append(executor.submit(extract_metadata, file_path))
        
        for future in concurrent.futures.as_completed(futures):
            metadata = future.result()
            if metadata:
                documents_metadata.append(metadata)

@app.on_event("startup")
async def startup_event():
    folder_path = "path_to_your_folder"
    scan_folder(folder_path)

@app.get("/documents", response_model=List[DocumentMetadata])
async def get_documents(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, gt=0),
    title: str = None,
    author: str = None
):
    filtered_documents = documents_metadata
    if title:
        filtered_documents = [doc for doc in filtered_documents if title.lower() in doc.title.lower()]
    if author:
        filtered_documents = [doc for doc in filtered_documents if author.lower() in doc.author.lower()]
    
    total_documents = len(filtered_documents)
    start_index = (page - 1) * page_size
    end_index = start_index + page_size
    paginated_documents = filtered_documents[start_index:end_index]
    
    return {
        "total": total_documents,
        "page": page,
        "page_size": page_size,
        "documents": paginated_documents
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)