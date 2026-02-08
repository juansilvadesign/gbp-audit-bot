Para transformar um endereço em uma grade de coordenadas (o famoso **Geogrid**), precisamos de um pouco de geometria básica aplicada à cartografia.

O objetivo é criar uma matriz de pontos equidistantes a partir de um centro. Aqui está a lógica técnica e o código para o seu protótipo:

### 1. A Lógica Matemática

A Terra não é plana, mas para raios curtos (ex: 5km ou 10km), podemos usar uma aproximação linear. O grande desafio é que, enquanto a distância entre latitudes é constante, a distância entre longitudes encurta conforme nos aproximamos dos polos.

As fórmulas básicas de deslocamento (*offset*) são:

* **Latitude:**  metros.
* **Longitude:**  metros.

### 2. Protótipo em Python

Como você já trabalha com Python e FastAPI no **LP Audit Bot**, este script gera a lista de coordenadas que você enviaria para a API de busca (como a DataForSEO ou Scale SERP).

```python
import math

def generate_grid(lat, lng, radius_km, grid_size=5):
    """
    lat, lng: Centro do mapa
    radius_km: Distância total do centro até a borda
    grid_size: N de pontos (ex: 5 gera uma grade 5x5 = 25 pontos)
    """
    points = []
    
    # Distância entre cada ponto da grade em metros
    # Se o raio é 5km, o 'lado' total é 10km. 
    step_distance = (radius_km * 2000) / (grid_size - 1)
    
    # Ponto inicial (canto superior esquerdo)
    start_offset = (grid_size - 1) / 2
    
    for row in range(grid_size):
        for col in range(grid_size):
            # Calcula o deslocamento em metros em relação ao centro
            offset_lat = (start_offset - row) * step_distance
            offset_lng = (col - start_offset) * step_distance
            
            # Converte metros para graus decimais
            new_lat = lat + (offset_lat / 111111)
            new_lng = lng + (offset_lng / (111111 * math.cos(math.radians(lat))))
            
            points.append({
                "lat": round(new_lat, 6),
                "lng": round(new_lng, 6),
                "label": f"Ponto_{row}_{col}"
            })
            
    return points

# Exemplo: Grade 3x3 em Copacabana com raio de 2km
minha_grade = generate_grid(-22.9711, -43.1825, 2, 3)
print(minha_grade)

```

---

### 3. Estrutura do Relatório Semanal

Para a funcionalidade de "progresso do cliente", a estrutura de dados no seu banco (Supabase ou PostgreSQL) deve ser simples:

* **Tabela `Scans`:** Guarda o `checkpoint_id`, `data`, `keyword` e o `average_ranking`.
* **A Métrica de Ouro:** O que vende esse serviço é o **ARP (Average Rank Position)**. Se na semana 1 a média da grade era 12.5 e na semana 4 está em 3.2, você tem um gráfico de linha que prova o seu valor para o cliente.

### Próximos Passos

Para o MVP, a parte visual no Next.js pode ser feita com a biblioteca **`react-leaflet`**. Você plota círculos nos pontos da grade e define a cor via CSS baseado no ranking:

* `Rank 1-3`: Verde (Sucesso)
* `Rank 4-10`: Amarelo (Atenção)
* `Rank 10+`: Vermelho (Falha)