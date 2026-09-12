# 🌉 Ponte de Carreira

Você digita seu cargo atual e suas habilidades. A ferramenta devolve três carreiras
adjacentes viáveis, mostrando o que já se aproveita, o que falta aprender, quanto tempo
leva e onde estudar de graça.

## Rodar

```bash
pip install -r requirements.txt
export GOOGLE_API_KEY="sua-chave"     # no Windows: set GOOGLE_API_KEY=...
streamlit run app.py
```

Chave gratuita em https://aistudio.google.com/apikey

## Arquivos

| Arquivo | O que faz |
|---|---|
| `app.py` | Interface Streamlit: input, cards, botões de perfil de exemplo |
| `bridge.py` | Prompt, schema JSON, chamada do Gemini, cálculo do overlap |
| `recursos.py` | Catálogo curado de 20 recursos gratuitos reais |
| `demo_cache.json` | Três perfis pré-gerados (fallback se a internet cair) |
| `gerar_cache.py` | Regera o cache com respostas reais da API |

## Como funciona (para explicar no pitch)

```
input do usuário
      ↓
bridge.montar_prompt()  →  injeta o catálogo de recursos no prompt
      ↓
Gemini com response_schema  →  JSON garantido pela API, sem parsing frágil
      ↓
bridge.pos_processar()  →  calcula % de overlap em Python
                        →  troca ids por links reais do catálogo
      ↓
cards no Streamlit
```

### As três decisões que valem ser ditas na apresentação

**1. A IA não gera os links, ela escolhe.**
O modelo recebe uma lista fixa de 20 recursos gratuitos reais e só pode escolher ids
dessa lista. Se ele inventar um id, `buscar_recursos()` descarta. É por isso que nenhum
link da demo dá 404 — o problema clássico de alucinação de URL simplesmente não existe
aqui, porque o modelo nunca escreve uma URL.

**2. O % de overlap é calculado, não opinado.**
Se perguntássemos "qual a porcentagem de aproveitamento?", o número seria chute. Em vez
disso pedimos as duas listas de habilidades e calculamos em Python:

```python
overlap = len(aproveitadas) / (len(aproveitadas) + len(faltantes))
```

O número que aparece na tela é auditável: dá pra contar os itens do card e conferir.

**3. O prompt proíbe habilidade genérica.**
"Comunicação", "proatividade" e "trabalho em equipe" estão explicitamente banidos no
prompt. É o que faz a resposta parecer saída de ChatGPT. Em vez disso, o modelo é obrigado
a citar coisas verificáveis: "fechamento de caixa", "operação de sistema ERP".
Junto com o campo `primeiro_passo_semana` (uma ação concreta de 7 dias), é o que
transforma sugestão em ponte.

### Detalhe técnico que ajuda se alguém perguntar

A API do Gemini aceita um `response_schema` na configuração da chamada. Isso força a saída
a seguir a estrutura definida em `bridge.SCHEMA` — sem limpar crases de markdown, sem
regex, sem `try/except` em volta do `json.loads`. O JSON já chega válido e com todos os
campos obrigatórios preenchidos.

## Antes da demo

- [ ] Rodar `python gerar_cache.py` para o cache ter saída real do modelo
- [ ] Clicar em cada um dos 20 links de `recursos.py` e confirmar que abrem
- [ ] Testar os 3 botões de perfil de exemplo com o Wi-Fi desligado
- [ ] Ensaiar a demo duas vezes, cronometrando

## Extensões se sobrar tempo

- Campo opcional de região, para o tempo de transição considerar o mercado local
- Botão "exportar plano em PDF" com o primeiro passo de cada carreira
- Salvar o resultado para comparar duas profissões lado a lado
