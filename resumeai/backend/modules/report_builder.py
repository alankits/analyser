"""
ReportLab PDF report generator.

Produces a multi-page PDF with:
  Page 1: Cover (name, date, ATS score badge)
  Page 2: ATS breakdown + keyword table
  Pages 3-4: Resume fixes (BEFORE/AFTER)
  Page 5: Career role cards
  Pages 6-7: Learning roadmap
"""

from __future__ import annotations

import io
import logging
from datetime import datetime
from typing import Any

logger = logging.getLogger(__name__)

# Color palette
NAVY = (0.039, 0.063, 0.118)        # #0A0F1E
CARD_BG = (0.067, 0.094, 0.153)     # #111827
INDIGO = (0.388, 0.400, 0.945)      # #6366F1
SUCCESS = (0.063, 0.725, 0.506)     # #10B981
WARNING = (0.961, 0.620, 0.043)     # #F59E0B
DANGER = (0.937, 0.267, 0.267)      # #EF4444
WHITE = (0.976, 0.980, 0.984)       # #F9FAFB
GREY = (0.612, 0.639, 0.686)        # #9CA3AF
RED_TINT = (0.988, 0.220, 0.220, 0.1)
GREEN_TINT = (0.063, 0.725, 0.506, 0.1)


def _score_color(score: int) -> tuple:
    if score >= 80:
        return SUCCESS
    if score >= 60:
        return WARNING
    return DANGER


def _grade_color(grade: str) -> tuple:
    if grade in ("A",):
        return SUCCESS
    if grade in ("B", "C"):
        return WARNING
    return DANGER


