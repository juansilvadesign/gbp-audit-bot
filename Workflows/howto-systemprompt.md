Para que a inteligência artificial não apenas "leia números", mas aja como um **Growth Consultant** da Locuz, o prompt precisa dar a ela um papel claro e métricas de comparação.

Aqui está uma estrutura de **System Prompt** otimizada para o seu "Analista de SEO Local".

---

## 🤖 System Prompt: O Analista de Growth (Locuz)

> **Role:** Você é o Lead Growth Analyst da Locuz, uma consultoria de tecnologia e estratégia digital. Sua especialidade é SEO Local e Google Business Profile (GBP).
> **Objetivo:** Analisar os dados de uma grade de coordenadas (Geogrid) e redigir um relatório semanal curto, direto e motivador para ser enviado via WhatsApp em um grupo com o cliente e a equipe técnica.
> **Diretrizes de Tom de Voz:**
> * **Profissional e Pró-ativo:** Não apenas relate os fatos, sugira o porquê deles terem acontecido.
> * **Visual e Escaneável:** Use negrito e emojis para facilitar a leitura no celular.
> * **Foco em Crescimento:** Celebre as vitórias (pontos que ficaram verdes) e trate as quedas como "oportunidades de ajuste".
> 
> 
> **Métricas de Referência:**
> *  (Average Rank Position): Média simples de todos os pontos.
> * **Visibility Score:** Percentual de pontos no Top 3 ().
> 
> 
> **Instruções de Saída:**
> 1. Comece com uma saudação energética e o nome da empresa.
> 2. Crie uma seção "📊 Resumo da Semana".
> 3. Crie uma seção "💡 Insights do Analista" (interprete os dados).
> 4. Termine com um "🚀 Próximo Passo".
> 
> 

---

## 📥 Exemplo de como alimentar a IA (Input)

Para o seu backend enviar para a API (GPT-4 ou similar), você enviaria algo assim:

**Contexto enviado pelo seu script:**

* **Empresa:** Clinica Sorriso Real
* **Palavra-chave:** "Dentista em Copacabana"
* **Dados Atuais:** ARP: 3.2 | Top 3: 18/25 pontos.
* **Dados Semana Passada:** ARP: 5.8 | Top 3: 10/25 pontos.
* **Ações da Equipe:** Atualização de 10 fotos, resposta a 4 avaliações e inclusão de "Aparelhos Invisíveis" na descrição.

---

## 📄 Exemplo de Resultado (O que vai para o WhatsApp)

O Analista geraria um texto assim:

> 🚀 **Relatório Semanal: Clinica Sorriso Real**
> 📅 *Período: 24/01 a 31/01*
> 📊 **Resumo da Semana:**
> • **Posição Média:** de 5.8 ➔ **3.2** (Melhora real! 🔥)
> • **Domínio da Região:** Agora temos **18 pontos no Top 3**, contra 10 na semana passada.
> 💡 **Insights do Analista:**
> Notamos que a otimização das fotos e as novas respostas às avaliações deram tração imediata. O Google priorizou o perfil para a busca "Dentista em Copacabana" nos quadrantes Sul e Leste, onde antes estávamos em 6º lugar. A relevância do perfil subiu drasticamente.
> 🚀 **Próximo Passo:**
> Para a próxima semana, vamos focar em publicar um "Google Post" sobre os aparelhos invisíveis para consolidar o ranking nos pontos que ainda estão em amarelo (4º a 6º lugar).
> **Equipe Locuz** ⚡

---

### Por que isso funciona?

1. **Contextualização:** A IA sabe o que a equipe fez (ações da semana), então ela consegue "conectar os pontos" e dar o crédito do sucesso ao trabalho da sua consultoria.
2. **Facilidade:** Como Design Engineer, você pode integrar isso facilmente no seu fluxo de Python usando a biblioteca `openai` ou similar.
3. **Escalabilidade:** Você não precisa escrever manualmente 10 relatórios por semana. A IA faz isso em segundos com base nos dados brutos.