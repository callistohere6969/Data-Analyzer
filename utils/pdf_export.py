"""PDF Export utility for analysis results"""

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
import pandas as pd


def _escape_html(text: str) -> str:
    """Escape special characters for ReportLab"""
    if text is None:
        return ""
    text = str(text)
    text = text.replace('&', '&amp;')
    text = text.replace('<', '&lt;')
    text = text.replace('>', '&gt;')
    text = text.replace('\n', '<br/>')
    return text


def generate_pdf_report(
    state: Dict[str, Any],
    output_path: str,
    title: str = "Data Analysis Report"
) -> tuple[bool, Optional[str]]:
    """
    Generate comprehensive PDF report from analysis state
    
    Args:
        state: Analysis state with all results
        output_path: Path to save PDF
        title: Report title
    
    Returns:
        Tuple of (success, error_message)
    """
    try:
        # Ensure output directory exists
        output_dir = Path(output_path).parent
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Create PDF document
        doc = SimpleDocTemplate(output_path, pagesize=letter,
                               rightMargin=72, leftMargin=72,
                               topMargin=72, bottomMargin=18)
        
        # Container for PDF elements
        story = []
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1f77b4'),
            spaceAfter=30,
            alignment=TA_CENTER
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=12,
            spaceBefore=12
        )
        
        # Title
        story.append(Paragraph(title, title_style))
        story.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Executive Summary
        if state.get("final_summary"):
            story.append(Paragraph("Executive Summary", heading_style))
            summary_text = _escape_html(state["final_summary"])
            story.append(Paragraph(summary_text, styles['Normal']))
            story.append(Spacer(1, 20))
        
        # Data Quality Score
        profile = state.get("profile_result", {})
        if profile and "data_quality_score" in profile:
            story.append(Paragraph("Data Quality Assessment", heading_style))
            score_data = profile["data_quality_score"]
            score = score_data["score"]
            
            quality_table_data = [
                ["Metric", "Value"],
                ["Overall Quality Score", f"{score}/100"],
                ["Missing Values", f"{score_data.get('missing_percentage', 0):.2f}%"],
                ["Duplicate Rows", f"{score_data.get('duplicate_percentage', 0):.2f}%"],
                ["Outliers", f"{score_data.get('outlier_percentage', 0):.2f}%"],
            ]
            
            quality_table = Table(quality_table_data, colWidths=[3*inch, 3*inch])
            quality_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(quality_table)
            story.append(Spacer(1, 20))
        
        # Data Profile
        if profile:
            story.append(Paragraph("Data Profile", heading_style))
            
            overview = profile.get("overview", {})
            if overview:
                data = [
                    ["Metric", "Value"],
                    ["Total Rows", f"{overview.get('total_rows', 'N/A'):,}"],
                    ["Total Columns", str(overview.get('total_columns', 'N/A'))],
                    ["Memory Usage (MB)", f"{overview.get('memory_usage_mb', 0):.2f}"]
                ]
                
                table = Table(data, colWidths=[3*inch, 3*inch])
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 12),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                story.append(table)
                story.append(Spacer(1, 20))
        
        # Key Insights
        insights = state.get("insights_result", [])
        if insights:
            story.append(Paragraph("Key Insights", heading_style))
            for i, insight in enumerate(insights[:10], 1):
                title_text = f"<b>{i}. {_escape_html(str(insight.get('title', 'Insight')))}</b>"
                story.append(Paragraph(title_text, styles['Normal']))
                desc_text = _escape_html(str(insight.get('description', 'No description')))
                story.append(Paragraph(desc_text, styles['Normal']))
                story.append(Spacer(1, 10))
        
        # Anomalies
        anomalies = state.get("anomalies_result", [])
        if anomalies:
            story.append(PageBreak())
            story.append(Paragraph("Detected Anomalies", heading_style))
            for i, anomaly in enumerate(anomalies[:10], 1):
                title_text = f"<b>{i}. {_escape_html(str(anomaly.get('title', 'Anomaly')))}</b>"
                story.append(Paragraph(title_text, styles['Normal']))
                desc_text = _escape_html(str(anomaly.get('description', 'No description')))
                story.append(Paragraph(desc_text, styles['Normal']))
                story.append(Spacer(1, 10))
        
        # Footer
        story.append(PageBreak())
        story.append(Spacer(1, 100))
        footer_text = f"<i>Report generated by Multi-Agent Data Analyzer | {datetime.now().strftime('%Y-%m-%d')}</i>"
        story.append(Paragraph(footer_text, ParagraphStyle('Footer', parent=styles['Normal'], 
                                                           fontSize=8, alignment=TA_CENTER)))
        
        # Build PDF
        doc.build(story)
        return True, None
        
    except Exception as e:
        return False, f"Error generating PDF: {str(e)}"


def create_quick_summary_pdf(df: pd.DataFrame, output_path: str) -> tuple[bool, Optional[str]]:
    """
    Create a quick PDF summary of a DataFrame
    
    Args:
        df: DataFrame to summarize
        output_path: Path to save PDF
    
    Returns:
        Tuple of (success, error_message)
    """
    try:
        # Ensure output directory exists
        output_dir = Path(output_path).parent
        output_dir.mkdir(parents=True, exist_ok=True)
        
        doc = SimpleDocTemplate(output_path, pagesize=letter)
        story = []
        styles = getSampleStyleSheet()
        
        # Title
        story.append(Paragraph("Data Summary Report", styles['Title']))
        story.append(Spacer(1, 20))
        
        # Basic stats
        data = [
            ["Metric", "Value"],
            ["Total Rows", f"{len(df):,}"],
            ["Total Columns", str(len(df.columns))],
            ["Memory Usage", f"{df.memory_usage(deep=True).sum() / 1024**2:.2f} MB"]
        ]
        
        table = Table(data, colWidths=[3*inch, 3*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(table)
        
        doc.build(story)
        return True, None
        
    except Exception as e:
        return False, f"Error creating PDF: {str(e)}"
