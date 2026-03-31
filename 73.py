# Prompt 73

from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
import pandas as pd
import numpy as np
import io

app = FastAPI()

@app.post("/upload-csv/")
async def upload_csv(file: UploadFile = File(...)):
    if not file.filename.endswith(".csv"):
        return JSONResponse(status_code=400, content={"message": "Invalid file type"})

    contents = await file.read()
    data = pd.read_csv(io.StringIO(contents.decode("utf-8")))

    summary_stats = {
        "mean": data.mean().to_dict(),
        "median": data.median().to_dict(),
        "std": data.std().to_dict(),
        "min": data.min().to_dict(),
        "max": data.max().to_dict(),
    }

    return JSONResponse(content=summary_stats)

@app.get("/summary-stats/")
async def get_summary_stats():
    # Example data for demonstration purposes
    data = pd.DataFrame({
        "A": [1, 2, 3, 4, 5],
        "B": [5, 6, 7, 8, 9],
    })

    summary_stats = {
        "mean": data.mean().to_dict(),
        "median": data.median().to_dict(),
        "std": data.std().to_dict(),
        "min": data.min().to_dict(),
        "max": data.max().to_dict(),
    }

    return JSONResponse(content=summary_stats)