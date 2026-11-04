"""
Citation Analysis Module - Validates references and in-text citations.
"""
import re
from typing import Dict, List, Optional, Tuple
from loguru import logger
import httpx


class CitationAnalyser:

    CROSSREF_BASE = "https://api.crossref.org/works"

    # Common citation style patterns
    INTEXT_PATTERNS = {
        "IEEE": r'\[(\d+(?:,\s*\d+)*)\]',
        "APA": r'\(([A-Z][a-z]+(?:\s+(?:et\s+al\.?|&\s+[A-Z][a-z]+))?,\s*\d{4}[a-z]?(?:,\s*p\.?\s*\d+)?)\)',
        "MLA": r'\(([A-Z][a-z]+\s+\d+(?:[-–]\d+)?)\)',
    }

    REF_PATTERNS = {
        "IEEE": r'^\[(\d+)\]\s+(.+)',
        "APA": r'^([A-Z][a-z]+(?:,\s+[A-Z]\.)+(?:,\s+&\s+[A-Z][a-z]+(?:,\s+[A-Z]\.)+)?\s*\(\d{4}\))',
        "numbered": r'^(\d+)\.\s+(.+)',
    }

    DOI_PATTERN = r'10\.\d{4,}/[^\s]+'

    def analyse(self, extracted_content: Dict) -> Dict:
        """Analyse citations in the paper."""
        full_text = extracted_content.get("full_text", "")
        references_text = extracted_content.get("references_text", "")
        references_list = extracted_content.get("references_list", [])

        # Detect citation style
        style = self._detect_citation_style(full_text)

        # Extract in-text citations
        intext_citations = self._extract_intext_citations(full_text, style)

        # Parse reference list
        parsed_refs = references_list or self._parse_references(references_text, style)

        # Cross-check
        issues = self._cross_check_citations(intext_citations, parsed_refs, style)

        # Check DOIs
        doi_issues = self._check_doi_format(parsed_refs)

        # Duplicate check
        duplicates = self._find_duplicates(parsed_refs)

        # Completeness check
        incomplete = self._check_completeness(parsed_refs)

        total_issues = len(issues) + len(doi_issues) + len(duplicates) + len(incomplete)
        score = max(0, 100 - (total_issues * 5))

        return {
            "detected_style": style,
            "total_references": len(parsed_refs),
            "total_intext_citations": len(set(intext_citations)),
            "issues": {
                "cross_reference_issues": issues[:20],
                "doi_issues": doi_issues[:10],
                "duplicates": duplicates[:10],
                "incomplete_references": incomplete[:10],
            },
            "total_issue_count": total_issues,
            "citation_score": round(score, 1),
            "sample_references": parsed_refs[:5],
            "recommendations": self._generate_recommendations(style, issues, duplicates, incomplete),
        }

    def _detect_citation_style(self, text: str) -> str:
        """Detect citation style from paper text."""
        ieee_count = len(re.findall(self.INTEXT_PATTERNS["IEEE"], text))
        apa_count = len(re.findall(self.INTEXT_PATTERNS["APA"], text))
        mla_count = len(re.findall(self.INTEXT_PATTERNS["MLA"], text))

        if ieee_count >= apa_count and ieee_count >= mla_count:
            return "IEEE"
        elif apa_count >= ieee_count and apa_count >= mla_count:
            return "APA"
        elif mla_count > 0:
            return "MLA"
        return "IEEE"  # Default

    def _extract_intext_citations(self, text: str, style: str) -> List[str]:
        """Extract all in-text citation keys."""
        pattern = self.INTEXT_PATTERNS.get(style, self.INTEXT_PATTERNS["IEEE"])
        matches = re.findall(pattern, text)
        citations = []
        for match in matches:
            if style == "IEEE":
                nums = [n.strip() for n in match.split(",")]
                citations.extend(nums)
            else:
                citations.append(match)
        return citations

    def _parse_references(self, ref_text: str, style: str) -> List[str]:
        """Parse references from reference section text."""
        if not ref_text:
            return []

        lines = [l.strip() for l in ref_text.split("\n") if l.strip()]
        refs = []
        current_ref = []

        for line in lines:
            is_new = (
                re.match(r'^\[\d+\]', line) or
                re.match(r'^\d+\.\s', line) or
                re.match(r'^[A-Z][a-z]+,\s+[A-Z]\.', line)
            )
            if is_new and current_ref:
                refs.append(" ".join(current_ref))
                current_ref = [line]
            else:
                current_ref.append(line)

        if current_ref:
            refs.append(" ".join(current_ref))

        return refs

    def _cross_check_citations(
        self, intext: List[str], refs: List[str], style: str
    ) -> List[Dict]:
        issues = []
        if style == "IEEE":
            # Extract reference numbers from refs list
            ref_numbers = set()
            for ref in refs:
                m = re.match(r'^\[(\d+)\]', ref.strip())
                if m:
                    ref_numbers.add(m.group(1))

            intext_set = set(intext)

            # Citations without references
            for cite in intext_set:
                if cite not in ref_numbers and ref_numbers:
                    issues.append({
                        "type": "citation_without_reference",
                        "description": f"In-text citation [{cite}] has no matching reference entry.",
                        "citation": f"[{cite}]",
                    })

            # References not cited
            for ref_num in ref_numbers:
                if ref_num not in intext_set and intext_set:
                    issues.append({
                        "type": "reference_not_cited",
                        "description": f"Reference [{ref_num}] is listed but never cited in the text.",
                        "citation": f"[{ref_num}]",
                    })

        return issues

    def _check_doi_format(self, refs: List[str]) -> List[Dict]:
        issues = []
        for i, ref in enumerate(refs):
            dois = re.findall(self.DOI_PATTERN, ref)
            for doi in dois:
                # Basic DOI validation
                if not doi.startswith("10."):
                    issues.append({
                        "type": "invalid_doi",
                        "description": f"Potentially malformed DOI in reference {i+1}: {doi}",
                        "reference_index": i + 1,
                    })
        return issues

    def _find_duplicates(self, refs: List[str]) -> List[Dict]:
        duplicates = []
        seen = {}
        for i, ref in enumerate(refs):
            # Use first 60 chars as key
            key = ref[:60].lower().strip()
            if key in seen:
                duplicates.append({
                    "type": "duplicate_reference",
                    "description": f"Reference {i+1} appears to be a duplicate of reference {seen[key]+1}.",
                    "reference_index": i + 1,
                })
            else:
                seen[key] = i
        return duplicates

    def _check_completeness(self, refs: List[str]) -> List[Dict]:
        incomplete = []
        for i, ref in enumerate(refs):
            issues_found = []
            if not re.search(r'\d{4}', ref):
                issues_found.append("missing year")
            if len(ref) < 40:
                issues_found.append("possibly incomplete")
            if not any(c.isupper() for c in ref):
                issues_found.append("no author name detected")

            if issues_found:
                incomplete.append({
                    "type": "incomplete_reference",
                    "description": f"Reference {i+1} may be incomplete: {', '.join(issues_found)}.",
                    "reference_index": i + 1,
                    "reference_snippet": ref[:80],
                })

        return incomplete

    def _generate_recommendations(
        self, style: str, issues: List, duplicates: List, incomplete: List
    ) -> List[str]:
        recs = [f"Detected citation style: {style}. Ensure consistency throughout."]
        if issues:
            recs.append(f"Resolve {len(issues)} cross-reference issue(s) between in-text citations and the reference list.")
        if duplicates:
            recs.append(f"Remove {len(duplicates)} duplicate reference(s).")
        if incomplete:
            recs.append(f"Complete {len(incomplete)} incomplete reference(s) with missing author, year, or title information.")
        recs.append("Verify all DOIs are valid and accessible.")
        recs.append("Ensure all referenced work is relevant to your research.")
        return recs
