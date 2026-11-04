"""
Paper Processing Module - Extracts text and structure from PDF/DOCX files.
"""
import re
import os
from typing import Dict, List, Optional, Tuple
from pathlib import Path
from loguru import logger


class PaperExtractor:
    """Extracts structured content from research paper PDFs and DOCX files."""

    SECTION_PATTERNS = {
        "abstract": [r"abstract", r"summary"],
        "introduction": [r"introduction", r"1\.\s*introduction", r"i\.\s*introduction"],
        "literature_review": [
            r"literature\s+review", r"related\s+work", r"background",
            r"2\.\s*literature", r"ii\.\s*related"
        ],
        "methodology": [
            r"methodology", r"methods?", r"approach", r"proposed\s+method",
            r"3\.\s*method", r"iii\.\s*method"
        ],
        "results": [
            r"results?", r"experiments?", r"evaluation", r"findings",
            r"4\.\s*result", r"iv\.\s*result"
        ],
        "discussion": [r"discussion", r"analysis"],
        "conclusion": [
            r"conclusion", r"future\s+work", r"concluding\s+remarks",
            r"5\.\s*conclusion", r"v\.\s*conclusion"
        ],
        "references": [r"references", r"bibliography", r"works\s+cited"],
    }

    def extract_from_pdf(self, file_path: str) -> Dict:
        """Extract text and structure from a PDF file."""
        try:
            import fitz  # PyMuPDF

            doc = fitz.open(file_path)
            full_text_parts = []
            page_texts = []

            for page_num, page in enumerate(doc):
                text = page.get_text("text")
                page_texts.append({"page": page_num + 1, "text": text})
                full_text_parts.append(text)

            full_text = "\n".join(full_text_parts)
            doc.close()

            return self._process_text(full_text, page_texts, len(page_texts))

        except Exception as e:
            logger.error(f"PDF extraction error: {e}")
            raise RuntimeError(f"Failed to extract PDF: {str(e)}")

    def extract_from_docx(self, file_path: str) -> Dict:
        """Extract text and structure from a DOCX file."""
        try:
            from docx import Document

            doc = Document(file_path)
            paragraphs = []
            for para in doc.paragraphs:
                if para.text.strip():
                    paragraphs.append(para.text)

            full_text = "\n".join(paragraphs)

            # Count tables
            tables_count = len(doc.tables)

            result = self._process_text(full_text, [], 0)
            result["tables_count"] = tables_count
            return result

        except Exception as e:
            logger.error(f"DOCX extraction error: {e}")
            raise RuntimeError(f"Failed to extract DOCX: {str(e)}")

    def _process_text(self, full_text: str, page_texts: list, page_count: int) -> Dict:
        """Process extracted text to identify sections and metadata."""
        sections = self._identify_sections(full_text)
        keywords = self._extract_keywords(full_text, sections.get("abstract", ""))
        title = self._extract_title(full_text)
        references = self._extract_references(sections.get("references", full_text))
        word_count = len(full_text.split())
        figures_count = self._count_figures(full_text)
        tables_count = self._count_tables(full_text)

        return {
            "full_text": full_text[:50000],  # Limit stored text
            "title": title,
            "abstract": sections.get("abstract", ""),
            "introduction": sections.get("introduction", ""),
            "literature_review": sections.get("literature_review", ""),
            "methodology": sections.get("methodology", ""),
            "results": sections.get("results", ""),
            "discussion": sections.get("discussion", ""),
            "conclusion": sections.get("conclusion", ""),
            "references_text": sections.get("references", ""),
            "keywords": keywords,
            "sections": {k: len(v) for k, v in sections.items()},
            "references_list": references,
            "word_count": word_count,
            "page_count": page_count,
            "figures_count": figures_count,
            "tables_count": tables_count,
        }

    def _identify_sections(self, text: str) -> Dict[str, str]:
        """Identify and extract sections from the paper."""
        lines = text.split("\n")
        sections = {}
        current_section = "preamble"
        current_content = []
        section_order = []

        for line in lines:
            line_stripped = line.strip()
            if not line_stripped:
                current_content.append("")
                continue

            detected = self._detect_section_header(line_stripped)
            if detected:
                # Save previous section
                if current_content:
                    sections[current_section] = "\n".join(current_content).strip()
                current_section = detected
                section_order.append(detected)
                current_content = []
            else:
                current_content.append(line)

        # Save last section
        if current_content:
            sections[current_section] = "\n".join(current_content).strip()

        return sections

    def _detect_section_header(self, line: str) -> Optional[str]:
        """Detect if a line is a section header."""
        line_lower = line.lower().strip()

        # Skip if line is too long to be a header
        if len(line) > 100:
            return None

        for section_name, patterns in self.SECTION_PATTERNS.items():
            for pattern in patterns:
                if re.match(r'^' + pattern + r'[\s\.\:]*$', line_lower, re.IGNORECASE):
                    return section_name
                # Also check numbered sections like "1. Introduction"
                if re.match(r'^\d+[\.\)]\s*' + pattern, line_lower, re.IGNORECASE):
                    return section_name

        return None

    def _extract_title(self, text: str) -> str:
        """Extract paper title from the first few lines."""
        lines = [l.strip() for l in text.split("\n") if l.strip()]
        # Title is usually in the first 10 lines, longer than 20 chars
        for line in lines[:10]:
            if 20 < len(line) < 200 and not line.lower().startswith(("abstract", "introduction")):
                return line
        return lines[0] if lines else "Untitled Paper"

    def _extract_keywords(self, full_text: str, abstract: str) -> List[str]:
        """Extract keywords from abstract or keywords section."""
        keywords = []

        # Look for explicit keywords section
        kw_match = re.search(
            r'(?:keywords?|index\s+terms?)\s*[:\-—]\s*(.+?)(?:\n\n|\Z)',
            full_text,
            re.IGNORECASE | re.DOTALL
        )
        if kw_match:
            kw_text = kw_match.group(1).strip()
            # Split by common delimiters
            keywords = [k.strip() for k in re.split(r'[;,·•]', kw_text) if k.strip()]
            keywords = [k for k in keywords if len(k) < 50][:10]

        return keywords

    def _extract_references(self, references_text: str) -> List[str]:
        """Parse individual references from the references section."""
        if not references_text:
            return []

        refs = []
        # Split by numbered references [1], [2], etc. or (1), 1., etc.
        patterns = [
            r'\[\d+\]',
            r'\(\d+\)',
            r'^\d+\.',
        ]

        lines = references_text.split("\n")
        current_ref = []
        for line in lines:
            line_stripped = line.strip()
            is_new_ref = any(re.match(p, line_stripped) for p in patterns)
            if is_new_ref and current_ref:
                refs.append(" ".join(current_ref))
                current_ref = [line_stripped]
            elif line_stripped:
                current_ref.append(line_stripped)

        if current_ref:
            refs.append(" ".join(current_ref))

        return refs[:100]  # Limit to 100 references

    def _count_figures(self, text: str) -> int:
        """Count figures mentioned in the paper."""
        matches = re.findall(
            r'fig(?:ure)?\.?\s*\d+|figure\s+\d+',
            text,
            re.IGNORECASE
        )
        numbers = set()
        for m in matches:
            nums = re.findall(r'\d+', m)
            if nums:
                numbers.add(nums[0])
        return len(numbers)

    def _count_tables(self, text: str) -> int:
        """Count tables mentioned in the paper."""
        matches = re.findall(r'table\s*\d+', text, re.IGNORECASE)
        numbers = set()
        for m in matches:
            nums = re.findall(r'\d+', m)
            if nums:
                numbers.add(nums[0])
        return len(numbers)
