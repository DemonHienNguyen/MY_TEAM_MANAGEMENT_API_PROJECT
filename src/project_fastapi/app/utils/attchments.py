import os
from pathlib import Path
from uuid import uuid4

from fastapi import File, HTTPException, UploadFile, status

from ..core import setting

BASE_DIR = Path(__file__).resolve().parent.parent
UPLOAD_DIR= BASE_DIR / setting.UPLOAD_DIR

async def save_a_file(file: UploadFile = File(...)) -> tuple[str, str | None, int]:
    ext = Path(file.filename).suffix.lower()
    if ext not in setting.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Định dạng file không hỗ trợ !",
                "error": f"JUST ALLOWED SOME EXTENTION LIKE : {", ".join(setting.ALLOWED_EXTENSIONS)}"
            }
        )
    if file.content_type not in setting.ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Loại file MINE không hợp lệ !",
                "error": "NOT ALLOWED THIS MINE !"
            }
        )
    conten = await file.read()
    file_size = len(conten)
    if file_size > setting.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "file vượt mức dữ liệu cho phép !",
                "error": f"THIS FILE IS TO BIG, ONLY UNDER {setting.MAX_FILE_SIZE / (1024  * 1024)}MB"
            }
        )
    unique_file_name = f"{uuid4().hex}{ext}"
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    file_path = os.path.join(UPLOAD_DIR, unique_file_name)
    
    with open(file_path, "wb") as Bust:
        Bust.write(conten)
        
    return file_path, file.filename, file_size, 
        