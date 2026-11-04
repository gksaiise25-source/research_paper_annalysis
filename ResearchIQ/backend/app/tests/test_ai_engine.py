"""
Unit tests for ResearchIQ AI evaluation modules.
Verifies determinism, scoring logic, and structural analysis without external network dependency.
"""
import pytest
from app.ai_engine.technical_review.reviewer import TechnicalReviewer
from app.ai_engine.citation_analysis.analyser import CitationAnalyser
from app.ai_engine.grammar_analysis.analyser import GrammarAnalyser
from app.ai_engine.plagiarism_detection.detector import PlagiarismDetector
from app.ai_engine.figure_validation.validator import FigureTableValidator
from app.ai_engine.patentability.evaluator import PatentabilityEvaluator
from app.ai_engine.readiness_scoring.scorer import ReadinessScorer


SAMPLE_PAPER_CONTENT = {
    "title": "Quantum Deep Learning: Robust Optimization for High-Dimensional Tensor State Classification",
    "full_text": """
Abstract: In this work, we propose a novel quantum deep learning architecture designed for tensor state classification.
Our objective is to minimize quantum gate decoherence while maximizing gradient throughput. We evaluate the proposed method
on synthetic and benchmark quantum state representations. Results demonstrate an accuracy improvement of 14.2% over existing classical baselines.
In conclusion, the proposed framework shows substantial promise for scalable quantum tensor processing.

1. Introduction: High-dimensional quantum state classification represents a fundamental challenge in computational physics.
Traditional tensor network contractions suffer from exponential scaling. To address this problem, we present an algorithmic breakthrough
based on parameterized variational circuits. Our primary contribution is a novel tensor decomposition layer that reduces gate depth.
Related work by Smith et al. [1] and Johnson [2] explored shallow circuits, but failed to address barren plateaus.

2. Methodology: We formulate the parameterization of our quantum ansatz using an interleaved circuit architecture.
A dataset consisting of 10,000 synthetic quantum density matrices was generated. The training objective minimizes cross-entropy loss
using the Adam optimizer with a learning rate of 0.001. Hardware simulations were performed on a 32-qubit tensor simulator.

3. Results: As illustrated in Fig. 1, our proposed architecture achieves 94.5% classification accuracy on test tensors.
Table 1 outlines comparative latency metrics against standard variational algorithms. Statistical significance was verified with p < 0.01.

4. Conclusion: We have demonstrated a novel approach to tensor state classification. Future work will investigate fault-tolerant quantum error correction.

References:
[1] A. Smith, B. Doe, "Quantum tensor contractions," Journal of Quantum Info, vol. 12, pp. 45-52, 2022.
[2] C. Johnson, "Variational quantum circuits," IEEE Trans. Quantum Eng., vol. 3, pp. 100-110, 2023.
    """,
    "abstract": "In this work, we propose a novel quantum deep learning architecture designed for tensor state classification. Our objective is to minimize quantum gate decoherence while maximizing gradient throughput. We evaluate the proposed method on synthetic and benchmark quantum state representations. Results demonstrate an accuracy improvement of 14.2% over existing classical baselines. In conclusion, the proposed framework shows substantial promise for scalable quantum tensor processing.",
    "introduction": "High-dimensional quantum state classification represents a fundamental challenge in computational physics. Traditional tensor network contractions suffer from exponential scaling. To address this problem, we present an algorithmic breakthrough based on parameterized variational circuits. Our primary contribution is a novel tensor decomposition layer that reduces gate depth.",
    "literature_review": "Related work by Smith et al. [1] and Johnson [2] explored shallow circuits, but failed to address barren plateaus.",
    "methodology": "We formulate the parameterization of our quantum ansatz using an interleaved circuit architecture. A dataset consisting of 10,000 synthetic quantum density matrices was generated. The training objective minimizes cross-entropy loss using the Adam optimizer with a learning rate of 0.001.",
    "results": "As illustrated in Fig. 1, our proposed architecture achieves 94.5% classification accuracy on test tensors. Table 1 outlines comparative latency metrics against standard variational algorithms.",
    "conclusion": "We have demonstrated a novel approach to tensor state classification. Future work will investigate fault-tolerant quantum error correction.",
    "references_text": "[1] A. Smith, B. Doe, 'Quantum tensor contractions', 2022.\n[2] C. Johnson, 'Variational quantum circuits', 2023.",
    "references_list": [
        "[1] A. Smith, B. Doe, 'Quantum tensor contractions', 2022.",
        "[2] C. Johnson, 'Variational quantum circuits', 2023."
    ],
    "keywords": ["Quantum Computing", "Deep Learning", "Tensor States"],
    "word_count": 420,
    "figures_count": 1,
    "tables_count": 1,
}


def test_technical_reviewer():
    reviewer = TechnicalReviewer()
    result = reviewer.analyse(SAMPLE_PAPER_CONTENT)
    assert "overall_score" in result
    assert result["overall_score"] > 40.0
    assert "abstract" in result["section_analyses"]
    assert result["section_analyses"]["abstract"]["present"] is True


def test_citation_analyser():
    analyser = CitationAnalyser()
    result = analyser.analyse(SAMPLE_PAPER_CONTENT)
    assert result["detected_style"] == "IEEE"
    assert result["total_references"] >= 2
    assert "citation_score" in result


def test_grammar_analyser():
    analyser = GrammarAnalyser()
    result = analyser.analyse(SAMPLE_PAPER_CONTENT)
    assert "grammar_score" in result
    assert "academic_tone_score" in result
    assert result["grammar_score"] > 60.0


def test_plagiarism_detector():
    detector = PlagiarismDetector()
    result = detector.analyse(SAMPLE_PAPER_CONTENT)
    assert "overall_risk_level" in result
    assert "originality_indicator" in result
    assert result["originality_indicator"] > 70.0


def test_figure_table_validator():
    validator = FigureTableValidator()
    result = validator.validate(file_path=None, extracted_content=SAMPLE_PAPER_CONTENT)
    assert "validation_score" in result
    assert result["summary"]["detected_figures_count"] >= 1


def test_patentability_evaluator():
    evaluator = PatentabilityEvaluator()
    result = evaluator.evaluate(SAMPLE_PAPER_CONTENT)
    assert "overall_patentability_score" in result
    assert "readiness_tier" in result
    assert "criteria_breakdown" in result


def test_readiness_scorer():
    scorer = ReadinessScorer()
    mock_analyses = {
        "technical_review": {"overall_score": 88.0, "strengths": ["Clear methodology"]},
        "novelty": {"overall_novelty_score": 75.0},
        "citations": {"citation_score": 90.0, "total_references": 15},
        "grammar": {"grammar_score": 85.0, "total_suggestions": 2},
        "figures_tables": {"validation_score": 95.0, "summary": {"figure_issues_count": 0}},
        "plagiarism": {"originality_indicator": 92.0},
    }
    result = scorer.calculate_readiness(mock_analyses)
    assert result["overall_score"] >= 80.0
    assert result["readiness_category"] == "Ready for Submission"
    assert len(result["category_scores"]) == 6
