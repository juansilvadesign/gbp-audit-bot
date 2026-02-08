Para o seu frontend em Next.js renderizar o mapa com eficiência, o JSON precisa ser leve e já trazer as informações mastigadas, evitando que o cliente (browser) tenha que fazer cálculos pesados.



Aqui está uma sugestão de estrutura que integra bem com bibliotecas de mapa como Leaflet ou Google Maps React



\### Estrutura do JSON (Payload da API)



```json

{

&nbsp; project\_id locuz-001,

&nbsp; business\_name Minha Empresa de TI,

&nbsp; keyword consultoria de tecnologia rio de janeiro,

&nbsp; scan\_date 2026-01-31T120000Z,

&nbsp; summary {

&nbsp;   average\_rank 4.2,

&nbsp;   visibility\_score 72%,

&nbsp;   trend +5% 

&nbsp; },

&nbsp; grid\_data \[

&nbsp;   {

&nbsp;     id 1,

&nbsp;     lat -22.9711,

&nbsp;     lng -43.1825,

&nbsp;     rank 1,

&nbsp;     status success,

&nbsp;     color #22c55e

&nbsp;   },

&nbsp;   {

&nbsp;     id 2,

&nbsp;     lat -22.9720,

&nbsp;     lng -43.1830,

&nbsp;     rank 8,

&nbsp;     status warning,

&nbsp;     color #eab308

&nbsp;   },

&nbsp;   {

&nbsp;     id 3,

&nbsp;     lat -22.9730,

&nbsp;     lng -43.1840,

&nbsp;     rank 15,

&nbsp;     status danger,

&nbsp;     color #ef4444

&nbsp;   }

&nbsp; ],

&nbsp; history \[

&nbsp;   { date 2026-01-10, avg\_rank 12.5 },

&nbsp;   { date 2026-01-17, avg\_rank 8.1 },

&nbsp;   { date 2026-01-24, avg\_rank 4.2 }

&nbsp; ]

}



```



---



\### Por que essa estrutura é eficiente



&nbsp;`color` e `status` no Backend Ao definir a cor no Python (FastAPI), você centraliza a regra de negócio. Se amanhã você decidir que Amarelo é até o rank 7 e não 10, você muda em um só lugar e o frontend reflete automaticamente.

&nbsp;`summary` Dados prontos para os Cards de destaque no topo do dashboard.

&nbsp;`history` Um array simples para alimentar um gráfico de linha (como o Chart.js ou Recharts) que mostra o progresso semanal.



\### Dica de Design Engineer (Frontend)



No Next.js, para criar o efeito de bolinhas no mapa, você pode usar o componente `CircleMarker` do `react-leaflet`. Ele permite que o tamanho da bolinha seja fixo em pixels, independentemente do zoom, o que mantém a grade legível.



```tsx

&nbsp;Exemplo rápido no Next.js

CircleMarker 

&nbsp; center={\[point.lat, point.lng]} 

&nbsp; pathOptions={{ fillColor point.color, color 'white', weight 1, fillOpacity 0.8 }}

&nbsp; radius={15}



&nbsp; Tooltip permanent direction=center className=rank-label

&nbsp;   {point.rank}

&nbsp; Tooltip

CircleMarker



```

