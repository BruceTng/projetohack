"""
Núcleo da Ponte de Carreira.

Três responsabilidades:
1. Montar o prompt (com o catálogo de recursos embutido)
2. Chamar o Gemini exigindo JSON válido via response_schema
3. Pós-processar: calcular o % de overlap em Python e trocar ids por recursos reais
"""

import json

from recursos import buscar_recursos, catalogo_para_prompt

MODELO = "gemini-2.5-flash"

# O schema obriga o Gemini a devolver exatamente esta estrutura.
# Sem isso, você gastaria tempo limpando ```json e tratando campo faltando.
SCHEMA = {
    "type": "object",
    "properties": {
        "risco_automacao": {
            "type": "object",
            "properties": {
                "nivel": {"type": "string", "enum": ["baixo", "medio", "alto"]},
                "justificativa": {"type": "string"},
            },
            "required": ["nivel", "justificativa"],
        },
        "carreiras": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "titulo": {"type": "string"},
                    "por_que_faz_sentido": {"type": "string"},
                    "skills_aproveitadas": {"type": "array", "items": {"type": "string"}},
                    "skills_faltantes": {"type": "array", "items": {"type": "string"}},
                    "tempo_transicao_meses": {"type": "integer"},
                    "primeiro_passo_semana": {"type": "string"},
                    "recursos_ids": {"type": "array", "items": {"type": "string"}},
                },
                "required": [
                    "titulo",
                    "por_que_faz_sentido",
                    "skills_aproveitadas",
                    "skills_faltantes",
                    "tempo_transicao_meses",
                    "primeiro_passo_semana",
                    "recursos_ids",
                ],
            },
        },
    },
    "required": ["risco_automacao", "carreiras"],
}

PROMPT = """Você é um orientador de carreira brasileiro, prático e direto.

PERFIL
Cargo atual: {cargo}
Habilidades declaradas: {skills}

TAREFA
1. Avalie o risco de automação do cargo atual nos próximos 5 anos (baixo, medio ou alto)
   com uma justificativa de no máximo 2 linhas.
2. Sugira 3 carreiras adjacentes e realistas para essa pessoa no mercado brasileiro.

REGRAS OBRIGATÓRIAS
- Carreiras adjacentes: alcançáveis em até 18 meses de estudo em paralelo ao trabalho atual.
  Nada de "cientista de dados sênior" para quem é atendente.
- skills_aproveitadas: só habilidades que aparecem no perfil ou que decorrem
  claramente do cargo atual. Seja concreto.
- PROIBIDO listar habilidades genéricas como: comunicação, proatividade, trabalho em
  equipe, organização, resiliência, dinamismo. Elas não diferenciam ninguém.
  Use habilidades verificáveis: "fechamento de caixa", "negociação de prazo com cliente
  inadimplente", "operação de sistema ERP", "conferência de estoque".
- skills_faltantes: no máximo 4, cada uma sendo algo que dá pra estudar
  (uma ferramenta, uma técnica, um conceito). Não escreva "experiência na área".
- primeiro_passo_semana: UMA ação concreta para os próximos 7 dias, com duração
  estimada. Exemplo: "Fazer os 3 primeiros módulos de Excel na Fundação Bradesco (4h)".
- recursos_ids: escolha de 2 a 3 ids da lista abaixo. NÃO invente ids e NÃO invente
  links. Use apenas o que está na lista.

CATÁLOGO DE RECURSOS (formato: id | título | áreas)
{catalogo}

Escreva tudo em português do Brasil.
"""


def montar_prompt(cargo: str, skills: str) -> str:
    return PROMPT.format(cargo=cargo, skills=skills, catalogo=catalogo_para_prompt())


def pos_processar(dados: dict) -> dict:
    """
    O % de overlap é calculado aqui, não pedido ao LLM.
    Número vindo do modelo é chute; este é auditável.
    """
    for c in dados["carreiras"]:
        aproveitadas = len(c["skills_aproveitadas"])
        faltantes = len(c["skills_faltantes"])
        total = aproveitadas + faltantes
        c["overlap"] = round(100 * aproveitadas / total) if total else 0
        c["recursos"] = buscar_recursos(c["recursos_ids"])

    dados["carreiras"].sort(key=lambda c: c["overlap"], reverse=True)
    return dados


def analisar(cargo: str, skills: str, api_key: str) -> dict:
    # Import aqui dentro de propósito: assim o modo demonstração roda
    # sem o pacote google-genai instalado.
    from google import genai
    from google.genai import types

    client = genai.Client(api_key=api_key)
    resposta = client.models.generate_content(
        model=MODELO,
        contents=montar_prompt(cargo, skills),
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=SCHEMA,
            temperature=0.4,
        ),
    )
    return pos_processar(json.loads(resposta.text))