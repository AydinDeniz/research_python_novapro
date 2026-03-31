# Prompt 94

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from transformers import pipeline

app = FastAPI()

class ProductDescriptionRequest(BaseModel):
    product_name: str
    tone: str = "neutral"
    style: str = "formal"
    word_count: int = 50

generator = pipeline('text-generation', model='gpt2')

@app.post("/generate-description/")
async def generate_description(request: ProductDescriptionRequest):
    try:
        prompt = f"Generate a {request.tone} and {request.style} product description for {request.product_name} with approximately {request.word_count} words."
        result = generator(prompt, max_length=request.word_count + 50, num_return_sequences=1)
        description = result[0]['generated_text']
        return {"description": description}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))