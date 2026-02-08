"""
GBP Audit Bot - AI Analysis Service

Generates narrative reports using OpenAI for weekly client updates.
Based on the get_ai_analysis function from esqueleto.md.
"""
from dataclasses import dataclass
from typing import Optional
import httpx

from app.config import get_settings


settings = get_settings()


@dataclass
class WeeklyStats:
    """Stats format matching esqueleto.md for AI analysis."""
    arp: float | None  # Average Rank Position
    top3: int          # Count of top 3 positions
    total_points: int  # Total grid points (e.g., 25 for 5x5)


async def get_ai_analysis(
    business_name: str,
    current_stats: WeeklyStats,
    prev_stats: Optional[WeeklyStats],
    actions: Optional[str] = None,
    api_key: Optional[str] = None
) -> str:
    """
    Generate an AI-powered analysis report for WhatsApp delivery.
    
    Uses OpenAI GPT-4o to create a consultative narrative comparing
    current performance with previous week.
    
    Args:
        business_name: Name of the business being analyzed
        current_stats: Current week's scan statistics
        prev_stats: Previous week's statistics (or None if first scan)
        actions: Team actions taken this week (for context)
        api_key: OpenAI API key (uses settings if not provided)
    
    Returns:
        Formatted report text ready for WhatsApp.
    
    Example:
        >>> current = WeeklyStats(arp=3.2, top3=18, total_points=25)
        >>> prev = WeeklyStats(arp=8.5, top3=5, total_points=25)
        >>> report = await get_ai_analysis("Restaurante Sabor Local", current, prev, "Otimizamos as categorias do GBP")
    """
    key = api_key or settings.openai_api_key
    
    if not key:
        return _generate_fallback_report(business_name, current_stats, prev_stats, actions)
    
    system_prompt = """
    Você é o Lead Growth Analyst da Locuz. Sua missão é escrever um relatório de SEO Local 
    para WhatsApp. Seja direto, use emojis e foque em resultados. 
    Compare os dados atuais com os da semana passada.
    
    Formato esperado:
    - Máximo 300 palavras
    - Use emojis para destacar pontos importantes
    - Inclua: resumo de performance, comparativo, e próximos passos
    - Tom: profissional mas acessível
    """
    
    # Build comparison text
    if prev_stats:
        comparison = f"""
        Dados Passados (semana anterior): 
        - ARP: {prev_stats.arp or 'N/A'}
        - Top 3: {prev_stats.top3}/{prev_stats.total_points} pontos
        """
    else:
        comparison = "Esta é a primeira análise - não há dados anteriores para comparação."
    
    user_content = f"""
    Empresa: {business_name}
    
    Dados Atuais:
    - ARP (Average Rank Position): {current_stats.arp or 'Não encontrado'}
    - Top 3: {current_stats.top3}/{current_stats.total_points} pontos da grade
    
    {comparison}
    
    Ações da Equipe Locuz: {actions or 'Nenhuma ação registrada esta semana.'}
    
    Gere um relatório conciso para enviar via WhatsApp ao cliente.
    """
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "gpt-4o",
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_content}
                    ],
                    "max_tokens": 500,
                    "temperature": 0.7
                },
                timeout=30.0
            )
            
            if response.status_code == 200:
                data = response.json()
                return data["choices"][0]["message"]["content"]
            else:
                # Fallback on API error
                return _generate_fallback_report(business_name, current_stats, prev_stats, actions)
                
    except Exception:
        return _generate_fallback_report(business_name, current_stats, prev_stats, actions)


def _generate_fallback_report(
    business_name: str,
    current_stats: WeeklyStats,
    prev_stats: Optional[WeeklyStats],
    actions: Optional[str]
) -> str:
    """
    Generate a simple report without AI when OpenAI is unavailable.
    """
    lines = [
        f"📊 *Relatório Semanal - {business_name}*",
        "",
        "📍 *Visibilidade Local*",
        f"• Posição Média (ARP): {current_stats.arp or 'N/A'}",
        f"• Top 3: {current_stats.top3}/{current_stats.total_points} pontos",
    ]
    
    if prev_stats and prev_stats.arp and current_stats.arp:
        diff = prev_stats.arp - current_stats.arp
        if diff > 0:
            lines.append(f"• Melhoria: ⬆️ +{diff:.1f} posições")
        elif diff < 0:
            lines.append(f"• Variação: ⬇️ {diff:.1f} posições")
    
    if actions:
        lines.extend(["", "🎯 *Ações da Semana*", f"• {actions}"])
    
    lines.extend(["", "_Relatório gerado por GBP Audit Bot - Locuz_"])
    
    return "\n".join(lines)
