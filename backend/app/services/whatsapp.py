"""
GBP Audit Bot - WhatsApp Integration

Integration with WhatsApp gateways (Evolution API, Z-API, etc.)
for sending weekly reports to client groups.
Based on pdf-script.md specifications.
"""
import httpx
from typing import Optional
from dataclasses import dataclass

from app.config import get_settings


settings = get_settings()


@dataclass
class WhatsAppMessage:
    """WhatsApp message structure."""
    group_id: str  # JID format: 123456789@g.us
    caption: str
    image_url: Optional[str] = None
    image_base64: Optional[str] = None


def format_weekly_report_message(
    business_name: str,
    avg_rank: float,
    prev_avg_rank: Optional[float],
    top3_count: int,
    total_points: int,
    visibility_score: float,
    period_start: str,
    period_end: str,
    insight: Optional[str] = None,
    dashboard_url: Optional[str] = None
) -> str:
    """
    Format the weekly report message for WhatsApp.
    
    Uses WhatsApp markdown formatting:
    - *bold*
    - _italic_
    - ~strikethrough~
    - ```code```
    
    Returns:
        Formatted message string ready for WhatsApp
    """
    # Calculate trend
    if prev_avg_rank and prev_avg_rank > 0:
        improvement = ((prev_avg_rank - avg_rank) / prev_avg_rank) * 100
        if improvement > 0:
            trend_text = f"+{improvement:.0f}% 📈"
        elif improvement < 0:
            trend_text = f"{improvement:.0f}% 📉"
        else:
            trend_text = "Estável →"
    else:
        trend_text = "Primeira análise"
    
    # Build message parts
    message_parts = [
        f"🚀 *Relatório Semanal: {business_name}*",
        f"📅 _Período: {period_start} a {period_end}_",
        "",
        "📊 *Resumo de Performance:*",
        f"• Posição Média na Grade: *{avg_rank:.1f}* ({trend_text})",
        f"• Pontos no Top 3: *{top3_count} de {total_points}*",
        f"• Visibilidade: *{visibility_score:.0f}%*",
    ]
    
    # Add insight if available
    if insight:
        message_parts.extend([
            "",
            "📍 *Análise da Equipe:*",
            f"_{insight}_"
        ])
    
    # Add dashboard link
    if dashboard_url:
        message_parts.extend([
            "",
            f"🔗 Dashboard completo: {dashboard_url}"
        ])
    
    # Footer
    message_parts.extend([
        "",
        "💻 *Equipe Locuz* ⚡"
    ])
    
    return "\n".join(message_parts)


async def send_whatsapp_message(
    message: WhatsAppMessage,
    api_url: Optional[str] = None,
    api_key: Optional[str] = None
) -> dict:
    """
    Send a message to WhatsApp via gateway API.
    
    Supports Evolution API format, adaptable to other gateways.
    
    Args:
        message: WhatsAppMessage with group_id, caption, and optional image
        api_url: Gateway API endpoint (uses settings if not provided)
        api_key: API key (uses settings if not provided)
    
    Returns:
        API response as dict
    """
    url = api_url or getattr(settings, 'whatsapp_api_url', None)
    key = api_key or getattr(settings, 'whatsapp_api_key', None)
    
    if not url or not key:
        raise ValueError("WhatsApp API URL and key must be configured")
    
    headers = {
        "apikey": key,
        "Content-Type": "application/json"
    }
    
    # Build payload based on whether we have an image
    if message.image_url:
        payload = {
            "number": message.group_id,
            "media": message.image_url,
            "caption": message.caption,
            "mediaType": "image"
        }
        endpoint = f"{url}/message/sendMedia"
    elif message.image_base64:
        payload = {
            "number": message.group_id,
            "mediaBase64": message.image_base64,
            "caption": message.caption,
            "mediaType": "image"
        }
        endpoint = f"{url}/message/sendMedia"
    else:
        payload = {
            "number": message.group_id,
            "text": message.caption
        }
        endpoint = f"{url}/message/sendText"
    
    async with httpx.AsyncClient() as client:
        response = await client.post(endpoint, json=payload, headers=headers, timeout=30.0)
        response.raise_for_status()
        return response.json()


async def send_weekly_report(
    group_id: str,
    business_name: str,
    avg_rank: float,
    prev_avg_rank: Optional[float],
    top3_count: int,
    total_points: int,
    visibility_score: float,
    period_start: str,
    period_end: str,
    heatmap_url: Optional[str] = None,
    insight: Optional[str] = None,
    dashboard_url: Optional[str] = None,
    api_url: Optional[str] = None,
    api_key: Optional[str] = None
) -> dict:
    """
    Convenience function to format and send a weekly report.
    
    This is the main entry point for the cron job.
    """
    caption = format_weekly_report_message(
        business_name=business_name,
        avg_rank=avg_rank,
        prev_avg_rank=prev_avg_rank,
        top3_count=top3_count,
        total_points=total_points,
        visibility_score=visibility_score,
        period_start=period_start,
        period_end=period_end,
        insight=insight,
        dashboard_url=dashboard_url
    )
    
    message = WhatsAppMessage(
        group_id=group_id,
        caption=caption,
        image_url=heatmap_url
    )
    
    return await send_whatsapp_message(message, api_url, api_key)
