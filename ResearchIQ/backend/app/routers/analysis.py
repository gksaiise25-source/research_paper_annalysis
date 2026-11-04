"""
Analysis Router - Triggers and fetches results for all 10 analysis features, plus PDF report download.
"""
from typing import Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session
from loguru import logger

from app.database.session import get_db
from app.models.user import User
from app.models.paper import Paper, AnalysisResult, AnalysisStatus
from app.schemas.paper import AnalysisResultResponse, FullReportResponse
from app.core.security import get_current_user
from app.services.analysis_service import analysis_service
from app.services.report_generator import PDFReportGenerator

router = APIRouter(prefix="/api/analysis", tags=["Analysis"])
report_generator = PDFReportGenerator()


def _get_user_paper(paper_id: int, user_id: int, db: Session) -> Paper:
    paper = db.query(Paper).filter(Paper.id == paper_id, Paper.user_id == user_id).first()
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found or unauthorized.")
    return paper


@router.get("/history")
def get_analysis_history(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve full analysis history with publication readiness scores for the user."""
    papers = (
        db.query(Paper)
        .filter(Paper.user_id == current_user.id)
        .order_by(Paper.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    history_items = []
    for p in papers:
        readiness_record = (
            db.query(AnalysisResult)
            .filter(AnalysisResult.paper_id == p.id, AnalysisResult.analysis_type == "readiness")
            .first()
        )
        score = readiness_record.score if readiness_record else None
        rec_data = readiness_record.result_data if readiness_record else {}
        category = rec_data.get("readiness_category") if rec_data else None

        history_items.append({
            "paper_id": p.id,
            "title": p.title,
            "filename": p.filename,
            "created_at": p.created_at,
            "status": p.status,
            "readiness_score": score,
            "readiness_category": category,
            "page_count": p.page_count,
        })

    return {"history": history_items, "total": len(history_items)}


@router.get("/{paper_id}/results")
def get_paper_analyses(
    paper_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve all available analysis module results for a given paper."""
    paper = _get_user_paper(paper_id, current_user.id, db)
    results = db.query(AnalysisResult).filter(AnalysisResult.paper_id == paper.id).all()

    analyses_map = {}
    for r in results:
        analyses_map[r.analysis_type] = {
            "status": r.status,
            "score": r.score,
            "result_data": r.result_data,
            "error_message": r.error_message,
            "updated_at": r.updated_at or r.created_at,
        }

    return {
        "paper_id": paper.id,
        "title": paper.title,
        "status": paper.status,
        "analyses": analyses_map,
    }


# Individual Feature Trigger Endpoints
@router.post("/{paper_id}/technical-review")
async def trigger_technical_review(
    paper_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    paper = _get_user_paper(paper_id, current_user.id, db)
    return await analysis_service.run_single_analysis(db, paper, "technical_review")


@router.post("/{paper_id}/novelty")
async def trigger_novelty(
    paper_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    paper = _get_user_paper(paper_id, current_user.id, db)
    return await analysis_service.run_single_analysis(db, paper, "novelty")


@router.post("/{paper_id}/citations")
async def trigger_citations(
    paper_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    paper = _get_user_paper(paper_id, current_user.id, db)
    return await analysis_service.run_single_analysis(db, paper, "citations")


@router.post("/{paper_id}/grammar")
async def trigger_grammar(
    paper_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    paper = _get_user_paper(paper_id, current_user.id, db)
    return await analysis_service.run_single_analysis(db, paper, "grammar")


@router.post("/{paper_id}/plagiarism")
async def trigger_plagiarism(
    paper_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    paper = _get_user_paper(paper_id, current_user.id, db)
    return await analysis_service.run_single_analysis(db, paper, "plagiarism")


@router.post("/{paper_id}/figures-tables")
async def trigger_figures_tables(
    paper_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    paper = _get_user_paper(paper_id, current_user.id, db)
    return await analysis_service.run_single_analysis(db, paper, "figures_tables")


@router.post("/{paper_id}/reviewer-comments")
async def trigger_reviewer_comments(
    paper_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    paper = _get_user_paper(paper_id, current_user.id, db)
    return await analysis_service.run_single_analysis(db, paper, "reviewer_comments")


@router.post("/{paper_id}/journals")
async def trigger_journals(
    paper_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    paper = _get_user_paper(paper_id, current_user.id, db)
    return await analysis_service.run_single_analysis(db, paper, "journals")


@router.post("/{paper_id}/patentability")
async def trigger_patentability(
    paper_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    paper = _get_user_paper(paper_id, current_user.id, db)
    return await analysis_service.run_single_analysis(db, paper, "patentability")


@router.post("/{paper_id}/readiness")
async def trigger_readiness(
    paper_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    paper = _get_user_paper(paper_id, current_user.id, db)
    return await analysis_service.run_single_analysis(db, paper, "readiness")


@router.get("/{paper_id}/report")
def download_pdf_report(
    paper_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Generate and download executive PDF evaluation report for the paper."""
    paper = _get_user_paper(paper_id, current_user.id, db)
    results = db.query(AnalysisResult).filter(AnalysisResult.paper_id == paper.id).all()

    analyses_dict = {}
    for r in results:
        if r.result_data:
            analyses_dict[r.analysis_type] = r.result_data

    # Generate PDF bytes
    pdf_bytes = report_generator.generate(
        paper=paper,
        extracted=paper.extracted_content,
        analyses=analyses_dict
    )

    clean_filename = f"ResearchIQ_Report_{paper.id}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename={clean_filename}"
        }
    )
