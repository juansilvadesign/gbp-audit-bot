Economizar créditos em APIs de busca é a diferença entre uma ferramenta lucrativa e um prejuízo técnico. Para um sistema de Geogrid, o custo pode escalar rápido: uma grade 5x5 (25 pontos) rodada semanalmente para 10 clientes são 1.000 requisições por mês.

Aqui está a estratégia para otimizar essas chamadas e a estrutura técnica para o seu backend.

---

### 1. Escolha da API: Onde está a economia?

Nem todas as APIs tratam coordenadas da mesma forma. Para o seu caso, você precisa de provedores que suportem os parâmetros `location`, `uule` (o parâmetro do Google para localização específica) ou `lat/lng` nativos.

| API | Suporte Geográfico | Custo Médio (1k reqs) | Vantagem para o MVP |
| --- | --- | --- | --- |
| **DataForSEO** | Excelente (API de Mapas) | ~$1.00 - $2.00 | Altamente granular, foca em SEO Local. |
| **Scale SERP** | Muito Bom | ~$3.00 | Interface simples e rápida de integrar. |
| **SerpApi** | Premium | ~$5.00+ | Muito estável, mas o custo escala rápido. |

### 2. Otimização de Chamadas (Batching e Async)

Como cada ponto da grade é uma requisição independente, você não deve rodá-las de forma síncrona (uma após a outra), ou seu bot levará minutos para responder. Usando **Python/FastAPI**, o ideal é usar `httpx` para chamadas assíncronas em lote.

> **Dica de Ouro:** Não processe tudo de uma vez se a grade for grande. Quebre em lotes de 5 para evitar que a API do provedor te bloqueie por excesso de concorrência.

```python
import asyncio
import httpx

async def fetch_rank(client, lat, lng, business_name, keyword):
    params = {
        "api_key": "SUA_CHAVE",
        "q": keyword,
        "location": f"geo:{lat},{lng}", # Sintaxe varia conforme a API
        "google_domain": "google.com.br",
        "gl": "br",
        "hl": "pt"
    }
    
    response = await client.get("https://api.scaleserp.com/search", params=params)
    data = response.json()
    
    # Lógica para encontrar a posição da empresa nos resultados
    position = 20 # Default se não encontrar
    for idx, result in enumerate(data.get("local_results", [])):
        if business_name.lower() in result.get("title", "").lower():
            position = idx + 1
            break
            
    return {"lat": lat, "lng": lng, "rank": position}

async def process_full_grid(points, business_name, keyword):
    async with httpx.AsyncClient() as client:
        tasks = [fetch_rank(client, p['lat'], p['lng'], business_name, keyword) for p in points]
        results = await asyncio.gather(*tasks)
        return results

```

---

### 3. A Estrutura do Banco de Dados (O Relatório)

Para gerar o relatório semanal comparativo sem gastar créditos extras, você precisa de uma tabela que funcione como um "histórico de snapshots".

**Sugestão de Schema (Supabase/PostgreSQL):**

* **`projects`**: `id`, `name`, `target_keyword`, `target_business_id`.
* **`scans`**: `id`, `project_id`, `created_at`, `average_rank`.
* **`scan_points`**: `id`, `scan_id`, `lat`, `lng`, `rank_found`.

Dessa forma, o relatório semanal não precisa de uma nova busca para olhar o passado; ele apenas compara o `scan` de hoje com o `scan` de 7 dias atrás.

---

### 4. Como "vender" o progresso

No relatório para o cliente, foque no **Visibility Index**.
Se você tem 25 pontos na grade, o máximo de "pontos de vitória" é  (primeiro lugar em tudo). Se a soma dos ranks hoje é 100 e na semana passada era 200, a visibilidade dobrou. É um KPI visual e fácil de entender.