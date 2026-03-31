# Prompt 89

from fastapi import FastAPI, File, UploadFile
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.future import select
from sqlalchemy.orm import sessionmaker
import pandas as pd
import asyncio

app = FastAPI()

# Database setup
DATABASE_URL = "postgresql+asyncpg://username:password@localhost/dbname"
engine = create_async_engine(DATABASE_URL, echo=True)
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

# Pydantic model for validation
class Record(BaseModel):
    column1: str
    column2: int

# Function to validate data
def validate_data(data: pd.DataFrame) -> list:
    records = []
    for _, row in data.iterrows():
        try:
            record = Record(**row)
            records.append(record)
        except ValueError:
            pass
    return records

# Function to insert data into database
async def insert_data(records: list):
    async with async_session() as session:
        for record in records:
            await session.execute(
                "INSERT INTO table_name (column1, column2) VALUES (:column1, :column2)",
                {"column1": record.column1, "column2": record.column2}
            )
        await session.commit()

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    if file.content_type!= "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
        return {"error": "Invalid file type"}
    
    data = pd.read_excel(file.file)
    valid_records = validate_data(data)
    
    await insert_data(valid_records)
    
    return {"message": "Data processed successfully"}