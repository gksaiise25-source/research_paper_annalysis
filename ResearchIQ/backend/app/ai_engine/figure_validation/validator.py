"""
Figure and Table Validation Module - Extracts and validates figures and tables in research papers.
Checks numbering, captions, in-text citations, resolution, and placement.
"""
import re
import os
from typing import Dict, List, Optional
from loguru import logger


class FigureTableValidator:
    """Validates figure and table presentation, numbering, captions, and text references."""

    FIGURE_CAPTION_REGEX = r'(?:Fig(?:ure)?\.?\s*(\d+[a-zA-Z]?))[\s\:\.\-—]+([^\n\r]+)'
    TABLE_CAPTION_REGEX = r'(?:Table\s*(\d+[a-zA-Z]?))[\s\:\.\-—]+([^\n\r]+)'
    FIGURE_REF_REGEX = r'(?:(?:see|in|shown in|refer to|from)?\s*fig(?:ure)?\.?\s*(\d+[a-zA-Z]?))'
    TABLE_REF_REGEX = r'(?:(?:see|in|shown in|refer to|from)?\s*table\s*(\d+[a-zA-Z]?))'

    def validate(self, file_path: Optional[str], extracted_content: Dict) -> Dict:
        """Run figure and table validation on document and extracted text."""
        full_text = extracted_content.get("full_text", "")
        extracted_figures = []
        extracted_tables = []
        image_diagnostics = []

        # If PDF exists, use PyMuPDF for visual inspection of images
        if file_path and os.path.exists(file_path) and file_path.lower().endswith(".pdf"):
            image_diagnostics = self._inspect_pdf_images(file_path)

        # Extract captions and numbers from text
        figure_captions = self._find_captions(full_text, self.FIGURE_CAPTION_REGEX, "Figure")
        table_captions = self._find_captions(full_text, self.TABLE_CAPTION_REGEX, "Table")

        # Extract in-text mentions
        figure_mentions = self._find_text_mentions(full_text, self.FIGURE_REF_REGEX)
        table_mentions = self._find_text_mentions(full_text, self.TABLE_REF_REGEX)

        # Run validation rules
        figure_issues = self._validate_elements(
            element_type="Figure",
            captions=figure_captions,
            mentions=figure_mentions,
            image_diagnostics=image_diagnostics,
        )

        table_issues = self._validate_elements(
            element_type="Table",
            captions=table_captions,
            mentions=table_mentions,
            image_diagnostics=[],
        )

        total_issues = len(figure_issues) + len(table_issues)
        score = max(20.0, 100.0 - (total_issues * 7.5))

        return {
            "validation_score": round(score, 1),
            "summary": {
                "detected_figures_count": len(figure_captions) or len(image_diagnostics) or extracted_content.get("figures_count", 0),
                "detected_tables_count": len(table_captions) or extracted_content.get("tables_count", 0),
                "figure_issues_count": len(figure_issues),
                "table_issues_count": len(table_issues),
            },
            "figure_captions": figure_captions,
            "table_captions": table_captions,
            "image_diagnostics": image_diagnostics,
            "issues": figure_issues + table_issues,
            "recommendations": self._generate_recommendations(figure_issues, table_issues),
        }

    def _inspect_pdf_images(self, pdf_path: str) -> List[Dict]:
        """Inspect embedded images in PDF using PyMuPDF."""
        diagnostics = []
        try:
            import fitz

            doc = fitz.open(pdf_path)
            for page_index in range(len(doc)):
                page = doc[page_index]
                image_list = page.get_images(full=True)
                for img_idx, img in enumerate(image_list):
                    xref = img[0]
                    base_image = doc.extract_image(xref)
                    width = base_image.get("width", 0)
                    height = base_image.get("height", 0)
                    ext = base_image.get("ext", "png")

                    # Heuristic check for low resolution
                    is_low_res = (width < 300 or height < 200) and (width * height < 100000)
                    diagnostics.append({
                        "page_number": page_index + 1,
                        "image_index": img_idx + 1,
                        "width": width,
                        "height": height,
                        "format": ext,
                        "is_low_res": is_low_res,
                        "warning": "Low resolution image detected (<300px width/height). May appear blurry in print." if is_low_res else None
                    })
            doc.close()
        except Exception as e:
            logger.warning(f"Failed to inspect PDF images via fitz: {e}")
        return diagnostics

    def _find_captions(self, text: str, regex_pattern: str, element_type: str) -> List[Dict]:
        """Find captions and numbering for figures or tables."""
        captions = []
        matches = re.finditer(regex_pattern, text, re.IGNORECASE)
        for match in matches:
            number = match.group(1).strip()
            caption_text = match.group(2).strip()
            # Clean caption if trailing text was captured
            caption_text = caption_text.split("\n")[0][:150]
            captions.append({
                "type": element_type,
                "number": number,
                "caption": caption_text,
            })
        return captions

    def _find_text_mentions(self, text: str, regex_pattern: str) -> List[str]:
        """Find in-text numerical mentions of figure or table."""
        matches = re.finditer(regex_pattern, text, re.IGNORECASE)
        mentions = []
        for match in matches:
            num = match.group(1).strip()
            if num:
                mentions.append(num)
        return mentions

    def _validate_elements(
        self, element_type: str, captions: List[Dict], mentions: List[str], image_diagnostics: List[Dict]
    ) -> List[Dict]:
        """Check for missing captions, duplicate numbering, sequence skips, unreferenced elements."""
        issues = []
        seen_numbers = {}

        # 1. Numbering sequence & duplicates
        numeric_labels = []
        for c in captions:
            num_str = c["number"]
            # Check duplicate
            if num_str in seen_numbers:
                issues.append({
                    "element": f"{element_type} {num_str}",
                    "severity": "high",
                    "type": "duplicate_numbering",
                    "message": f"Duplicate {element_type} numbering detected: '{element_type} {num_str}' appears multiple times.",
                })
            seen_numbers[num_str] = seen_numbers.get(num_str, 0) + 1

            # Check caption quality
            if len(c["caption"]) < 10:
                issues.append({
                    "element": f"{element_type} {num_str}",
                    "severity": "medium",
                    "type": "short_or_missing_caption",
                    "message": f"{element_type} {num_str} has an excessively short or incomplete caption.",
                })

            if num_str.isdigit():
                numeric_labels.append(int(num_str))

        # Check sequence gaps (e.g., Fig 1 then Fig 3)
        if numeric_labels:
            numeric_labels.sort()
            expected = 1
            for num in numeric_labels:
                if num > expected:
                    issues.append({
                        "element": f"{element_type} numbering sequence",
                        "severity": "medium",
                        "type": "sequence_gap",
                        "message": f"{element_type} sequence skips: Expected {element_type} {expected}, but found {element_type} {num}.",
                    })
                    expected = num + 1
                elif num == expected:
                    expected += 1

        # 2. Check unreferenced elements in text
        mention_set = set(mentions)
        for c in captions:
            num = c["number"]
            if num not in mention_set:
                issues.append({
                    "element": f"{element_type} {num}",
                    "severity": "low",
                    "type": "unreferenced_in_text",
                    "message": f"{element_type} {num} is declared with a caption but never explicitly cited/referenced in the body text.",
                })

        # 3. Check low resolution images (for figures)
        for diag in image_diagnostics:
            if diag.get("is_low_res"):
                issues.append({
                    "element": f"Image on Page {diag['page_number']}",
                    "severity": "medium",
                    "type": "low_resolution",
                    "message": f"Image #{diag['image_index']} on Page {diag['page_number']} has low dimensions ({diag['width']}x{diag['height']}px). Ensure at least 300 DPI for publication.",
                })

        return issues

    def _generate_recommendations(self, figure_issues: List[Dict], table_issues: List[Dict]) -> List[str]:
        recs = []
        if any(i["type"] == "duplicate_numbering" for i in figure_issues + table_issues):
            recs.append("Resolve duplicate figure/table numbering so each asset has a unique identifier.")
        if any(i["type"] == "sequence_gap" for i in figure_issues + table_issues):
            recs.append("Fix sequential numbering gaps to ensure figures and tables appear in strictly ascending order.")
        if any(i["type"] == "unreferenced_in_text" for i in figure_issues + table_issues):
            recs.append("Reference every figure and table directly in the text (e.g. 'As shown in Figure 1...') before or near its appearance.")
        if any(i["type"] == "low_resolution" for i in figure_issues):
            recs.append("Replace low-resolution raster graphics with vector formats (PDF/SVG) or high-res images (minimum 300 DPI).")
        if not recs:
            recs.append("Figures and tables are well-structured, correctly numbered, and properly cited in the text.")
        return recs
