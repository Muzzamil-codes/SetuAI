import os
import shutil
from fastapi import APIRouter, UploadFile, File, HTTPException

router = APIRouter()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """Handles multipart file uploads and saves files under the uploads/ directory."""
    try:
        # Create a safe file path inside uploads/
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        
        # Save the uploaded file to disk
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # Return a data/-relative path according to API contract
        relative_path = f"uploads/{file.filename}"
        return {"path": relative_path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save upload: {str(e)}")