import os
import shutil
import unicodedata
from fastapi import APIRouter, UploadFile, File, HTTPException

router = APIRouter()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """Handles multipart file uploads and saves files under the uploads/ directory."""
    try:
        # Create a safe file path inside uploads/ with normalized spaces
        safe_filename = unicodedata.normalize("NFKC", file.filename)
        file_path = os.path.join(UPLOAD_DIR, safe_filename)
        
        # Save the uploaded file to disk
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # Return a data/-relative path according to API contract
        relative_path = f"uploads/{safe_filename}"
        return {"path": relative_path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save upload: {str(e)}")