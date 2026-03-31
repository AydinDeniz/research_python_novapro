import PyPDF2
from pdfminer.high_level import extract_text
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from PIL import Image
import io
import json
import os

def extract_text_from_pdf(pdf_path):
    text = extract_text(pdf_path, laparams=LAParams())
    return text

def extract_images_from_pdf(pdf_path):
    images = []
    with open(pdf_path, "rb") as file:
        reader = PyPDF2.PdfFileReader(file)
        for page_num in range(reader.numPages):
            page = reader.getPage(page_num)
            xObject = page["/Resources"]["/XObject"]
            if xObject:
                for obj in xObject:
                    if xObject[obj]["/Subtype"] == "/Image":
                        size = (xObject[obj]["/Width"], xObject[obj]["/Height"])
                        data = xObject[obj].getData()
                        image_mode = "RGB" if xObject[obj]["/ColorSpace"] == "/DeviceRGB" else "P"
                        image = Image.frombytes(image_mode, size, data)
                        image_bytes = io.BytesIO()
                        image.save(image_bytes, format="PNG")
                        images.append(image_bytes.getvalue())
    return images

def extract_metadata_from_pdf(pdf_path):
    with open(pdf_path, "rb") as file:
        reader = PyPDF2.PdfFileReader(file)
        metadata = reader.getDocumentInfo()
        return metadata

def parse_pdf(pdf_path):
    text = extract_text_from_pdf(pdf_path)
    images = extract_images_from_pdf(pdf_path)
    metadata = extract_metadata_from_pdf(pdf_path)
    
    structured_output = {
        "text": text,
        "images": [img.hex() for img in images],  # Store images as hex strings
        "metadata": metadata
    }
    
    return structured_output

def save_to_json(data, output_path):
    with open(output_path, "w") as file:
        json.dump(data, file, indent=4)

if __name__ == "__main__":
    pdf_path = "example.pdf"
    output_path = "output.json"
    
    parsed_data = parse_pdf(pdf_path)
    save_to_json(parsed_data, output_path)
    print(f"Parsed data saved to {output_path}")