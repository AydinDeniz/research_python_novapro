from fastapi import FastAPI, File, UploadFile, HTTPException
from pydantic import BaseModel
from typing import Any
import pickle
import os
import datetime
from bson import ObjectId
from pymongo import MongoClient

app = FastAPI()

# MongoDB setup
client = MongoClient("mongodb://localhost:27017")
db = client["processing_db"]
collection = db["processing_metadata"]

# Shared filesystem location
SHARED_FS_LOCATION = "/path/to/shared/fs"

class ProcessingMetadata(BaseModel):
    uploader: str
    timestamp: datetime.datetime
    result_path: str

@app.post("/process/")
async def process_pkl(file: UploadFile = File(...), uploader: str = "anonymous"):
    if not file.filename.endswith(".pkl"):
        raise HTTPException(status_code=400, detail="Invalid file type. Only .pkl files are accepted.")
    
    try:
        # Read and deserialize the .pkl file
        contents = await file.read()
        loaded_obj = pickle.loads(contents)
        
        # Check if the object has a process function
        if not hasattr(loaded_obj, "process"):
            raise HTTPException(status_code=400, detail="The uploaded object does not contain a 'process' function.")
        
        # Invoke the process function
        result = loaded_obj.process(context={})  # Assuming context is an empty dict for simplicity
        
        # Write the result to the shared filesystem
        result_filename = f"result_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.pkl"
        result_path = os.path.join(SHARED_FS_LOCATION, result_filename)
        with open(result_path, "wb") as f:
            pickle.dump(result, f)
        
        # Record processing metadata
        timestamp = datetime.datetime.now()
        metadata = ProcessingMetadata(uploader=uploader, timestamp=timestamp, result_path=result_path)
        collection.insert_one(metadata.dict())
        
        return {"message": "Processing successful", "metadata": metadata.dict()}
    
    except pickle.PickleError as e:
        raise HTTPException(status_code=400, detail=f"Error deserializing the .pkl file: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred during processing: {str(e)}")