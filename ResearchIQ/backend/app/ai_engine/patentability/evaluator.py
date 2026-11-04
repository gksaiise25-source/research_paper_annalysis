"""
Patentability Indicator Module - Assesses patent readiness criteria (Novelty, Non-obviousness, Industrial Applicability).
IMPORTANT: This provides an automated preliminary screening, NOT certified legal advice or a patent guarantee.
"""
import re
from typing import Dict, List, Optional
from loguru import logger
import httpx


class PatentabilityEvaluator:
    """Evaluates manuscript text for standard patentability criteria and industrial utility indicators."""

    # Keywords indicating patentable technical embodiment vs pure abstract theory
    APPLICABILITY_KEYWORDS = [
        "system", "apparatus", "device", "hardware", "circuit", "sensor",
        "processor", "method of manufacturing", "fabrication", "composition",
        "formulation", "industrial", "protocol", "architecture", "deployment",
        "throughput", "latency", "efficiency", "energy consumption", "optimization"
    ]

    ABSTRACT_THEORY_KEYWORDS = [
        "theoretical framework", "purely mathematical", "philosophy",
        "speculative hypothesis", "literature survey", "bibliometric",
        "pedagogical", "review of previous literature"
    ]

    NOVELTY_CLAIM_PATTERNS = [
        r'(?:we propose|we invent|we design|herein disclosed|novel technique|first to demonstrate)',
        r'(?:outperforms existing|significantly improves|reduces computation by \d+%)',
        r'(?:a new architecture|an improved mechanism|a bespoke apparatus)'
    ]

    def evaluate(self, extracted_content: Dict) -> Dict:
        """Run patentability screening on paper content."""
        title = extracted_content.get("title", "")
        abstract = extracted_content.get("abstract", "")
        methodology = extracted_content.get("methodology", "")
        results = extracted_content.get("results", "")

        corpus = f"{title}\n{abstract}\n{methodology}".lower()

        # 1. Industrial Applicability & Technical Embodiment
        app_hits = [kw for kw in self.APPLICABILITY_KEYWORDS if kw in corpus]
        theory_hits = [kw for kw in self.ABSTRACT_THEORY_KEYWORDS if kw in corpus]

        industrial_score = min(95.0, max(20.0, 30.0 + (len(app_hits) * 6.0) - (len(theory_hits) * 10.0)))

        # 2. Novelty & Inventive Step (Non-Obviousness) Signals
        inventive_claims = []
        for pattern in self.NOVELTY_CLAIM_PATTERNS:
            matches = re.findall(pattern, corpus, re.IGNORECASE)
            inventive_claims.extend(matches)

        inventive_step_score = min(92.0, max(25.0, 40.0 + (len(inventive_claims) * 8.0)))

        # 3. Patent Subject Matter Eligibility Check (35 U.S.C. 101 / EPC Art 52)
        eligibility_concerns = []
        if len(app_hits) < 2:
            eligibility_concerns.append(
                "Abstract idea / Pure software algorithm concern: Patent offices require a practical technical application or physical transformation, not merely abstract math."
            )
        if "natural law" in corpus or "biological process" in corpus and len(app_hits) < 3:
            eligibility_concerns.append(
                "Potential natural phenomenon objection: Verify whether the claimed mechanism contains an inventive application beyond observing natural phenomena."
            )
        if not methodology or len(methodology.split()) < 150:
            eligibility_concerns.append(
                "Insufficient enablement: The disclosure may lack sufficient technical specifics for a Person Having Ordinary Skill In The Art (PHOSITA) to replicate the invention."
            )

        # 4. Overall Patentability Score Calculation
        overall_score = round((industrial_score * 0.5) + (inventive_step_score * 0.5) - (len(eligibility_concerns) * 10.0), 1)
        overall_score = max(15.0, min(92.0, overall_score))

        # Categorize
        if overall_score >= 70:
            tier = "High Potential for Patent Protection"
            readiness_summary = "The paper describes concrete technical systems, industrial applicability, and measurable performance advantages."
        elif overall_score >= 50:
            tier = "Moderate Potential (Needs Method/Claim Refinement)"
            readiness_summary = "Technical contributions are present, but legal enablement and concrete hardware/industrial embodiment should be detailed."
        else:
            tier = "Low Patentability Likelihood (Primarily Academic/Theoretical)"
            readiness_summary = "The work appears heavily theoretical, survey-based, or abstract, which commonly faces 35 U.S.C. § 101 or equivalent eligibility rejections."

        return {
            "overall_patentability_score": overall_score,
            "readiness_tier": tier,
            "criteria_breakdown": {
                "industrial_applicability": {
                    "score": round(industrial_score, 1),
                    "detected_elements": app_hits[:8],
                    "status": "Satisfied" if industrial_score > 60 else "Borderline",
                },
                "inventive_step_novelty": {
                    "score": round(inventive_step_score, 1),
                    "claims_found": len(inventive_claims),
                    "status": "Present" if inventive_step_score > 60 else "Unclear",
                },
                "technical_enablement": {
                    "score": 80.0 if len(methodology.split()) > 200 else 40.0,
                    "status": "Sufficient" if len(methodology.split()) > 200 else "Needs More Detail",
                }
            },
            "eligibility_concerns": eligibility_concerns if eligibility_concerns else ["No major statutory disqualifications detected in preliminary analysis."],
            "potential_patent_claims": self._suggest_draft_claims(title, app_hits),
            "disclaimer": (
                "LEGAL DISCLAIMER: ResearchIQ's Patentability Indicator is an automated preliminary screening tool "
                "intended solely for research awareness. It does NOT constitute formal legal advice, a certified patentability "
                "search, or a guarantee of USPTO, EPO, or WIPO approval. Consult a registered Patent Attorney or Patent Agent."
            ),
            "recommended_next_steps": [
                "Maintain strict confidentiality prior to filing; publishing this paper publicly before filing a provisional patent establishes prior art against your own invention.",
                "Conduct a formal prior art search on Google Patents, Espacenet, and USPTO databases.",
                "Consult your university or institution's Technology Transfer Office (TTO) to discuss patent assignment and provisional filings.",
            ],
        }

    def _suggest_draft_claims(self, title: str, app_hits: List[str]) -> List[str]:
        """Generate high-level draft claim archetypes."""
        tech_terms = ", ".join(app_hits[:3]) if app_hits else "processing unit"
        return [
            f"1. A computer-implemented system configured to perform {title.lower() if title else 'technical processing'}, comprising: memory and one or more processors configured to execute instructions.",
            f"2. A method for optimizing operations utilizing {tech_terms}, comprising: receiving input datasets, executing algorithmic transformations, and generating output telemetry.",
        ]
