"""
Plagiarism Risk Detection Module - Uses semantic similarity to detect potential plagiarism risk.
IMPORTANT: This is a similarity risk assessment, NOT a confirmed plagiarism check.
"""
import re
from typing import Dict, List, Optional
from loguru import logger


class PlagiarismDetector:

    SIMILARITY_THRESHOLDS = {
        "high_risk": 70,
        "moderate_risk": 45,
        "low_risk": 20,
    }

    def analyse(self, extracted_content: Dict, comparison_texts: Optional[List[Dict]] = None) -> Dict:
        """
        Analyse plagiarism risk.
        comparison_texts: list of dicts with 'text', 'source', 'title' keys.
        """
        full_text = extracted_content.get("full_text", "")
        abstract = extracted_content.get("abstract", "")

        if not full_text:
            return {"error": "No text available for plagiarism analysis."}

        # Internal analysis: detect self-similar paragraphs
        internal_results = self._check_internal_repetition(full_text)

        # N-gram fingerprint analysis
        ngram_results = self._ngram_analysis(full_text)

        # If comparison texts provided, compute similarities
        external_results = []
        if comparison_texts:
            external_results = self._compare_with_sources(full_text, comparison_texts)

        # Overall risk
        max_external_sim = max(
            (r["similarity_percentage"] for r in external_results), default=0
        )
        internal_dup_rate = internal_results.get("duplication_rate", 0)

        overall_risk = self._assess_overall_risk(max_external_sim, internal_dup_rate)

        score = max(0, 100 - max_external_sim - (internal_dup_rate * 50))

        return {
            "overall_risk_level": overall_risk,
            "similarity_score": round(100 - score, 1),
            "originality_indicator": round(score, 1),
            "internal_repetition": internal_results,
            "external_comparisons": external_results[:10],
            "ngram_analysis": ngram_results,
            "disclaimer": (
                "This is an AI-based similarity risk assessment using available scholarly sources. "
                "It does NOT constitute a comprehensive internet-wide plagiarism check. "
                "High similarity scores indicate thematic or content overlap, not confirmed plagiarism."
            ),
            "recommendations": self._generate_recommendations(overall_risk, internal_results),
        }

    def _check_internal_repetition(self, text: str) -> Dict:
        """Detect repeated paragraphs within the same document (self-plagiarism risk)."""
        paragraphs = [p.strip() for p in text.split("\n\n") if len(p.strip()) > 100]
        duplicates = []

        seen = {}
        for i, para in enumerate(paragraphs):
            key = para[:80].lower()
            if key in seen:
                duplicates.append({
                    "paragraph_index": i + 1,
                    "duplicate_of": seen[key] + 1,
                    "snippet": para[:150] + "...",
                })
            else:
                seen[key] = i

        duplication_rate = len(duplicates) / max(len(paragraphs), 1)

        return {
            "total_paragraphs": len(paragraphs),
            "duplicate_paragraphs": len(duplicates),
            "duplication_rate": round(duplication_rate, 3),
            "duplicates": duplicates[:5],
        }

    def _ngram_analysis(self, text: str) -> Dict:
        """Analyse text using n-gram fingerprinting."""
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())

        if len(words) < 10:
            return {"fingerprints_generated": 0}

        # Generate 5-grams
        ngrams = [" ".join(words[i:i+5]) for i in range(len(words)-4)]
        unique_ngrams = len(set(ngrams))
        total_ngrams = len(ngrams)

        uniqueness_ratio = unique_ngrams / max(total_ngrams, 1)

        return {
            "total_5grams": total_ngrams,
            "unique_5grams": unique_ngrams,
            "uniqueness_ratio": round(uniqueness_ratio, 3),
            "interpretation": (
                "High uniqueness ratio suggests original content. "
                f"Ratio: {uniqueness_ratio:.1%}"
            ),
        }

    def _compare_with_sources(self, text: str, sources: List[Dict]) -> List[Dict]:
        """Compare paper against provided source texts."""
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.metrics.pairwise import cosine_similarity

            source_texts = [s.get("text", "") for s in sources if s.get("text")]
            if not source_texts:
                return []

            vectorizer = TfidfVectorizer(max_features=2000, stop_words="english", ngram_range=(1, 2))
            all_texts = [text[:5000]] + [t[:5000] for t in source_texts]
            tfidf_matrix = vectorizer.fit_transform(all_texts)
            sims = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:])[0]

            results = []
            for i, source in enumerate(sources[:len(source_texts)]):
                sim_pct = round(float(sims[i]) * 100, 1)
                results.append({
                    "source_title": source.get("title", f"Source {i+1}"),
                    "source": source.get("source", "Unknown"),
                    "similarity_percentage": sim_pct,
                    "risk_level": self._get_risk_level(sim_pct),
                })

            results.sort(key=lambda x: x["similarity_percentage"], reverse=True)
            return results

        except Exception as e:
            logger.warning(f"Source comparison error: {e}")
            return []

    def _get_risk_level(self, sim_pct: float) -> str:
        if sim_pct >= self.SIMILARITY_THRESHOLDS["high_risk"]:
            return "High Risk"
        elif sim_pct >= self.SIMILARITY_THRESHOLDS["moderate_risk"]:
            return "Moderate Risk"
        elif sim_pct >= self.SIMILARITY_THRESHOLDS["low_risk"]:
            return "Low Risk"
        return "Minimal Risk"

    def _assess_overall_risk(self, max_external_sim: float, internal_dup_rate: float) -> str:
        if max_external_sim >= 70 or internal_dup_rate > 0.3:
            return "High Risk"
        elif max_external_sim >= 45 or internal_dup_rate > 0.15:
            return "Moderate Risk"
        elif max_external_sim >= 20 or internal_dup_rate > 0.05:
            return "Low Risk"
        return "Minimal Risk"

    def _generate_recommendations(self, risk_level: str, internal_results: Dict) -> List[str]:
        recs = [
            "Run your paper through an institutional plagiarism checker (e.g., Turnitin, iThenticate) before submission.",
        ]
        if risk_level in ["High Risk", "Moderate Risk"]:
            recs.append("Review highlighted sections and ensure all borrowed content is properly cited.")
            recs.append("Paraphrase and properly attribute any content adapted from other sources.")
        if internal_results.get("duplicate_paragraphs", 0) > 0:
            recs.append(f"Found {internal_results['duplicate_paragraphs']} internally repeated paragraph(s). Remove redundancy.")
        recs.append("Ensure all direct quotations use quotation marks and proper citation.")
        return recs
