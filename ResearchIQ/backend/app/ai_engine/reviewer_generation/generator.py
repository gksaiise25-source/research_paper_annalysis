"""
AI Reviewer Comments Module - Generates realistic peer-reviewer feedback grounded in the uploaded paper.
Integrates with Google Gemini API when configured, with a structured academic rubric fallback.
"""
import os
import json
from typing import Dict, List, Optional
from loguru import logger
from app.core.config import settings


class ReviewerGenerator:
    """Generates rigorous academic peer review comments grounded in the paper's actual text."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.GEMINI_API_KEY

    async def generate_review(self, extracted_content: Dict) -> Dict:
        """Generate comprehensive peer reviewer feedback."""
        title = extracted_content.get("title", "Untitled Manuscript")
        abstract = extracted_content.get("abstract", "")
        introduction = extracted_content.get("introduction", "")
        methodology = extracted_content.get("methodology", "")
        results = extracted_content.get("results", "")
        conclusion = extracted_content.get("conclusion", "")
        word_count = extracted_content.get("word_count", 0)

        # Try Gemini API if key is available
        if self.api_key and self.api_key.strip():
            try:
                gemini_review = await self._generate_with_gemini(
                    title=title,
                    abstract=abstract,
                    introduction=introduction,
                    methodology=methodology,
                    results=results,
                    conclusion=conclusion,
                )
                if gemini_review:
                    gemini_review["generator_mode"] = "Google Gemini API"
                    return gemini_review
            except Exception as e:
                logger.warning(f"Gemini API review generation failed, using rule-based generator: {e}")

        # Fallback to deterministic NLP / manuscript-grounded review generator
        return self._generate_rule_based_review(extracted_content)

    async def _generate_with_gemini(
        self, title: str, abstract: str, introduction: str, methodology: str, results: str, conclusion: str
    ) -> Optional[Dict]:
        """Call Google Gemini model to perform grounded peer review."""
        try:
            import google.generativeai as genai

            genai.configure(api_key=self.api_key)
            model = genai.GenerativeModel("gemini-1.5-flash")

            prompt = f"""
You are an expert peer reviewer for top-tier academic journals (e.g., IEEE, Nature, ACM).
Critique the following research manuscript objectively based ONLY on the provided text.
Do not hallucinate facts. If certain sections or validation details are missing from the text, state that explicitly.

TITLE: {title}
ABSTRACT: {abstract[:1500]}
INTRODUCTION: {introduction[:1500]}
METHODOLOGY: {methodology[:2000]}
RESULTS & DISCUSSION: {results[:2000]}
CONCLUSION: {conclusion[:1000]}

