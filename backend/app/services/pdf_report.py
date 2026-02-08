"""
GBP Audit Bot - PDF Report Generator

Generates professional PDF reports using ReportLab.
"""
import io
from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from dataclasses import dataclass

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.enums import TA_CENTER, TA_LEFT

from PIL import Image as PILImage


# Locuz brand colors
LOCUZ_GREEN = colors.HexColor("#22c55e")
LOCUZ_YELLOW = colors.HexColor("#eab308")
LOCUZ_RED = colors.HexColor("#ef4444")
LOCUZ_DARK = colors.HexColor("#1C1E21")
LOCUZ_ACCENT = colors.HexColor("#3b82f6")


@dataclass
class ReportData:
    """Data structure for report generation."""
    business_name: str
    keyword: str
    scan_date: datetime
    
    # Current metrics
    current_arp: Optional[float]
    current_top3: int
    current_top10: int
    current_visibility: float
    
    # Previous metrics (for comparison)
    prev_arp: Optional[float] = None
    prev_top3: Optional[int] = None
    prev_visibility: Optional[float] = None
    
    # Grid info
    grid_size: int = 5
    total_points: int = 25
    
    # AI analysis
    ai_analysis: Optional[str] = None
    
    # Team actions
    weekly_actions: Optional[str] = None
    
    # Heatmap image bytes
    heatmap_image: Optional[bytes] = None


def generate_pdf_report(data: ReportData) -> bytes:
    """
    Generate a PDF report for the weekly scan.
    
    Args:
        data: ReportData with all metrics and optional heatmap image
    
    Returns:
        PDF file as bytes
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm
    )
    
    # Styles
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=LOCUZ_ACCENT,
        spaceAfter=12,
        alignment=TA_CENTER
    )
    
    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Normal'],
        fontSize=12,
        textColor=colors.gray,
        alignment=TA_CENTER,
        spaceAfter=20
    )
    
    section_style = ParagraphStyle(
        'Section',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=LOCUZ_DARK,
        spaceBefore=16,
        spaceAfter=8
    )
    
    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontSize=11,
        leading=14
    )
    
    # Content elements
    elements = []
    
    # Header
    elements.append(Paragraph("📍 GBP Audit Bot - Relatório Semanal", title_style))
    elements.append(Paragraph(
        f"<b>{data.business_name}</b><br/>"
        f"Análise gerada em {data.scan_date.strftime('%d/%m/%Y')}",
        subtitle_style
    ))
    elements.append(Spacer(1, 10))
    
    # Keyword info
    # elements.append(Paragraph(f"🔍 Palavra-chave: <i>\"{data.keyword}\"</i>", body_style))
    # elements.append(Spacer(1, 15))
    
    # Metrics table
    elements.append(Paragraph("📊 Resumo de Performance", section_style))
    
    metrics_data = [
        ["Métrica", "Atual", "Anterior", "Variação"],
        [
            "Posição Média (ARP)",
            f"{data.current_arp:.1f}" if data.current_arp else "—",
            f"{data.prev_arp:.1f}" if data.prev_arp else "—",
            _format_change(data.prev_arp, data.current_arp, reverse=True) if data.prev_arp else "—"
        ],
        [
            "Top 3 (Local Pack)",
            f"{data.current_top3}/{data.total_points}",
            f"{data.prev_top3}/{data.total_points}" if data.prev_top3 is not None else "—",
            _format_change(data.prev_top3, data.current_top3) if data.prev_top3 is not None else "—"
        ],
        [
            "Visibilidade",
            f"{data.current_visibility:.0f}%",
            f"{data.prev_visibility:.0f}%" if data.prev_visibility else "—",
            _format_change(data.prev_visibility, data.current_visibility) if data.prev_visibility else "—"
        ],
    ]
    
    table = Table(metrics_data, colWidths=[5*cm, 3*cm, 3*cm, 3*cm])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), LOCUZ_ACCENT),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor("#f8fafc")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('TOPPADDING', (0, 1), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 20))
    
    # Heatmap image (if provided)
    if data.heatmap_image:
        elements.append(Paragraph("🗺️ Mapa de Calor (Geogrid)", section_style))
        
        # Load image to get actual dimensions and preserve aspect ratio
        heatmap_img = PILImage.open(io.BytesIO(data.heatmap_image))
        img_width, img_height = heatmap_img.size
        aspect_ratio = img_height / img_width
        
        # Set width to fit page, calculate height to preserve aspect ratio
        target_width = 16*cm  # Full page width (minus margins)
        target_height = target_width * aspect_ratio
        
        # Cap maximum height to avoid page overflow
        max_height = 12*cm
        if target_height > max_height:
            target_height = max_height
            target_width = target_height / aspect_ratio
        
        img = Image(io.BytesIO(data.heatmap_image), width=target_width, height=target_height)
        elements.append(img)
        elements.append(Spacer(1, 10))
        
        # Legend
        legend_text = (
            "<font color='#22c55e'>● Verde (1-3)</font> &nbsp;&nbsp; "
            "<font color='#eab308'>● Amarelo (4-10)</font> &nbsp;&nbsp; "
            "<font color='#ef4444'>● Vermelho (11+)</font>"
        )
        elements.append(Paragraph(legend_text, ParagraphStyle(
            'Legend', parent=body_style, alignment=TA_CENTER, fontSize=9
        )))
        elements.append(Spacer(1, 15))
    
    # AI Analysis
    if data.ai_analysis:
        elements.append(Paragraph("💡 Análise do Especialista", section_style))
        # Split by lines and format
        for line in data.ai_analysis.split('\n'):
            if line.strip():
                elements.append(Paragraph(line.strip(), body_style))
        elements.append(Spacer(1, 15))
    
    # Weekly actions
    if data.weekly_actions:
        elements.append(Paragraph("🛠️ Ações da Equipe Esta Semana", section_style))
        elements.append(Paragraph(data.weekly_actions, body_style))
        elements.append(Spacer(1, 15))
    
    # Footer
    elements.append(Spacer(1, 30))
    footer_style = ParagraphStyle(
        'Footer', parent=body_style, 
        alignment=TA_CENTER, 
        textColor=colors.gray,
        fontSize=9
    )
    elements.append(Paragraph(
        "Relatório gerado automaticamente por <b>GBP Audit Bot</b> | Locuz ⚡",
        footer_style
    ))
    
    # Build PDF
    doc.build(elements)
    buffer.seek(0)
    
    return buffer.getvalue()


def _format_change(prev: Optional[float], current: Optional[float], reverse: bool = False) -> str:
    """Format the change between two values with arrow indicator."""
    if prev is None or current is None:
        return "—"
    
    diff = current - prev
    if reverse:
        diff = -diff  # For ARP, lower is better
    
    if abs(diff) < 0.01:
        return "→ Estável"
    elif diff > 0:
        return f"↑ +{abs(diff):.1f}"
    else:
        return f"↓ -{abs(diff):.1f}"
