
"""
AthleteVision AI PDF Performance Report Generator.

Generates reports from measured computer-vision results.
No fabricated performance scores or measurements.
"""

from datetime import datetime
from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    KeepTogether,
)


GREEN = colors.HexColor("#087F60")
DARK = colors.HexColor("#17243B")
LIGHT = colors.HexColor("#EDF8F3")
GREY = colors.HexColor("#64748B")


def clean(value):
    """Convert values safely for PDF paragraphs."""
    if value is None:
        return "Not available"

    text = str(value)

    # Built-in Helvetica does not contain every Unicode symbol.
    text = (
        text.replace("\u00b0", " degrees")
        .replace("\u2013", "-")
        .replace("\u2014", "-")
        .replace("\u2022", "-")
    )

    return escape(text)


def format_metric(name):
    """Convert JSON measurement keys to readable labels."""
    labels = {
        "average_knee_angle_deg": "Average knee angle (deg)",
        "min_knee_angle_deg": "Minimum knee angle (deg)",
        "average_torso_inclination_deg":
            "Average torso inclination (deg)",
        "max_torso_inclination_deg":
            "Maximum torso inclination (deg)",
        "torso_variability_deg": "Torso variability (deg)",
        "left_knee_range_deg": "Left knee movement range (deg)",
        "right_knee_range_deg": "Right knee movement range (deg)",
        "left_knee_visibility_ratio":
            "Left knee visibility ratio",
        "right_knee_visibility_ratio":
            "Right knee visibility ratio",
        "ankle_crossings_per_min_proxy":
            "Ankle crossings/min (proxy)",
        "frames_with_pose": "Frames with detected pose",
        "average_technique_score":
            "Experimental screening score",
    }

    return labels.get(
        name,
        name.replace("_", " ").title()
    )


def draw_footer(canvas, doc):
    canvas.saveState()

    width, _ = doc.pagesize

    canvas.setStrokeColor(colors.HexColor("#D9E4E1"))
    canvas.line(40, 45, width - 40, 45)

    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(GREY)

    canvas.drawString(
        40, 31,
        "AthleteVision AI | Computer Vision Research Prototype"
    )

    canvas.drawRightString(
        width - 40, 31,
        f"Page {doc.page}"
    )

    canvas.restoreState()