Respond ONLY with a valid JSON object matching this exact schema:
{{
  "overall_assessment": "Summary of the paper's premise, contributions, and readiness level",
  "recommendation": "Accept" | "Minor Revision" | "Major Revision" | "Reject",
  "paper_strengths": ["Strength 1 with reference to text", "Strength 2..."],
  "paper_weaknesses": ["Weakness 1 with reference to text", "Weakness 2..."],
  "major_revisions": ["Major revision item 1...", "Major revision item 2..."],
  "minor_revisions": ["Minor revision item 1...", "Minor revision item 2..."],
  "methodology_critique": "Specific feedback on experimental design, dataset, and baseline comparisons",
  "experimental_suggestions": "Concrete steps to validate or reproduce findings",
  "conclusion_improvements": "Critique on whether claims are supported by experimental data"
}}
"""
            response = await model.generate_content_async(prompt)
            raw_text = response.text.strip()

            # Clean JSON if wrapped in markdown blocks
            if raw_text.startswith("```json"):
                raw_text = raw_text[7:]
            if raw_text.startswith("```"):
                raw_text = raw_text[3:]
            if raw_text.endswith("```"):
                raw_text = raw_text[:-3]

            data = json.loads(raw_text.strip())
            return data
        except Exception as e:
            logger.error(f"Error querying Gemini for peer review: {e}")
            return None

    def _generate_rule_based_review(self, content: Dict) -> Dict:
        """Generate structured peer review grounded strictly on verified extracted sections."""
        title = content.get("title", "The manuscript")
        abstract = content.get("abstract", "")
        intro = content.get("introduction", "")
        method = content.get("methodology", "")
        results = content.get("results", "")
        conclusion = content.get("conclusion", "")
        word_count = content.get("word_count", 0)

        strengths = []
        weaknesses = []
        major_revisions = []
        minor_revisions = []

        # Grounded checks: Abstract
        if abstract:
            if len(abstract.split()) > 80:
                strengths.append(f"The abstract provides an overview of the scope and core themes ({len(abstract.split())} words).")
            else:
                weaknesses.append("The abstract is relatively terse and omits specific numerical outcome metrics.")
                minor_revisions.append("Expand the abstract to clearly present problem statement, quantitative findings, and broader impact.")
        else:
            weaknesses.append("Abstract is not explicitly identified or formatted according to standard guidelines.")
            major_revisions.append("Provide a well-structured abstract (150-250 words) highlighting objectives, methodology, and empirical findings.")

        # Grounded checks: Methodology
        if method:
            method_words = len(method.split())
            if method_words > 250:
                strengths.append(f"Methodology section outlines procedural steps and technical design ({method_words} words).")
            else:
                weaknesses.append("The methodology is concise; reproducibility parameters, hardware specs, or hyperparameter setups appear incomplete.")
                major_revisions.append("Include full mathematical definitions, dataset curation details, and explicit baseline comparisons in the methodology.")
        else:
            weaknesses.append("No dedicated methodology section was detected in the manuscript.")
            major_revisions.append("Add a formal Methodology/Approach section detailing experimental setups, algorithms, or theoretical derivations.")

        # Grounded checks: Results & Validation
        if results:
            res_lower = results.lower()
            if any(term in res_lower for term in ["baseline", "accuracy", "f1", "comparison", "benchmark", "p-value"]):
                strengths.append("Results section includes comparative performance metrics or benchmarking terminology.")
            else:
                weaknesses.append("Results lack explicit statistical validation (e.g. standard deviation, confidence intervals, ablation studies).")
                major_revisions.append("Strengthen empirical evaluation with rigorous statistical tests, error analyses, and ablation experiments.")
        else:
            weaknesses.append("Dedicated empirical results or evaluation metrics could not be verified in the extracted sections.")
            major_revisions.append("Include thorough empirical results comparing the proposed approach against established state-of-the-art baselines.")

        # Grounded checks: Conclusion
        if conclusion:
            strengths.append("Conclusion summarizes key findings and addresses current research scope.")
            if "future work" not in conclusion.lower():
                minor_revisions.append("Articulate future work directions and open research avenues in the conclusion.")
        else:
            minor_revisions.append("Formalize a concluding section detailing summary of contributions, technical limitations, and future outlook.")

        # Overall Recommendation calculation
        if len(major_revisions) >= 3:
            rec = "Major Revision"
            overall = (
                f"The manuscript '{title}' addresses an interesting topic, but requires substantial enhancements in technical validation, "
                "methodological rigor, and section completeness before it reaches standard publication threshold."
            )
        elif len(major_revisions) >= 1:
            rec = "Minor Revision"
            overall = (
                f"The manuscript '{title}' presents coherent research with promising ideas. "
                "The core contributions are visible, but several revisions to baselines, framing, and empirical support are necessary."
            )
        else:
            rec = "Accept with Minor Changes"
            overall = (
                f"The manuscript '{title}' is well-organized with adequate structural integrity. "
                "Minor formatting and polishing will prepare this paper for submission."
            )

        return {
            "overall_assessment": overall,
            "recommendation": rec,
            "paper_strengths": strengths if strengths else ["Document demonstrates engagement with current academic literature."],
            "paper_weaknesses": weaknesses,
            "major_revisions": major_revisions,
            "minor_revisions": minor_revisions,
            "methodology_critique": (
                "Ensure all experimental parameters, dataset partitions, and algorithmic pseudocode are fully specified for independent reproducibility."
                if method else "Methodology details could not be verified from the document text."
            ),
            "experimental_suggestions": (
                "Perform statistical significance testing (e.g. t-tests or ANOVA) and include sensitivity analysis on critical hyperparameters."
            ),
            "conclusion_improvements": (
                "Ensure every claim made in the conclusion is strictly substantiated by the data presented in the results section."
            ),
            "generator_mode": "Rule-based Academic Evaluation (Gemini API key not configured)",
        }
