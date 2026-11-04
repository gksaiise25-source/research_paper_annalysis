from sqlalchemy import (
    Column, Integer, String, DateTime, Float, Text, ForeignKey, JSON, Enum
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.database.session import Base


class AnalysisStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class Paper(Base):
    __tablename__ = "papers"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=True)
    filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    file_type = Column(String, nullable=False)
    file_size_bytes = Column(Integer, nullable=True)
    page_count = Column(Integer, nullable=True)
    status = Column(Enum(AnalysisStatus), default=AnalysisStatus.PENDING)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    owner = relationship("User", back_populates="papers")
    extracted_content = relationship("ExtractedContent", back_populates="paper", uselist=False)
    analysis_results = relationship("AnalysisResult", back_populates="paper")


class ExtractedContent(Base):
    __tablename__ = "extracted_contents"

    id = Column(Integer, primary_key=True, index=True)
    paper_id = Column(Integer, ForeignKey("papers.id"), unique=True, nullable=False)
    full_text = Column(Text, nullable=True)
    abstract = Column(Text, nullable=True)
    introduction = Column(Text, nullable=True)
    literature_review = Column(Text, nullable=True)
    methodology = Column(Text, nullable=True)
    results = Column(Text, nullable=True)
    conclusion = Column(Text, nullable=True)
    references_text = Column(Text, nullable=True)
    keywords = Column(JSON, nullable=True)
    sections = Column(JSON, nullable=True)
    figures_count = Column(Integer, default=0)
    tables_count = Column(Integer, default=0)
    word_count = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    paper = relationship("Paper", back_populates="extracted_content")


class AnalysisResult(Base):
    __tablename__ = "analysis_results"

    id = Column(Integer, primary_key=True, index=True)
    paper_id = Column(Integer, ForeignKey("papers.id"), nullable=False)
    analysis_type = Column(String, nullable=False)  # e.g. "technical_review", "novelty", etc.
    status = Column(Enum(AnalysisStatus), default=AnalysisStatus.PENDING)
    result_data = Column(JSON, nullable=True)
    score = Column(Float, nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    paper = relationship("Paper", back_populates="analysis_results")
