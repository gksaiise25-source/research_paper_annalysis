"""
Central Analysis Coordinator Service.
Executes individual analysis modules or full pipeline, saving results directly to PostgreSQL.
"""
import asyncio
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from loguru import logger

from app.models.paper import Paper, ExtractedContent, AnalysisResult, AnalysisStatus
from app.ai_engine.technical_review.reviewer import TechnicalReviewer
from app.ai_engine.novelty_analysis.analyser import NoveltyAnalyser
from app.ai_engine.citation_analysis.analyser import CitationAnalyser
from app.ai_engine.grammar_analysis.analyser import GrammarAnalyser
from app.ai_engine.plagiarism_detection.detector import PlagiarismDetector
from app.ai_engine.figure_validation.validator import FigureTableValidator
from app.ai_engine.reviewer_generation.generator import ReviewerGenerator
from app.ai_engine.journal_recommendation.recommender import JournalRecommender
from app.ai_engine.patentability.evaluator import PatentabilityEvaluator
from app.ai_engine.readiness_scoring.scorer import ReadinessScorer


class AnalysisService:
    """Manages execution and persistence of all 10 analytical modules."""

    def __init__(self):
        self.technical_reviewer = TechnicalReviewer()
        self.novelty_analyser = NoveltyAnalyser()
        self.citation_analyser = CitationAnalyser()
        self.grammar_analyser = GrammarAnalyser()
        self.plagiarism_detector = PlagiarismDetector()
        self.figure_validator = FigureTableValidator()
        self.reviewer_generator = ReviewerGenerator()
        self.journal_recommender = JournalRecommender()
        self.patentability_evaluator = PatentabilityEvaluator()
        self.readiness_scorer = ReadinessScorer()

    def get_extracted_dict(self, paper: Paper) -> Dict[str, Any]:
        """Convert ExtractedContent ORM model into dictionary for engines."""
        ec = paper.extracted_content
        if not ec:
            return {}
        return {
            "title": paper.title or "",
            "full_text": ec.full_text or "",
            "abstract": ec.abstract or "",
            "introduction": ec.introduction or "",
            "literature_review": ec.literature_review or "",
            "methodology": ec.methodology or "",
            "results": ec.results or "",
            "conclusion": ec.conclusion or "",
            "references_text": ec.references_text or "",
            "keywords": ec.keywords or [],
            "word_count": ec.word_count or 0,
            "figures_count": ec.figures_count or 0,
            "tables_count": ec.tables_count or 0,
        }

    def save_or_update_result(
        self, db: Session, paper_id: int, analysis_type: str, status: AnalysisStatus,
        result_data: Optional[Dict] = None, score: Optional[float] = None, error: Optional[str] = None
    ) -> AnalysisResult:
        """Persist or update analysis record in database."""
        result = db.query(AnalysisResult).filter(
            AnalysisResult.paper_id == paper_id,
            AnalysisResult.analysis_type == analysis_type
        ).first()

        if not result:
            result = AnalysisResult(
                paper_id=paper_id,
                analysis_type=analysis_type,
                status=status,
                result_data=result_data,
                score=score,
                error_message=error
            )
            db.add(result)
        else:
            result.status = status
            result.result_data = result_data
            result.score = score
            result.error_message = error

        db.commit()
        db.refresh(result)
        return result

    async def run_single_analysis(self, db: Session, paper: Paper, analysis_type: str) -> Dict[str, Any]:
        """Execute a specific analysis module by name."""
        extracted = self.get_extracted_dict(paper)
        if not extracted or not extracted.get("full_text"):
            raise ValueError("No extracted text available for this paper. Please re-upload or wait for extraction.")

        # Mark in progress
        self.save_or_update_result(db, paper.id, analysis_type, AnalysisStatus.PROCESSING)

        try:
            if analysis_type == "technical_review":
                data = self.technical_reviewer.analyse(extracted)
                score = data.get("overall_score")
            elif analysis_type == "novelty":
                data = await self.novelty_analyser.analyse(extracted)
                score = data.get("overall_novelty_score")
            elif analysis_type == "citations":
                data = self.citation_analyser.analyse(extracted)
                score = data.get("citation_score")
            elif analysis_type == "grammar":
                data = self.grammar_analyser.analyse(extracted)
                score = data.get("grammar_score")
            elif analysis_type == "plagiarism":
                data = self.plagiarism_detector.analyse(extracted)
                score = data.get("originality_indicator")
            elif analysis_type == "figures_tables":
                data = self.figure_validator.validate(paper.file_path, extracted)
                score = data.get("validation_score")
            elif analysis_type == "reviewer_comments":
                data = await self.reviewer_generator.generate_review(extracted)
                score = 85.0 if data.get("recommendation") == "Accept" else (
                    70.0 if "Minor" in data.get("recommendation", "") else 50.0
                )
            elif analysis_type == "journals":
                data = await self.journal_recommender.recommend(extracted)
                score = 80.0
            elif analysis_type == "patentability":
                data = self.patentability_evaluator.evaluate(extracted)
                score = data.get("overall_patentability_score")
            elif analysis_type == "readiness":
                # Gather existing results to score readiness
                all_results = {}
                db_results = db.query(AnalysisResult).filter(AnalysisResult.paper_id == paper.id).all()
                for r in db_results:
                    if r.result_data and r.status == AnalysisStatus.COMPLETED:
                        all_results[r.analysis_type] = r.result_data
                data = self.readiness_scorer.calculate_readiness(all_results)
                score = data.get("overall_score")
            else:
                raise ValueError(f"Unknown analysis type: {analysis_type}")

            record = self.save_or_update_result(
                db, paper.id, analysis_type, AnalysisStatus.COMPLETED,
                result_data=data, score=score
            )
            return data

        except Exception as e:
            logger.error(f"Error in {analysis_type} for paper {paper.id}: {e}")
            self.save_or_update_result(
                db, paper.id, analysis_type, AnalysisStatus.FAILED, error=str(e)
            )
            raise

    async def run_full_pipeline(self, db: Session, paper_id: int):
        """Run all 10 analysis steps sequentially and compute readiness."""
        paper = db.query(Paper).filter(Paper.id == paper_id).first()
        if not paper:
            logger.error(f"Paper {paper_id} not found for pipeline run")
            return

        paper.status = AnalysisStatus.PROCESSING
        db.commit()

        analysis_steps = [
            "technical_review",
            "novelty",
            "citations",
            "grammar",
            "plagiarism",
            "figures_tables",
            "reviewer_comments",
            "journals",
            "patentability",
        ]

        for step in analysis_steps:
            try:
                logger.info(f"Running {step} for paper {paper_id}")
                await self.run_single_analysis(db, paper, step)
            except Exception as e:
                logger.error(f"Pipeline error at step {step}: {e}")

        # Finally calculate publication readiness
        try:
            logger.info(f"Computing final readiness score for paper {paper_id}")
            await self.run_single_analysis(db, paper, "readiness")
            paper.status = AnalysisStatus.COMPLETED
        except Exception as e:
            logger.error(f"Failed to calculate publication readiness: {e}")
            paper.status = AnalysisStatus.FAILED

        db.commit()


analysis_service = AnalysisService()
