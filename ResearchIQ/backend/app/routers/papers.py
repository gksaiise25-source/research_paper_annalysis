"""
Papers Router - Handles document uploads (PDF/DOCX), extraction, and paper management.
"""
import os
import shutil
import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks, status
from sqlalchemy.orm import Session
from loguru import logger

from app.database.session import get_db
from app.models.user import User
from app.models.paper import Paper, ExtractedContent, AnalysisStatus
from app.schemas.paper import PaperResponse, PaperListResponse, ExtractedContentResponse
from app.core.security import get_current_user
from app.core.config import settings
from app.paper_processing.extractor import PaperExtractor
from app.services.analysis_service import analysis_service

router = APIRouter(prefix="/api/papers", tags=["Papers"])
extractor = PaperExtractor()


@router.post("/upload", response_model=PaperResponse, status_code=status.HTTP_201_CREATED)
async def upload_paper(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Upload research manuscript (PDF or DOCX), extract text, and launch AI pipeline."""
    # Validate extension
    filename = file.filename or "paper.pdf"
    ext = os.path.splitext(filename)[1].lower()
    if ext not in [".pdf", ".docx"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported file format. Please upload a PDF (.pdf) or Word document (.docx)."
        )

    # Prepare upload directory
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    unique_filename = f"{uuid.uuid4().hex}_{filename}"
    file_path = os.path.join(settings.UPLOAD_DIR, unique_filename)

    # Save file to disk
    file_size = 0
    with open(file_path, "wb") as buffer:
        while chunk := await file.read(1024 * 1024):  # 1MB chunks
            file_size += len(chunk)
            if file_size > settings.MAX_FILE_SIZE_MB * 1024 * 1024:
                os.remove(file_path)
                raise HTTPException(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    detail=f"File exceeds maximum allowed size of {settings.MAX_FILE_SIZE_MB}MB."
                )
            buffer.write(chunk)

    # Extract text from document
    try:
        if ext == ".pdf":
            extracted = extractor.extract_from_pdf(file_path)
        else:
            extracted = extractor.extract_from_docx(file_path)
    except Exception as e:
        logger.error(f"Extraction failure: {e}")
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Could not extract readable text from manuscript: {str(e)}"
        )

    # Create Paper record
    paper = Paper(
        user_id=current_user.id,
        title=extracted.get("title") or filename,
        filename=filename,
        file_path=file_path,
        file_type=ext.replace(".", ""),
        file_size_bytes=file_size,
        page_count=extracted.get("page_count", 1),
        status=AnalysisStatus.PENDING,
    )
    db.add(paper)
    db.commit()
    db.refresh(paper)

    # Create ExtractedContent record
    ec = ExtractedContent(
        paper_id=paper.id,
        full_text=extracted.get("full_text"),
        abstract=extracted.get("abstract"),
        introduction=extracted.get("introduction"),
        literature_review=extracted.get("literature_review"),
        methodology=extracted.get("methodology"),
        results=extracted.get("results"),
        conclusion=extracted.get("conclusion"),
        references_text=extracted.get("references_text"),
        keywords=extracted.get("keywords"),
        sections=extracted.get("sections"),
        figures_count=extracted.get("figures_count", 0),
        tables_count=extracted.get("tables_count", 0),
        word_count=extracted.get("word_count", 0),
    )
    db.add(ec)
    db.commit()

    # Enqueue background analysis pipeline
    background_tasks.add_task(analysis_service.run_full_pipeline, db, paper.id)

    return paper


@router.get("", response_model=PaperListResponse)
def list_papers(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve list of manuscripts uploaded by the authenticated user."""
    query = db.query(Paper).filter(Paper.user_id == current_user.id)
    total = query.count()
    papers = query.order_by(Paper.created_at.desc()).offset(skip).limit(limit).all()
    return {"papers": papers, "total": total}


@router.get("/{paper_id}", response_model=PaperResponse)
def get_paper(
    paper_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve details of a single paper by ID."""
    paper = db.query(Paper).filter(Paper.id == paper_id, Paper.user_id == current_user.id).first()
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found.")
    return paper


@router.get("/{paper_id}/extracted", response_model=ExtractedContentResponse)
def get_extracted_content(
    paper_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve parsed structure and sections of the manuscript."""
    paper = db.query(Paper).filter(Paper.id == paper_id, Paper.user_id == current_user.id).first()
    if not paper or not paper.extracted_content:
        raise HTTPException(status_code=404, detail="Extracted content not found.")
    return paper.extracted_content


@router.delete("/{paper_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_paper(
    paper_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a paper, its extracted content, and all analysis records."""
    paper = db.query(Paper).filter(Paper.id == paper_id, Paper.user_id == current_user.id).first()
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found.")

    if os.path.exists(paper.file_path):
        try:
            os.remove(paper.file_path)
        except Exception as e:
            logger.warning(f"Could not delete physical file: {e}")

    db.delete(paper)
    db.commit()
    return None