def generate_pdf_report(
    candidate_name: str,
    ats_result: dict[str, Any],
    resume_fixes: list[dict[str, Any]],
    career_matches: list[dict[str, Any]],
    roadmap: dict[str, Any],
) -> bytes:
    """Build the full analysis PDF and return it as bytes."""
    try:
        from reportlab.lib.pagesizes import A4  # type: ignore
        from reportlab.lib.units import mm  # type: ignore
        from reportlab.pdfgen import canvas  # type: ignore
        from reportlab.lib.styles import getSampleStyleSheet  # type: ignore
        from reportlab.platypus import (  # type: ignore
            SimpleDocTemplate,
            Paragraph,
            Spacer,
            Table,
            TableStyle,
            PageBreak,
            HRFlowable,
        )
        from reportlab.lib import colors  # type: ignore
        from reportlab.lib.enums import TA_CENTER, TA_LEFT  # type: ignore
        from reportlab.lib.styles import ParagraphStyle  # type: ignore
    except ImportError as exc:
        logger.error("reportlab not available: %s", exc)
        raise

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=15 * mm,
        rightMargin=15 * mm,
        topMargin=22 * mm,
        bottomMargin=15 * mm,
    )

    W, H = A4
    styles = getSampleStyleSheet()

    # Custom styles
    def rgb(*args):
        from reportlab.lib.colors import Color
        return Color(*args)

    navy_color = rgb(*NAVY)
    white_color = rgb(*WHITE)
    grey_color = rgb(*GREY)
    indigo_color = rgb(*INDIGO)
    success_color = rgb(*SUCCESS)
    warning_color = rgb(*WARNING)
    danger_color = rgb(*DANGER)

    def _style(name, **kwargs):
        return ParagraphStyle(name, **kwargs)

    h1 = _style("h1", fontSize=26, fontName="Helvetica-Bold", textColor=white_color, spaceAfter=6, leading=32)
    h2 = _style("h2", fontSize=16, fontName="Helvetica-Bold", textColor=white_color, spaceAfter=4, leading=22)
    h3 = _style("h3", fontSize=12, fontName="Helvetica-Bold", textColor=white_color, spaceAfter=3, leading=16)
    body = _style("body", fontSize=9, fontName="Helvetica", textColor=white_color, spaceAfter=2, leading=13)
    grey_body = _style("grey_body", fontSize=9, fontName="Helvetica", textColor=grey_color, spaceAfter=2, leading=13)
    small = _style("small", fontSize=8, fontName="Helvetica", textColor=grey_color, leading=11)

    score = ats_result.get("overall_score", 0)
    grade = ats_result.get("grade", "?")
    score_col = rgb(*_score_color(score))
    grade_col = rgb(*_grade_color(grade))
    date_str = datetime.now().strftime("%B %d, %Y")
    target_role = roadmap.get("target_role", "")

    story: list = []

    # ── PAGE 1: COVER ────────────────────────────────────────────────────────
    story.append(Spacer(1, 30 * mm))
    story.append(Paragraph("ResumeAI", _style("brand", fontSize=13, fontName="Helvetica", textColor=indigo_color, spaceAfter=4)))
    story.append(Paragraph("Analysis Report", _style("sub", fontSize=11, fontName="Helvetica", textColor=grey_color, spaceAfter=16)))
    story.append(HRFlowable(width="100%", thickness=1, color=indigo_color, spaceAfter=20))
    story.append(Paragraph(candidate_name, h1))
    if target_role:
        story.append(Paragraph(f"Target Role: {target_role}", _style("tr", fontSize=12, fontName="Helvetica", textColor=grey_color, spaceAfter=8)))
    story.append(Paragraph(date_str, grey_body))
    story.append(Spacer(1, 20 * mm))

    # Score badge table
    score_data = [[
        Paragraph(f"ATS Score", _style("sl", fontSize=9, fontName="Helvetica", textColor=grey_color, alignment=1)),
    ], [
        Paragraph(f"{score}", _style("sc", fontSize=36, fontName="Helvetica-Bold", textColor=score_col, alignment=1)),
    ], [
        Paragraph(f"Grade: {grade}", _style("sg", fontSize=12, fontName="Helvetica-Bold", textColor=grade_col, alignment=1)),
    ]]
    badge_table = Table(score_data, colWidths=[60 * mm])
    badge_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), rgb(*CARD_BG)),
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [rgb(*CARD_BG)]),
        ("BOX", (0, 0), (-1, -1), 1, indigo_color),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING", (0, 0), (-1, -1), 12),
        ("RIGHTPADDING", (0, 0), (-1, -1), 12),
    ]))
    story.append(badge_table)
    story.append(PageBreak())

    # ── PAGE 2: ATS BREAKDOWN ────────────────────────────────────────────────
    story.append(Paragraph("ATS Score Breakdown", h2))
    story.append(HRFlowable(width="100%", thickness=1, color=indigo_color, spaceAfter=10))

    section_scores = ats_result.get("section_scores", {})
    ss_data = [["Section", "Score", "Rating"]]
    for section, sec_score in section_scores.items():
        rating = "Good" if sec_score >= 75 else ("Fair" if sec_score >= 50 else "Poor")
        ss_data.append([section.capitalize(), f"{sec_score}/100", rating])

    ss_table = Table(ss_data, colWidths=[80 * mm, 40 * mm, 50 * mm])
    ss_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), rgb(*INDIGO)),
        ("TEXTCOLOR", (0, 0), (-1, 0), white_color),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [rgb(*CARD_BG), rgb(*NAVY)]),
        ("TEXTCOLOR", (0, 1), (-1, -1), white_color),
        ("GRID", (0, 0), (-1, -1), 0.5, rgb(0.2, 0.2, 0.3)),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(ss_table)
    story.append(Spacer(1, 8 * mm))

    # Top issues
    if ats_result.get("top_issues"):
        story.append(Paragraph("Key Issues", h3))
        for issue in ats_result["top_issues"]:
            story.append(Paragraph(f"• {issue}", body))
        story.append(Spacer(1, 6 * mm))

    # Keyword analysis table
    kws = ats_result.get("keyword_analysis", [])
    if kws:
        story.append(Paragraph("Keyword Analysis", h3))
        kw_data = [["Keyword", "Found", "Importance"]]
        for kw in kws[:20]:
            found = "✓" if kw.get("present") else "✗"
            kw_data.append([kw.get("keyword", ""), found, kw.get("importance", "").capitalize()])
        kw_table = Table(kw_data, colWidths=[100 * mm, 30 * mm, 40 * mm])
        kw_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), rgb(*INDIGO)),
            ("TEXTCOLOR", (0, 0), (-1, 0), white_color),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [rgb(*CARD_BG), rgb(*NAVY)]),
            ("TEXTCOLOR", (0, 1), (-1, -1), white_color),
            ("GRID", (0, 0), (-1, -1), 0.5, rgb(0.2, 0.2, 0.3)),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ]))
        story.append(kw_table)

    story.append(PageBreak())

    # ── PAGES 3-4: RESUME FIXES ──────────────────────────────────────────────
    story.append(Paragraph("Resume Fixes: Before & After", h2))
    story.append(HRFlowable(width="100%", thickness=1, color=indigo_color, spaceAfter=10))

    for section_fix in resume_fixes:
        section_name = section_fix.get("section_name", "")
        story.append(Paragraph(section_name, h3))

        issues = section_fix.get("issues", [])
        for issue in issues:
            story.append(Paragraph(f"⚠ {issue}", _style("iss", fontSize=8, fontName="Helvetica", textColor=warning_color, spaceAfter=2)))

        for fix in section_fix.get("fixes", []):
            orig = fix.get("original", "")
            rewr = fix.get("rewritten", "")
            reason = fix.get("reason", "")

            fix_table = Table(
                [[
                    Paragraph(f"<b>BEFORE</b><br/>{orig}", _style("bf", fontSize=8, fontName="Helvetica", textColor=danger_color, leading=12)),
                    Paragraph(f"<b>AFTER</b><br/>{rewr}", _style("af", fontSize=8, fontName="Helvetica", textColor=success_color, leading=12)),
                ]],
                colWidths=[85 * mm, 85 * mm],
            )
            fix_table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (0, 0), rgb(0.3, 0.05, 0.05)),
                ("BACKGROUND", (1, 0), (1, 0), rgb(0.05, 0.2, 0.1)),
                ("BOX", (0, 0), (-1, -1), 0.5, rgb(0.2, 0.2, 0.3)),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ]))
            story.append(fix_table)
            if reason:
                story.append(Paragraph(f"Reason: {reason}", _style("rsn", fontSize=7, fontName="Helvetica-Oblique", textColor=grey_color, spaceAfter=6)))
            story.append(Spacer(1, 3 * mm))

        story.append(Spacer(1, 4 * mm))

    story.append(PageBreak())

    # ── PAGE 5: CAREER MATCHES ───────────────────────────────────────────────
    story.append(Paragraph("Career Role Recommendations", h2))
    story.append(HRFlowable(width="100%", thickness=1, color=indigo_color, spaceAfter=10))

    role_colors = [INDIGO, SUCCESS, (0.502, 0.000, 0.502)]

    for i, role in enumerate(career_matches[:3]):
        role_title = role.get("role_title", "")
        match_pct = role.get("match_score", 0)
        col = rgb(*role_colors[i % len(role_colors)])

        story.append(Paragraph(f"<b>{role_title}</b>  —  Match: {match_pct}%",
                                _style(f"rt{i}", fontSize=11, fontName="Helvetica-Bold", textColor=col, spaceAfter=4)))

        reasons = role.get("match_reasons", [])
        gaps = role.get("skill_gaps", [])
        seniority = role.get("seniority_target", "")
        ttr = role.get("time_to_ready", "")
        proj = role.get("recommended_project", "")

        if reasons:
            story.append(Paragraph("Why you match:", _style("wm", fontSize=9, fontName="Helvetica-Bold", textColor=white_color, spaceAfter=2)))
            for r in reasons:
                story.append(Paragraph(f"  ✓ {r}", body))

        if gaps:
            story.append(Paragraph("Skill gaps to address:", _style("ga", fontSize=9, fontName="Helvetica-Bold", textColor=white_color, spaceAfter=2)))
            for g in gaps:
                story.append(Paragraph(f"  ✗ {g}", _style(f"gp{i}", fontSize=9, fontName="Helvetica", textColor=danger_color, spaceAfter=2)))

        if ttr:
            story.append(Paragraph(f"Time to ready: {ttr}", grey_body))
        if seniority:
            story.append(Paragraph(f"Seniority target: {seniority}", grey_body))
        if proj:
            story.append(Paragraph(f"Recommended project: {proj}", _style("rp", fontSize=9, fontName="Helvetica-Oblique", textColor=indigo_color, spaceAfter=6)))

        story.append(HRFlowable(width="100%", thickness=0.5, color=rgb(0.2, 0.2, 0.3), spaceAfter=8))

    story.append(PageBreak())

    # ── PAGES 6-7: ROADMAP ───────────────────────────────────────────────────
    story.append(Paragraph(f"Learning Roadmap: {roadmap.get('target_role', '')}", h2))
    story.append(Paragraph(
        f"Current level: {roadmap.get('current_level', '')}  |  Total estimated hours: {roadmap.get('total_estimated_hours', 0)}",
        grey_body,
    ))
    story.append(HRFlowable(width="100%", thickness=1, color=indigo_color, spaceAfter=10))

    phase_colors = [INDIGO, SUCCESS, WARNING]

    for phase in roadmap.get("phases", []):
        p_num = phase.get("phase_number", 1)
        p_col = rgb(*phase_colors[(p_num - 1) % len(phase_colors)])

        story.append(Paragraph(
            f"Phase {p_num}  ·  {phase.get('duration', '')}",
            _style(f"ph{p_num}", fontSize=12, fontName="Helvetica-Bold", textColor=p_col, spaceAfter=2),
        ))
        story.append(Paragraph(phase.get("goal", ""), body))
        story.append(Spacer(1, 3 * mm))

        skill_data = [["Skill", "Why It Matters", "Resource", "Hours"]]
        for skill in phase.get("skills", []):
            skill_data.append([
                skill.get("skill_name", ""),
                skill.get("why_it_matters", "")[:80] + ("..." if len(skill.get("why_it_matters", "")) > 80 else ""),
                skill.get("resource_type", ""),
                str(skill.get("estimated_hours", 0)),
            ])

        if len(skill_data) > 1:
            sk_table = Table(skill_data, colWidths=[45 * mm, 80 * mm, 35 * mm, 15 * mm])
            sk_table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), rgb(*CARD_BG)),
                ("TEXTCOLOR", (0, 0), (-1, 0), p_col),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [rgb(*CARD_BG), rgb(*NAVY)]),
                ("TEXTCOLOR", (0, 1), (-1, -1), white_color),
                ("GRID", (0, 0), (-1, -1), 0.5, rgb(0.2, 0.2, 0.3)),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ]))
            story.append(sk_table)

        milestone = phase.get("milestone", "")
        if milestone:
            ms_table = Table(
                [[Paragraph(f"🎯 Milestone: {milestone}", _style(f"ms{p_num}", fontSize=9, fontName="Helvetica-Bold", textColor=indigo_color, leading=13))]],
                colWidths=[175 * mm],
            )
            ms_table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), rgb(0.067, 0.094, 0.27)),
                ("LEFTPADDING", (0, 0), (-1, -1), 10),
                ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                ("LINEAFTER", (0, 0), (0, -1), 3, indigo_color),
            ]))
            story.append(Spacer(1, 3 * mm))
            story.append(ms_table)

        story.append(Spacer(1, 6 * mm))

    # Build PDF with page callback for dark background
    def _add_background(canvas_obj, doc_obj):
        canvas_obj.saveState()
        canvas_obj.setFillColorRGB(*NAVY)
        canvas_obj.rect(0, 0, W, H, fill=1, stroke=0)
        # Dark navy header bar
        canvas_obj.setFillColorRGB(*CARD_BG)
        canvas_obj.rect(0, H - 14 * mm, W, 14 * mm, fill=1, stroke=0)
        # Header text
        canvas_obj.setFillColorRGB(*GREY)
        canvas_obj.setFont("Helvetica", 8)
        canvas_obj.drawString(15 * mm, H - 9 * mm, "ResumeAI Analysis Report")
        canvas_obj.drawRightString(W - 15 * mm, H - 9 * mm, candidate_name)
        # Footer
        canvas_obj.setFont("Helvetica", 7)
        canvas_obj.drawCentredString(W / 2, 8 * mm, f"Page {doc_obj.page}  |  Generated by ResumeAI  |  {date_str}")
        canvas_obj.restoreState()

    doc.build(story, onFirstPage=_add_background, onLaterPages=_add_background)
    return buffer.getvalue()