def generate_pdf(result, output_path):
    """
    Create a PDF for a completed analysis.

    Args:
        result: Analysis dictionary returned by pipeline.py.
        output_path: Path where the PDF should be saved.
    """

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=(595.28, 841.89),
        rightMargin=40,
        leftMargin=40,
        topMargin=48,
        bottomMargin=65,
    )

    styles = getSampleStyleSheet()

    styles.add(
        ParagraphStyle(
            name="AVTitle",
            fontName="Helvetica-Bold",
            fontSize=21,
            leading=27,
            textColor=DARK,
            spaceAfter=10,
        )
    )

    styles.add(
        ParagraphStyle(
            name="AVSection",
            fontName="Helvetica-Bold",
            fontSize=12,
            leading=16,
            textColor=GREEN,
            spaceBefore=14,
            spaceAfter=8,
        )
    )

    styles.add(
        ParagraphStyle(
            name="AVBody",
            fontName="Helvetica",
            fontSize=9,
            leading=14,
            textColor=DARK,
            spaceAfter=7,
        )
    )

    styles.add(
        ParagraphStyle(
            name="AVSmall",
            fontName="Helvetica",
            fontSize=8,
            leading=12,
            textColor=GREY,
            spaceAfter=6,
        )
    )

    styles.add(
        ParagraphStyle(
            name="AVCenter",
            parent=styles["AVBody"],
            alignment=TA_CENTER,
        )
    )

    story = []

    body = styles["AVBody"]
    section = styles["AVSection"]
    small = styles["AVSmall"]

    def p(text, style=None):
        return Paragraph(clean(text), style or body)

    def heading(text):
        story.append(Paragraph(clean(text), section))

    def info_table(rows):
        if not rows:
            return

        formatted = [
            [
                p(label),
                p(value),
            ]
            for label, value in rows
        ]

        table = Table(
            formatted,
            colWidths=[235, 280],
            hAlign="LEFT",
            repeatRows=0,
        )

        table.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), LIGHT),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 10),
                ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                ("TOPPADDING", (0, 0), (-1, -1), 7),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
                ("LINEBELOW", (0, 0), (-1, -1),
                 0.35, colors.white),
            ])
        )

        story.append(table)

    sport = result.get("sport", "unknown")

    sport_name = {
        "squat": "Weightlifting - Squat",
        "running": "Running",
    }.get(sport, sport.title())

    generated_at = datetime.now().strftime(
        "%d %B %Y, %I:%M %p"
    )

    # -------------------------------------------------
    # REPORT TITLE
    # -------------------------------------------------

    story.append(
        Paragraph(
            "ATHLETEVISION AI",
            styles["AVTitle"],
        )
    )

    story.append(
        Paragraph(
            "Sports Performance Analysis Report",
            styles["AVSection"],
        )
    )

    story.append(
        p(
            "Computer-vision based movement screening. "
            "This is an educational analysis report, "
            "not a certified coaching or medical assessment.",
            small,
        )
    )

    story.append(Spacer(1, 12))

    # -------------------------------------------------
    # ANALYSIS OVERVIEW
    # -------------------------------------------------

    heading("1. Analysis Overview")

    overview = [
        ("Sport", sport_name),
        ("Report generated", generated_at),
        ("Assessment", result.get(
            "assessment", "Not available"
        )),
    ]

    if sport == "squat":
        overview.append(
            ("Detected repetitions", result.get("reps"))
        )

    video = result.get("video") or {}

    if video.get("duration_s") is not None:
        overview.append(
            ("Video duration", f"{video['duration_s']} seconds")
        )

    info_table(overview)

    # -------------------------------------------------
    # PERFORMANCE METRICS
    # -------------------------------------------------

    heading("2. Performance Measurements")

    metrics = result.get("metrics") or {}

    metric_rows = [
        (format_metric(key), value)
        for key, value in metrics.items()
        if value is not None
    ]

    if metric_rows:
        info_table(metric_rows)
    else:
        story.append(p("No reliable measurements available."))

    # -------------------------------------------------
    # COACHING OBSERVATIONS
    # -------------------------------------------------

    heading("3. Movement Observations and Recommendations")

    issues = result.get("issues") or []

    if not issues:
        story.append(
            p(
                "No issue was flagged by the current "
                "screening rules. This does not establish "
                "that technique is correct or safe."
            )
        )

    for index, issue in enumerate(issues, start=1):
        title = issue.get("title", "Observation")
        detail = issue.get("detail", "")
        tip = (
            issue.get("tip")
            or issue.get("correction")
            or "Review with a qualified coach."
        )

        content = [
            Paragraph(
                clean(f"{index}. {title}"),
                section,
            ),
            p(detail),
            p(f"Recommendation: {tip}"),
        ]

        if issue.get("time_s") is not None:
            content.append(
                p(f"Timestamp: {issue['time_s']} seconds", small)
            )

        story.append(KeepTogether(content))

    # -------------------------------------------------
    # REP-BY-REP SQUAT REVIEW
    # -------------------------------------------------

    rep_details = result.get("rep_details") or []

    if sport == "squat" and rep_details:
        heading("4. Repetition-by-Repetition Review")

        for rep in rep_details:
            number = rep.get("rep", "?")

            content = [
                Paragraph(
                    clean(f"Repetition {number}"),
                    section,
                )
            ]

            rows = [
                ("Start time (s)", rep.get("start_s")),
                ("Bottom time (s)", rep.get("bottom_s")),
                ("End time (s)", rep.get("end_s")),
                (
                    "Minimum knee angle (deg)",
                    rep.get("min_knee_angle_deg"),
                ),
                (
                    "Maximum torso inclination (deg)",
                    rep.get("max_torso_inclination_deg"),
                ),
                (
                    "Experimental screening score",
                    rep.get("technique_score"),
                ),
            ]

            content.append(
                Paragraph(
                    clean(
                        " | ".join(
                            f"{label}: {value}"
                            for label, value in rows
                        )
                    ),
                    body,
                )
            )

            findings = rep.get("findings") or []

            if findings:
                for finding in findings:
                    content.append(
                        p(
                            finding.get(
                                "title", "Technique review"
                            )
                        )
                    )
                    content.append(
                        p(
                            finding.get(
                                "correction", ""
                            )
                        )
                    )
            else:
                content.append(
                    p(
                        "No issue flagged by the current "
                        "experimental screening checks."
                    )
                )

            story.extend(content)

    # -------------------------------------------------
    # LIMITATIONS
    # -------------------------------------------------

    heading("5. Limitations")

    limitations = result.get("limitations") or []

    for item in limitations:
        story.append(p(f"- {item}"))

    story.append(
        p(
            "Interpret the findings with a qualified "
            "sports coach. Camera viewpoint, lighting, "
            "occlusion and landmark accuracy can affect "
            "the reported measurements.",
            small,
        )
    )

    # -------------------------------------------------
    # BUILD PDF
    # -------------------------------------------------

    doc.build(
        story,
        onFirstPage=draw_footer,
        onLaterPages=draw_footer,
    )

    return output_path
