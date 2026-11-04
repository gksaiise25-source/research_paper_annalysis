"""
Novelty Analysis Module - Compares paper with published research via OpenAlex/Crossref.
"""
import asyncio
import re
from typing import Dict, List, Optional
from loguru import logger
import httpx


class NoveltyAnalyser:

    OPENALEX_BASE = "https://api.openalex.org"
    CROSSREF_BASE = "https://api.crossref.org"

    def __init__(self, email: Optional[str] = None):
        self.email = email
        self._embedder = None

    def _get_embedder(self):
        """Lazy-load sentence transformer."""
        if self._embedder is None:
            try:
                from sentence_transformers import SentenceTransformer
                self._embedder = SentenceTransformer("all-MiniLM-L6-v2")
                logger.info("Sentence transformer loaded.")
            except Exception as e:
                logger.warning(f"Could not load sentence transformer: {e}")
        return self._embedder

    async def analyse(self, extracted_content: Dict) -> Dict:
        """Run novelty analysis."""
        title = extracted_content.get("title", "")
        abstract = extracted_content.get("abstract", "")
        keywords = extracted_content.get("keywords", [])
        methodology = extracted_content.get("methodology", "")

        if not abstract and not title:
            return {"error": "Insufficient content for novelty analysis.", "score": None}

        query_text = f"{title} {abstract}"[:500]

        # Fetch related papers from OpenAlex
        related_papers = await self._fetch_related_papers(query_text, keywords)

        if not related_papers:
            return {
                "overall_novelty_score": 65.0,
                "assessment": "Could not retrieve comparison papers from OpenAlex. Novelty cannot be quantitatively assessed.",
                "similar_papers": [],
                "research_gaps": self._identify_research_gaps(abstract, []),
                "novelty_indicators": self._extract_novelty_indicators(abstract, methodology),
                "data_source": "OpenAlex API unavailable",
            }

        # Compute semantic similarities
        similarities = self._compute_similarities(query_text, related_papers)

        # Score novelty
        score, assessment = self._score_novelty(similarities)

        return {
            "overall_novelty_score": round(score, 1),
            "assessment": assessment,
            "similar_papers": similarities[:8],
            "research_gaps": self._identify_research_gaps(abstract, related_papers),
            "novelty_indicators": self._extract_novelty_indicators(abstract, methodology),
            "papers_compared": len(related_papers),
            "data_source": "OpenAlex",
        }

    async def _fetch_related_papers(self, query: str, keywords: List[str]) -> List[Dict]:
        """Fetch related papers from OpenAlex."""
        papers = []
        try:
            params = {
                "search": query[:200],
                "per-page": 15,
                "select": "id,title,abstract_inverted_index,publication_year,doi,primary_location,cited_by_count",
            }
            if self.email:
                params["mailto"] = self.email

            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.get(f"{self.OPENALEX_BASE}/works", params=params)
                if resp.status_code == 200:
                    data = resp.json()
                    results = data.get("results", [])
                    for item in results:
                        abstract = self._reconstruct_abstract(
                            item.get("abstract_inverted_index", {})
                        )
                        papers.append({
                            "title": item.get("title", "Untitled"),
                            "abstract": abstract,
                            "year": item.get("publication_year"),
                            "doi": item.get("doi", ""),
                            "url": item.get("doi", ""),
                            "citations": item.get("cited_by_count", 0),
                            "venue": item.get("primary_location", {}).get("source", {}).get("display_name", "Unknown") if item.get("primary_location") else "Unknown",
                        })
        except Exception as e:
            logger.warning(f"OpenAlex fetch error: {e}")

        return papers

    def _reconstruct_abstract(self, inverted_index: Dict) -> str:
        """Reconstruct abstract from OpenAlex inverted index format."""
        if not inverted_index:
            return ""
        try:
            word_positions = []
            for word, positions in inverted_index.items():
                for pos in positions:
                    word_positions.append((pos, word))
            word_positions.sort(key=lambda x: x[0])
            return " ".join(w for _, w in word_positions)
        except Exception:
            return ""

    def _compute_similarities(self, query_text: str, papers: List[Dict]) -> List[Dict]:
        """Compute semantic similarity between query and each paper."""
        embedder = self._get_embedder()

        if embedder is None:
            # Fallback: TF-IDF cosine similarity
            return self._tfidf_similarities(query_text, papers)

        try:
            from sklearn.metrics.pairwise import cosine_similarity
            import numpy as np

            texts = [p.get("abstract") or p.get("title", "") for p in papers]
            texts = [t for t in texts if t.strip()]
            if not texts:
                return []

            all_texts = [query_text] + texts
            embeddings = embedder.encode(all_texts, show_progress_bar=False)
            query_emb = embeddings[0:1]
            paper_embs = embeddings[1:]

            sims = cosine_similarity(query_emb, paper_embs)[0]

            results = []
            for i, paper in enumerate(papers[:len(texts)]):
                if i < len(sims):
                    sim_pct = round(float(sims[i]) * 100, 1)
                    results.append({
                        "title": paper["title"],
                        "abstract_snippet": (paper.get("abstract") or "")[:300],
                        "year": paper.get("year"),
                        "doi": paper.get("doi", ""),
                        "venue": paper.get("venue", ""),
                        "citations": paper.get("citations", 0),
                        "similarity_percentage": sim_pct,
                        "overlap_level": self._categorize_similarity(sim_pct),
                    })

            results.sort(key=lambda x: x["similarity_percentage"], reverse=True)
            return results

        except Exception as e:
            logger.warning(f"Embedding similarity error: {e}")
            return self._tfidf_similarities(query_text, papers)

    def _tfidf_similarities(self, query_text: str, papers: List[Dict]) -> List[Dict]:
        """Fallback TF-IDF based similarity."""
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.metrics.pairwise import cosine_similarity

            texts = [p.get("abstract") or p.get("title", "") for p in papers]
            texts = [t if t.strip() else "empty" for t in texts]

            vectorizer = TfidfVectorizer(max_features=1000, stop_words="english")
            all_texts = [query_text] + texts
            tfidf_matrix = vectorizer.fit_transform(all_texts)
            sims = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:])[0]

            results = []
            for i, paper in enumerate(papers):
                sim_pct = round(float(sims[i]) * 100, 1) if i < len(sims) else 0.0
                results.append({
                    "title": paper["title"],
                    "abstract_snippet": (paper.get("abstract") or "")[:300],
                    "year": paper.get("year"),
                    "doi": paper.get("doi", ""),
                    "venue": paper.get("venue", ""),
                    "citations": paper.get("citations", 0),
                    "similarity_percentage": sim_pct,
                    "overlap_level": self._categorize_similarity(sim_pct),
                })

            results.sort(key=lambda x: x["similarity_percentage"], reverse=True)
            return results
        except Exception as e:
            logger.error(f"TF-IDF error: {e}")
            return []

    def _categorize_similarity(self, sim_pct: float) -> str:
        if sim_pct >= 70:
            return "High Overlap"
        elif sim_pct >= 45:
            return "Moderate Overlap"
        elif sim_pct >= 20:
            return "Low Overlap"
        else:
            return "Minimal Overlap"

    def _score_novelty(self, similarities: List[Dict]) -> tuple:
        if not similarities:
            return 60.0, "No comparison papers found. Novelty assessment is inconclusive."

        top_sims = [s["similarity_percentage"] for s in similarities[:5]]
        avg_top_sim = sum(top_sims) / len(top_sims)
        max_sim = max(top_sims)

        # Novelty score is inverse of similarity
        base_score = max(0, 100 - avg_top_sim)
        penalty = max(0, (max_sim - 60) * 0.5) if max_sim > 60 else 0
        score = max(10, min(95, base_score - penalty))

        if score >= 75:
            assessment = "The paper shows strong novelty indicators with low overlap to existing published work."
        elif score >= 55:
            assessment = "The paper shows moderate novelty. Some overlap with existing work is present, but unique contributions may exist."
        elif score >= 35:
            assessment = "The paper has significant overlap with existing research. Clearer articulation of unique contributions is needed."
        else:
            assessment = "High overlap detected with existing research. The paper's novelty requires substantial strengthening."

        assessment += " Note: Similarity scores do not confirm plagiarism — they indicate thematic relatedness."
        return score, assessment

    def _identify_research_gaps(self, abstract: str, papers: List[Dict]) -> List[str]:
        gaps = []
        gap_keywords = [
            "however", "limitation", "challenge", "gap", "unexplored",
            "not yet", "lack", "insufficient", "future", "remains"
        ]
        sentences = abstract.split(".")
        for sent in sentences:
            if any(kw in sent.lower() for kw in gap_keywords):
                gaps.append(sent.strip() + ".")

        if not gaps:
            gaps.append("No explicit research gaps identified in the abstract. Consider adding a gap statement.")

        return gaps[:5]

    def _extract_novelty_indicators(self, abstract: str, methodology: str) -> List[str]:
        indicators = []
        novelty_keywords = [
            "novel", "propose", "new approach", "first", "innovative",
            "original", "contribution", "introduce", "present a", "this paper"
        ]
        text = f"{abstract} {methodology}".lower()
        sentences = (abstract + " " + methodology).split(".")

        for sent in sentences:
            if any(kw in sent.lower() for kw in novelty_keywords):
                indicators.append(sent.strip() + ".")

        return indicators[:5]
