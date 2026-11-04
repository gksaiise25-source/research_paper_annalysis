"""
Publication Readiness Scorer Module - Aggregates outputs from all 9 analytical modules.
Calculates a transparent, weighted score dynamically adjusting for available modules.
"""
from typing import Dict, List, Optional
from loguru import logger


class ReadinessScorer:
    """Calculates overall publication readiness based on rigorous multi-attribute evaluation."""

    # Default weights for each core dimension
    MODULE_WEIGHTS = {
        "technical_review": 0.25,      # Methodology & structural completeness
        "novelty": 0.20,               # Research novelty & uniqueness
        "citation_analysis": 0.15,     # Bibliographic integrity & cross-referencing
        "grammar_analysis": 0.15,      # Writing quality, clarity, readability
        "figure_validation": 0.10,     # Visual presentation, captions, resolution
        "plagiarism_detection": 0.15,  # Originality vs similarity risk
    }

    def calculate_readiness(self, all_analyses: Dict[str, Dict]) -> Dict:
        """
        Aggregate all completed analysis results and compute publication readiness.
        all_analyses: dict mapping analysis_type -> analysis_result_dict
        """
        category_scores = {}
        weighted_sum = 0.0
        total_weight_used = 0.0

        # 1. Technical Review (Methodology & Sections)
        tech = all_analyses.get("technical_review", {})
        if tech and "overall_score" in tech:
            score = float(tech["overall_score"])
            category_scores["methodology_and_structure"] = {
                "score": score,
                "weight": self.MODULE_WEIGHTS["technical_review"],
                "status": "Evaluated",
                "label": "Methodology & Section Completeness",
            }
            weighted_sum += score * self.MODULE_WEIGHTS["technical_review"]
            total_weight_used += self.MODULE_WEIGHTS["technical_review"]
        else:
            category_scores["methodology_and_structure"] = {"status": "Unavailable", "score": None}

        # 2. Novelty
        nov = all_analyses.get("novelty", {})
        if nov and "overall_novelty_score" in nov and nov["overall_novelty_score"] is not None:
            score = float(nov["overall_novelty_score"])
            category_scores["novelty"] = {
                "score": score,
                "weight": self.MODULE_WEIGHTS["novelty"],
                "status": "Evaluated",
                "label": "Research Novelty & Uniqueness",
            }
            weighted_sum += score * self.MODULE_WEIGHTS["novelty"]
            total_weight_used += self.MODULE_WEIGHTS["novelty"]
        else:
            category_scores["novelty"] = {"status": "Unavailable", "score": None}

        # 3. Citation Analysis
        cit = all_analyses.get("citations", {})
        if cit and "citation_score" in cit and cit["citation_score"] is not None:
            score = float(cit["citation_score"])
            category_scores["citations"] = {
                "score": score,
                "weight": self.MODULE_WEIGHTS["citation_analysis"],
                "status": "Evaluated",
                "label": "Citation & Bibliographic Rigor",
            }
            weighted_sum += score * self.MODULE_WEIGHTS["citation_analysis"]
            total_weight_used += self.MODULE_WEIGHTS["citation_analysis"]
        else:
            category_scores["citations"] = {"status": "Unavailable", "score": None}

        # 4. Grammar & Writing Quality
        gram = all_analyses.get("grammar", {})
        if gram and "grammar_score" in gram and gram["grammar_score"] is not None:
            score = float(gram["grammar_score"])
            category_scores["writing_quality"] = {
                "score": score,
                "weight": self.MODULE_WEIGHTS["grammar_analysis"],
                "status": "Evaluated",
                "label": "Academic Writing Quality & Tone",
            }
            weighted_sum += score * self.MODULE_WEIGHTS["grammar_analysis"]
            total_weight_used += self.MODULE_WEIGHTS["grammar_analysis"]
        else:
            category_scores["writing_quality"] = {"status": "Unavailable", "score": None}

        # 5. Figure and Table Validation
        fig = all_analyses.get("figures_tables", {})
        if fig and "validation_score" in fig and fig["validation_score"] is not None:
            score = float(fig["validation_score"])
            category_scores["figures_and_tables"] = {
                "score": score,
                "weight": self.MODULE_WEIGHTS["figure_validation"],
                "status": "Evaluated",
                "label": "Figures, Tables & Presentation",
            }
            weighted_sum += score * self.MODULE_WEIGHTS["figure_validation"]
            total_weight_used += self.MODULE_WEIGHTS["figure_validation"]
        else:
            category_scores["figures_and_tables"] = {"status": "Unavailable", "score": None}

        # 6. Plagiarism & Originality
        plag = all_analyses.get("plagiarism", {})
        if plag and "originality_indicator" in plag and plag["originality_indicator"] is not None:
            score = float(plag["originality_indicator"])
            category_scores["originality"] = {
                "score": score,
                "weight": self.MODULE_WEIGHTS["plagiarism_detection"],
                "status": "Evaluated",
                "label": "Originality & Low Similarity Risk",
            }
            weighted_sum += score * self.MODULE_WEIGHTS["plagiarism_detection"]
            total_weight_used += self.MODULE_WEIGHTS["plagiarism_detection"]
        else:
            category_scores["originality"] = {"status": "Unavailable", "score": None}

        # Dynamically normalize based on available weights
        if total_weight_used > 0:
            overall_score = round(weighted_sum / total_weight_used, 1)
        else:
            overall_score = 50.0

        # Categorize readiness recommendation
        if overall_score >= 85.0:
            category = "Ready for Submission"
            summary_text = "The paper meets high academic standards across structure, citations, language, and originality."
        elif overall_score >= 70.0:
            category = "Minor Revision"
            summary_text = "The paper is in solid condition but will benefit from addressing minor issues in citations, figures, or wording."
        elif overall_score >= 50.0:
            category = "Major Revision"
            summary_text = "Substantial improvements required in experimental validation, section completeness, or language before journal submission."
        else:
            category = "Not Ready for Submission"
            summary_text = "Core sections or empirical data appear incomplete or significant formatting/originality revisions are necessary."

        # Aggregate strengths and weaknesses
        strengths, weaknesses, improvements = self._synthesize_insights(all_analyses)

        return {
            "overall_score": overall_score,
            "readiness_category": category,
            "summary_assessment": summary_text,
            "weights_normalization_factor": round(total_weight_used, 2),
            "category_scores": category_scores,
            "strengths": strengths,
            "weaknesses": weaknesses,
            "priority_improvements": improvements[:6],
            "disclaimer": (
                "The Publication Readiness Score is an algorithmic heuristic tool designed to assist authors prior to submission. "
                "It is NOT a guarantee of peer review outcome, journal acceptance, or conference selection."
            ),
        }

    def _synthesize_insights(self, analyses: Dict[str, Dict]):
        strengths = []
        weaknesses = []
        improvements = []

        # From Technical Review
        tech = analyses.get("technical_review", {})
        for s in tech.get("strengths", [])[:2]:
            strengths.append(s)
        for w in tech.get("weaknesses", [])[:2]:
            weaknesses.append(w)
            improvements.append(f"Technical: {w}")

        # From Citations
        cit = analyses.get("citations", {})
        if cit.get("citation_score", 0) > 80:
            strengths.append(f"Clean bibliographic formatting ({cit.get('total_references', 0)} references parsed).")
        elif cit.get("total_issue_count", 0) > 0:
            weaknesses.append(f"Citation analysis detected {cit.get('total_issue_count')} reference inconsistencies.")
            improvements.append("Citations: Harmonize in-text citation keys with bibliography items.")

        # From Grammar
        gram = analyses.get("grammar", {})
        if gram.get("grammar_score", 0) > 80:
            strengths.append("High academic writing tone and readability.")
        elif gram.get("total_suggestions", 0) > 5:
            weaknesses.append(f"Identified {gram.get('total_suggestions')} language and sentence structure suggestions.")
            improvements.append("Language: Eliminate wordy phrases and reduce passive voice overuse.")

        # From Figures
        fig = analyses.get("figures_tables", {})
        if fig.get("summary", {}).get("figure_issues_count", 0) > 0:
            weaknesses.append(f"Figure/Table validation found {fig['summary']['figure_issues_count']} numbering or resolution alerts.")
            improvements.append("Visuals: Check sequential figure numbering and replace low-resolution diagrams.")

        # Defaults if empty
        if not strengths:
            strengths.append("Manuscript uploaded and extracted with intact structural headings.")
        if not weaknesses:
            weaknesses.append("No critical blocking flaws discovered in primary automated checks.")
        if not improvements:
            improvements.append("Perform a final author proofread prior to journal submission.")

        return strengths, weaknesses, improvements
