"""
Regera o demo_cache.json com respostas reais da API.

Rode isso perto da hora da apresentação:  python gerar_cache.py
Assim os perfis de exemplo são saída de verdade do modelo, não texto escrito à mão.
"""

import json
import os

from bridge import analisar

PERFIS = {
    "Caixa de banco": (
        "caixa de banco",
        "fechamento de caixa, atendimento presencial, conferência de documentos, "
        "sistema interno do banco, venda de consórcio",
    ),
    "Motorista de aplicativo": (
        "motorista de aplicativo",
        "rotas e trânsito urbano, atendimento ao passageiro, controle de gasto com "
        "combustível, manutenção preventiva do carro, apps de navegação",
    ),
    "Atendente de call center": (
        "atendente de call center",
        "atendimento telefônico, sistema de CRM, registro de chamados, negociação de "
        "dívida, script de retenção",
    ),
}

chave = os.environ["GOOGLE_API_KEY"]
saida = {}

for nome, (cargo, skills) in PERFIS.items():
    print(f"Gerando: {nome}")
    resultado = analisar(cargo, skills, chave)
    # Guarda só a saída crua; o overlap e os recursos são recalculados ao carregar.
    for c in resultado["carreiras"]:
        c.pop("overlap", None)
        c.pop("recursos", None)
    saida[nome] = resultado

with open("demo_cache.json", "w", encoding="utf-8") as f:
    json.dump(saida, f, ensure_ascii=False, indent=2)

print("demo_cache.json atualizado.")
