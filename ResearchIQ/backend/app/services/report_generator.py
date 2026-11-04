"""
PDF Report Generator Service using ReportLab.
Generates an executive, professional academic evaluation report with all 10 features.
"""
import io
import os
from typing import Dict, Any, Optional
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, KeepTogether
)
from reportlab.pdfgen import canvas
from loguru import logger


class NumberedCanvas(canvas.Canvas):
    """Canvas that computes total page count dynamically for footer page numbers."""
    def __init__(self, *args, **kwargs):
        super(NumberedCanvas, self).__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_number(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 9)
        self.setFillColor(colors.HexColor("#64748b"))
        # Header line
        self.setStrokeColor(colors.HexColor("#e2e8f0"))
        self.setLineWidth(0.5)
        self.line(40, letter[1] - 40, letter[0] - 40, letter[1] - 40)
        self.drawString(40, letter[1] - 35, "ResearchIQ — AI Paper Analysis & Publication Readiness Report")

        # Footer
        self.line(40, 45, letter[0] - 40, 45)
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(letter[0] - 40, 32, page_str)
        self.drawString(40, 32, "Confidential — Generated for Author Self-Assessment")
        self.restoreState()


class PDFReportGenerator:
    """Creates downloadable PDF analysis report."""

    def generate(self, paper: Any, extracted: Any, analyses: Dict[str, Any]) -> bytes:
        """Build PDF byte stream containing all 10 feature findings."""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=40,
            leftMargin=40,
            topMargin=55,
            bottomMargin=55,
        )

        styles = getSampleStyleSheet()

        # Custom academic palette styles
        primary_color = colors.HexColor("#1e3a8a")     # Deep Navy
        secondary_color = colors.HexColor("#0284c7")   # Light blue accent
        dark_neutral = colors.HexColor("#1e293b")
        slate_color = colors.HexColor("#475569")

        title_style = ParagraphStyle(
            'DocTitle',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=22,
            leading=26,
            textColor=primary_color,
            spaceAfter=6,
        )

        subtitle_style = ParagraphStyle(
            'DocSubTitle',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=11,
            leading=15,
            textColor=slate_color,
            spaceAfter=12,
        )

        h1_style = ParagraphStyle(
            'Heading1_Custom',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=14,
            leading=18,
            textColor=primary_color,
            spaceBefore=14,
            spaceAfter=6,
        )

        body_style = ParagraphStyle(
            'Body_Custom',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=10,
            leading=14,
            textColor=dark_neutral,
        )

        bullet_style = ParagraphStyle(
            'Bullet_Custom',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=9.5,
            leading=13.5,
            textColor=dark_neutral,
            leftIndent=15,
            firstLineIndent=-10,
            spaceAfter=3,
        )

        story = []

        # 1. Header Banner
        story.append(Paragraph("ResearchIQ Evaluation Report", title_style))
        paper_title = getattr(paper, "title", "Untitled Manuscript") or "Untitled Manuscript"
        paper_file = getattr(paper, "filename", "manuscript.pdf")
        created_str = datetime.now().strftime("%B %d, %Y - %H:%M UTC")

        story.append(Paragraph(
            f"<b>Manuscript:</b> {paper_title}<br/>"
            f"<b>File:</b> {paper_file} &nbsp;|&nbsp; <b>Evaluation Date:</b> {created_str}",
            subtitle_style
        ))
        story.append(HRFlowable(width="100%", thickness=1.5, color=secondary_color, spaceBefore=4, spaceAfter=14))

        # 2. Executive Publication Readiness Summary
        readiness_data = analyses.get("readiness", {})
        readiness_score = readiness_data.get("overall_score", 0.0) if readiness_data else 0.0
        readiness_cat = readiness_data.get("readiness_category", "Pending Review") if readiness_data else "Pending Review"

        score_color = colors.HexColor("#16a34a") if readiness_score >= 80 else (
            colors.HexColor("#ca8a04") if readiness_score >= 60 else colors.HexColor("#dc2626")
        )

        readiness_table_data = [
            [
                Paragraph("<b>Overall Publication Readiness Score</b>", body_style),
                Paragraph(f"<font color='{score_color.hexval()}'><b>{readiness_score} / 100</b></font>", ParagraphStyle('Score', fontName='Helvetica-Bold', fontSize=16, leading=18)),
                Paragraph(f"<b>Recommendation:</b><br/>{readiness_cat}", body_style),
            ]
        ]
        readiness_table = Table(readiness_table_data, colWidths=[200, 140, 190])
        readiness_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#cbd5e1")),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('PADDING', (0, 0), (-1, -1), 8),
        ]))
        story.append(readiness_table)
        story.append(Spacer(1, 12))

        # 3. Category Breakdown Table
        story.append(Paragraph("Multi-Dimensional Metric Breakdown", h1_style))
        cat_scores = readiness_data.get("category_scores", {}) if readiness_data else {}
        cat_table_data = [
            ["Dimension", "Score", "Weight", "Evaluation Status"]
        ]
        for key, details in cat_scores.items():
            if isinstance(details, dict):
                score_str = f"{details.get('score')}%" if details.get('score') is not None else "N/A"
                weight_str = f"{int(details.get('weight', 0) * 100)}%" if details.get('weight') else "—"
                cat_table_data.append([
                    details.get('label', key.replace('_', ' ').title()),
                    score_str,
                    weight_str,
                    details.get('status', 'Completed')
                ])

        if len(cat_table_data) > 1:
            breakdown_table = Table(cat_table_data, colWidths=[220, 80, 80, 150])
            breakdown_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), primary_color),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
                ('PADDING', (0, 0), (-1, -1), 6),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
            ]))
            story.append(breakdown_table)
            story.append(Spacer(1, 14))

        # 4. Feature 1: Technical Review
        tech = analyses.get("technical_review", {})
        if tech:
            story.append(Paragraph("1. Automated Technical Review", h1_style))
            story.append(Paragraph(
                f"<b>Overall Structural Score:</b> {tech.get('overall_score', 0)}% &nbsp;|&nbsp; "
                f"<b>Words Analyzed:</b> {tech.get('word_count', 0)}", body_style
            ))
            story.append(Spacer(1, 4))
            for s in tech.get("strengths", [])[:3]:
                story.append(Paragraph(f"• <b>Strength:</b> {s}", bullet_style))
            for w in tech.get("weaknesses", [])[:3]:
                story.append(Paragraph(f"• <b>Area for Improvement:</b> {w}", bullet_style))
            story.append(Spacer(1, 10))

        # 5. Feature 2: Novelty Analysis
        novelty = analyses.get("novelty", {})
        if novelty:
            story.append(Paragraph("2. Novelty Analysis & Scholarly Discovery", h1_style))
            story.append(Paragraph(f"<b>Novelty Score:</b> {novelty.get('overall_novelty_score', 'N/A')}%", body_style))
            story.append(Paragraph(novelty.get("assessment", ""), body_style))
            sim_papers = novelty.get("similar_papers", [])[:3]
            if sim_papers:
                story.append(Spacer(1, 4))
                story.append(Paragraph("<b>Top Thematically Related Publications:</b>", body_style))
                for p in sim_papers:
                    p_title = p.get("title", "Untitled")
                    p_sim = p.get("similarity_percentage", 0)
                    p_year = p.get("year", "")
                    story.append(Paragraph(f"• <b>{p_title}</b> ({p_year}) — {p_sim}% similarity overlap", bullet_style))
            story.append(Spacer(1, 10))

        # 6. Feature 3: Citation Analysis
        citations = analyses.get("citations", {})
        if citations:
            story.append(Paragraph("3. Citation & Bibliographic Analysis", h1_style))
            story.append(Paragraph(
                f"<b>Style Detected:</b> {citations.get('detected_style', 'IEEE')} &nbsp;|&nbsp; "
                f"<b>Total References:</b> {citations.get('total_references', 0)} &nbsp;|&nbsp; "
                f"<b>In-text Citations:</b> {citations.get('total_intext_citations', 0)}", body_style
            ))
            for rec in citations.get("recommendations", [])[:3]:
                story.append(Paragraph(f"• {rec}", bullet_style))
            story.append(Spacer(1, 10))

        # 7. Feature 4: Grammar & Language Enhancement
        grammar = analyses.get("grammar", {})
        if grammar:
            story.append(Paragraph("4. Grammar, Language & Tone Analysis", h1_style))
            story.append(Paragraph(
                f"<b>Language Score:</b> {grammar.get('grammar_score', 0)}% &nbsp;|&nbsp; "
                f"<b>Academic Tone Score:</b> {grammar.get('academic_tone_score', 0)}% &nbsp;|&nbsp; "
                f"<b>Readability:</b> {grammar.get('readability_score', {}).get('level', 'Academic')}", body_style
            ))
            for sug in grammar.get("suggestions", [])[:3]:
                orig = sug.get("original", "")[:60]
                rec = sug.get("suggestion", "")
                story.append(Paragraph(f"• <i>'{orig}'</i> &rarr; <b>{rec}</b>", bullet_style))
            story.append(Spacer(1, 10))

        # 8. Feature 5: Plagiarism Risk Detection
        plag = analyses.get("plagiarism", {})
        if plag:
            story.append(Paragraph("5. Plagiarism Risk & Originality Assessment", h1_style))
            story.append(Paragraph(
                f"<b>Risk Level:</b> {plag.get('overall_risk_level', 'Minimal Risk')} &nbsp;|&nbsp; "
                f"<b>Originality Indicator:</b> {plag.get('originality_indicator', 100)}%", body_style
            ))
            story.append(Paragraph(f"<font color='#64748b' size='8'>{plag.get('disclaimer', '')}</font>", body_style))
            story.append(Spacer(1, 10))

        # 9. Feature 6: Figures & Tables
        fig_tbl = analyses.get("figures_tables", {})
        if fig_tbl:
            story.append(Paragraph("6. Figure and Table Validation", h1_style))
            summary = fig_tbl.get("summary", {})
            story.append(Paragraph(
                f"<b>Figures Detected:</b> {summary.get('detected_figures_count', 0)} &nbsp;|&nbsp; "
                f"<b>Tables Detected:</b> {summary.get('detected_tables_count', 0)} &nbsp;|&nbsp; "
                f"<b>Validation Score:</b> {fig_tbl.get('validation_score', 100)}%", body_style
            ))
            for rec in fig_tbl.get("recommendations", [])[:2]:
                story.append(Paragraph(f"• {rec}", bullet_style))
            story.append(Spacer(1, 10))

        # 10. Feature 7: AI Reviewer Comments
        reviewer = analyses.get("reviewer_comments", {})
        if reviewer:
            story.append(Paragraph("7. Peer Reviewer Critique & Recommendations", h1_style))
            story.append(Paragraph(f"<b>Reviewer Verdict:</b> {reviewer.get('recommendation', 'Minor Revision')}", body_style))
            story.append(Paragraph(f"<i>{reviewer.get('overall_assessment', '')}</i>", body_style))
            story.append(Spacer(1, 4))
            for maj in reviewer.get("major_revisions", [])[:2]:
                story.append(Paragraph(f"• <b>Major Action:</b> {maj}", bullet_style))
            for minr in reviewer.get("minor_revisions", [])[:2]:
                story.append(Paragraph(f"• <b>Minor Action:</b> {minr}", bullet_style))
            story.append(Spacer(1, 10))

        # 11. Feature 8: Journal Recommendations
        journals = analyses.get("journals", {})
        if journals:
            story.append(Paragraph("8. Recommended Publication Venues", h1_style))
            rec_venues = journals.get("recommendations", [])[:3]
            for v in rec_venues:
                story.append(Paragraph(
                    f"• <b>{v.get('name')}</b> ({v.get('type')}) — Publisher: {v.get('publisher')} | "
                    f"Suitability: <b>{v.get('suitability_score')}%</b>", bullet_style
                ))
            story.append(Spacer(1, 10))

        # 12. Feature 9: Patentability Indicator
        patent = analyses.get("patentability", {})
        if patent:
            story.append(Paragraph("9. Patentability Screening Indicator", h1_style))
            story.append(Paragraph(
                f"<b>Tier:</b> {patent.get('readiness_tier')} &nbsp;|&nbsp; "
                f"<b>Preliminary Score:</b> {patent.get('overall_patentability_score', 0)}%", body_style
            ))
            for concern in patent.get("eligibility_concerns", [])[:2]:
                story.append(Paragraph(f"• {concern}", bullet_style))
            story.append(Paragraph(f"<font color='#64748b' size='8'>{patent.get('disclaimer', '')}</font>", body_style))
            story.append(Spacer(1, 10))

        # 13. Improvement Checklist
        story.append(Paragraph("10. Author Action Checklist Prior to Submission", h1_style))
        for item in readiness_data.get("priority_improvements", []) if readiness_data else []:
            story.append(Paragraph(f"[  ] {item}", bullet_style))

        # Build PDF with dynamic 2-pass page numbers
        doc.build(story, canvasmaker=NumberedCanvas)
        buffer.seek(0)
        return buffer.getvalue()
