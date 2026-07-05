from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from app.ai.rag_pipeline import RAGPipeline
from app.auth.dependencies import get_current_user
from app.db.mongo import get_database
import pypdf
import io
from datetime import datetime

router = APIRouter(prefix="/upload", tags=["Upload"])

@router.post("/")
async def upload_document(file: UploadFile = File(...), user: dict = Depends(get_current_user)):
    content = await file.read()
    text = ""
    
    if file.filename.endswith(".pdf"):
        pdf_reader = pypdf.PdfReader(io.BytesIO(content))
        for page in pdf_reader.pages:
            text += page.extract_text()
    elif file.filename.endswith(".txt"):
        text = content.decode("utf-8")
    else:
        raise HTTPException(status_code=400, detail="Unsupported file type")

    rag = RAGPipeline()
    chunks_count = await rag.ingest_text(text, {"filename": file.filename, "uploaded_by": user["email"]})
    
    # Record in Mongo
    db = get_database()
    await db.documents.insert_one({
        "filename": file.filename,
        "uploaded_by": user["email"],
        "chunks_count": chunks_count,
        "created_at": datetime.utcnow()
    })
    
    return {"message": f"Successfully ingested {file.filename}", "chunks": chunks_count}
