"""
Technical Review Module - Analyses research paper sections for quality and completeness.
"""
from typing import Dict, List, Optional
from loguru import logger


SECTION_CRITERIA = {
    "abstract": {
        "min_words": 100,
        "max_words": 350,
        "required_elements": ["objective", "method", "result", "conclusion"],
        "weight": 15,
    },
    "introduction": {
        "min_words": 200,
        "required_elements": ["background", "problem", "objective", "contribution"],
        "weight": 15,
    },
    "literature_review": {
        "min_words": 300,
        "required_elements": ["review", "comparison", "gap"],
        "weight": 15,
    },
    "methodology": {
        "min_words": 200,
        "required_elements": ["data", "method", "approach", "technique"],
        "weight": 25,
    },
    "results": {
        "min_words": 150,
        "required_elements": ["result", "finding", "performance", "accuracy"],
        "weight": 20,
    },
    "conclusion": {
        "min_words": 100,
        "required_elements": ["conclude", "future", "contribution", "summary"],
        "weight": 10,
    },
}

ELEMENT_KEYWORDS = {
    "objective": ["objective", "aim", "goal", "purpose", "intend"],
    "method": ["method", "approach", "technique", "algorithm", "model", "framework"],
    "result": ["result", "finding", "achieve", "performance", "accuracy", "show"],
    "conclusion": ["conclude", "conclusion", "summary", "finding"],
    "background": ["background", "context", "motivat", "problem", "challeng"],
    "problem": ["problem", "challenge", "issue", "limitation", "gap"],
    "contribution": ["contribut", "novelty", "novel", "propose", "present"],
    "review": ["review", "survey", "study", "work", "literature", "existing"],
    "comparison": ["compar", "contrast", "differ", "similar", "versus", "vs"],
    "gap": ["gap", "limitation", "miss", "lack", "unexplored", "insufficient"],
    "data": ["dataset", "data", "corpus", "sample", "experiment", "benchmark"],
    "approach": ["approach", "framework", "architecture", "design"],
    "technique": ["technique", "algorithm", "neural", "model", "classif", "detect"],
    "finding": ["finding", "result", "outcome", "show", "demonstrate", "reveal"],
    "performance": ["performance", "accuracy", "precision", "recall", "F1", "score"],
    "future": ["future", "further", "extend", "improve", "subsequent"],
    "summary": ["summary", "summarize", "overall", "this paper", "this work"],
}


class TechnicalReviewer:

    def analyse(self, extracted_content: Dict) -> Dict:
        """Run technical review on extracted paper content."""
        try:
            section_analyses = {}
            total_score = 0.0
            total_weight = 0.0
            missing_sections = []
            present_sections = []

            for section_name, criteria in SECTION_CRITERIA.items():
                section_text = extracted_content.get(section_name, "") or ""
                analysis = self._analyse_section(section_name, section_text, criteria)
                section_analyses[section_name] = analysis

                if section_text.strip():
                    present_sections.append(section_name)
                    score = analysis["score"]
                    weight = criteria["weight"]
                    total_score += score * weight
                    total_weight += weight
                else:
                    missing_sections.append(section_name)
                    # Penalise for missing section - use half the weight as penalty
                    total_weight += criteria["weight"]

            overall_score = (total_score / total_weight * 100) if total_weight > 0 else 0

            # Check for results+discussion as combined
            results = extracted_content.get("results", "") or ""
            discussion = extracted_content.get("discussion", "") or ""

            strengths = self._identify_strengths(section_analyses, present_sections)
            weaknesses = self._identify_weaknesses(section_analyses, missing_sections)

            return {
                "overall_score": round(overall_score, 1),
                "sections_present": present_sections,
                "sections_missing": missing_sections,
                "section_analyses": section_analyses,
                "strengths": strengths,
                "weaknesses": weaknesses,
                "word_count": extracted_content.get("word_count", 0),
                "recommendations": self._generate_recommendations(section_analyses, missing_sections),
            }

        except Exception as e:
            logger.error(f"Technical review error: {e}")
            raise

    def _analyse_section(self, section_name: str, text: str, criteria: Dict) -> Dict:
        """Analyse a single section."""
        if not text.strip():
            return {
                "present": False,
                "score": 0.0,
                "word_count": 0,
                "feedback": [f"Section '{section_name}' is missing from the paper."],
                "issues": ["Section not found"],
                "strengths": [],
            }

        words = text.split()
        word_count = len(words)
        issues = []
        section_strengths = []
        score_components = []

        # Word count check
        min_words = criteria.get("min_words", 100)
        max_words = criteria.get("max_words", 99999)

        if word_count < min_words:
            issues.append(f"Section is too brief ({word_count} words; recommended minimum: {min_words} words).")
            score_components.append(word_count / min_words * 40)
        elif word_count > max_words:
            issues.append(f"Abstract is too long ({word_count} words; recommended maximum: {max_words} words).")
            score_components.append(80.0)
        else:
            section_strengths.append(f"Section has adequate length ({word_count} words).")
            score_components.append(40.0)

        # Required element check
        text_lower = text.lower()
        found_elements = []
        missing_elements = []

        for element in criteria.get("required_elements", []):
            keywords = ELEMENT_KEYWORDS.get(element, [element])
            if any(kw in text_lower for kw in keywords):
                found_elements.append(element)
            else:
                missing_elements.append(element)

        element_score = (len(found_elements) / max(len(criteria.get("required_elements", [1])), 1)) * 60
        score_components.append(element_score)

        if missing_elements:
            issues.append(f"Missing expected content: {', '.join(missing_elements)}.")
        if found_elements:
            section_strengths.append(f"Contains: {', '.join(found_elements)}.")

        # Compute normalized score (0.0 to 1.0)
        final_score = (sum(score_components) / 100.0) if score_components else 0.0

        feedback = []
        for issue in issues:
            feedback.append(f"⚠️ {issue}")
        for strength in section_strengths:
            feedback.append(f"✓ {strength}")

        return {
            "present": True,
            "score": round(final_score, 3),
            "word_count": word_count,
            "found_elements": found_elements,
            "missing_elements": missing_elements,
            "feedback": feedback,
            "issues": issues,
            "strengths": section_strengths,
        }

    def _identify_strengths(self, section_analyses: Dict, present_sections: List[str]) -> List[str]:
        strengths = []
        if len(present_sections) >= 5:
            strengths.append("Paper has a comprehensive section structure.")
        for section, analysis in section_analyses.items():
            if analysis.get("present") and analysis.get("score", 0) > 0.7:
                strengths.append(f"The {section} section is well-written and complete.")
        return strengths

    def _identify_weaknesses(self, section_analyses: Dict, missing_sections: List[str]) -> List[str]:
        weaknesses = []
        for s in missing_sections:
            weaknesses.append(f"The '{s}' section is absent from the paper.")
        for section, analysis in section_analyses.items():
            if analysis.get("present") and analysis.get("score", 1) < 0.4:
                weaknesses.append(f"The {section} section needs significant improvement.")
        return weaknesses

    def _generate_recommendations(self, section_analyses: Dict, missing_sections: List[str]) -> List[str]:
        recs = []
        for s in missing_sections:
            recs.append(f"Add a dedicated '{s}' section.")
        for section, analysis in section_analyses.items():
            for issue in analysis.get("issues", []):
                recs.append(f"[{section.title()}] {issue}")
        return recs[:15]
