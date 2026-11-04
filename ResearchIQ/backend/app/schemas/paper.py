from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional, Any, Dict, List
from app.models.paper import AnalysisStatus


class PaperResponse(BaseModel):
    id: int
    title: Optional[str]
    filename: str
    file_type: str
    file_size_bytes: Optional[int]
    page_count: Optional[int]
    status: AnalysisStatus
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PaperListResponse(BaseModel):
    papers: List[PaperResponse]
    total: int


class ExtractedContentResponse(BaseModel):
    abstract: Optional[str]
    introduction: Optional[str]
    methodology: Optional[str]
    conclusion: Optional[str]
    keywords: Optional[List[str]]
    word_count: Optional[int]
    figures_count: int
    tables_count: int

    model_config = ConfigDict(from_attributes=True)


class AnalysisResultResponse(BaseModel):
    id: int
    analysis_type: str
    status: AnalysisStatus
    result_data: Optional[Dict[str, Any]]
    score: Optional[float]
    error_message: Optional[str]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class FullReportResponse(BaseModel):
    paper: PaperResponse
    extracted_content: Optional[ExtractedContentResponse]
    analyses: Dict[str, Optional[AnalysisResultResponse]]
