Aqui está o "esqueleto" mestre em Python. Este script une a lógica matemática da grade, a inteligência da IA para análise e a estrutura de disparo.

Ele foi desenhado de forma modular, para que você possa apenas plugar as suas chaves de API (OpenAI e seu Gateway de WhatsApp).

```python
import math
import openai # pip install openai
import requests

# === 1. CONFIGURAÇÕES E CHAVES ===
OPENAI_API_KEY = "sua_chave_aqui"
WHATSAPP_API_URL = "https://sua-api-whatsapp.com/message/send"
WHATSAPP_API_KEY = "sua_chave_wa_aqui"

# === 2. LÓGICA DA GRADE (GEOGRID) ===
def generate_grid(lat, lng, radius_km, grid_size=5):
    points = []
    step_distance = (radius_km * 2000) / (grid_size - 1)
    start_offset = (grid_size - 1) / 2
    
    for row in range(grid_size):
        for col in range(grid_size):
            offset_lat = (start_offset - row) * step_distance
            offset_lng = (col - start_offset) * step_distance
            
            new_lat = lat + (offset_lat / 111111)
            new_lng = lng + (offset_lng / (111111 * math.cos(math.radians(lat))))
            
            points.append({"lat": round(new_lat, 6), "lng": round(new_lng, 6)})
    return points

# === 3. SIMULAÇÃO DE COLETA DE DADOS (API DE SERP) ===
def get_rankings_mock(points):
    # Aqui você chamaria a DataForSEO ou Scale SERP
    # Retornando ranks aleatórios para o exemplo
    import random
    return [random.randint(1, 20) for _ in points]

# === 4. ANALISTA DE IA (OPENAI) ===
def get_ai_analysis(business_name, current_stats, prev_stats, actions):
    client = openai.OpenAI(api_key=OPENAI_API_KEY)
    
    system_prompt = """
    Você é o Lead Growth Analyst da Locuz. Sua missão é escrever um relatório de SEO Local 
    para WhatsApp. Seja direto, use emojis e foque em resultados. 
    Compare os dados atuais com os da semana passada.
    """
    
    user_content = f"""
    Empresa: {business_name}
    Dados Atuais: ARP {current_stats['arp']}, Top3: {current_stats['top3']}/25
    Dados Passados: ARP {prev_stats['arp']}, Top3: {prev_stats['top3']}/25
    Ações da Equipe: {actions}
    """
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content}
        ]
    )
    return response.choices[0].message.content

# === 5. FLUXO PRINCIPAL (ORQUESTRADOR) ===
def run_weekly_report(client_data):
    print(f"🚀 Iniciando relatório para: {client_data['name']}")
    
    # 1. Gerar Grade
    grid = generate_grid(client_data['lat'], client_data['lng'], radius_km=2)
    
    # 2. Buscar Rankings (Simulado)
    ranks = get_rankings_mock(grid)
    
    # 3. Calcular Métricas
    avg_rank = round(sum(ranks) / len(ranks), 1)
    top3_count = len([r for r in ranks if r <= 3])
    
    current_stats = {'arp': avg_rank, 'top3': top3_count}
    prev_stats = client_data['last_week_stats'] # Dados vindos do seu banco
    
    # 4. Gerar Texto com IA
    report_text = get_ai_analysis(
        client_data['name'], 
        current_stats, 
        prev_stats, 
        client_data['actions']
    )
    
    # 5. Simular Envio para o WhatsApp
    print("\n--- MENSAGEM PARA O WHATSAPP ---")
    print(report_text)
    # Aqui você chamaria requests.post(WHATSAPP_API_URL, ...)

# === EXECUÇÃO DO PROTÓTIPO ===
cliente_exemplo = {
    "name": "Restaurante Sabor Local",
    "lat": -23.5505,
    "lng": -46.6333,
    "actions": "Otimizamos as categorias do GBP e adicionamos 5 novas fotos de pratos principais.",
    "last_week_stats": {"arp": 8.5, "top3": 5}
}

run_weekly_report(cliente_exemplo)

```

### O que este script entrega:

1. **Precisão Geográfica:** A função `generate_grid` cria a matriz exata que as APIs de busca local exigem.
2. **Cálculo Automático de KPIs:** Ele já extrai a Média de Ranking (ARP) e a contagem de Top 3.
3. **Análise Consultiva:** O `get_ai_analysis` transforma os números frios em uma narrativa de consultoria da Locuz.

### Como evoluir para Produção:

* **Banco de Dados:** Substitua o dicionário `cliente_exemplo` por uma query no seu banco (Supabase/Postgres) para rodar isso em um loop para todos os clientes.
* **Image Generation:** Antes do passo 5, você inseriria a função que discutimos anteriormente para gerar a imagem do mapa e fazer o upload para um bucket.
* **Agendamento:** Coloque esse script para rodar em um servidor (como uma Google Cloud Function ou um simples VPS com um `cron job`) toda segunda-feira às 09:00.