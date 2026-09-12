"""
Interface Streamlit da Ponte de Carreira.

Roda com:  streamlit run app.py
Precisa da chave em .streamlit/secrets.toml ou na variável de ambiente GOOGLE_API_KEY.
"""

import json
import os
from pathlib import Path

import streamlit as st

from bridge import analisar, pos_processar

CACHE = Path(__file__).parent / "demo_cache.json"

st.set_page_config(page_title="Ponte de Carreira", page_icon="🌉", layout="centered")


def pegar_chave():
    chave = os.environ.get("GOOGLE_API_KEY")
    if chave:
        return chave
    try:
        return st.secrets["GOOGLE_API_KEY"]
    except Exception:
        return None


def carregar_cache():
    """
    Perfis pré-gerados. Salvam a demo se o Wi-Fi do evento cair.
    Passam pelo mesmo pos_processar da resposta real, então o cache guarda
    só a saída crua do modelo (sem overlap e sem recursos expandidos).
    """
    if not CACHE.exists():
        return {}
    bruto = json.loads(CACHE.read_text(encoding="utf-8"))
    return {nome: pos_processar(dados) for nome, dados in bruto.items()}


def cor_risco(nivel):
    return {"baixo": "🟢", "medio": "🟡", "alto": "🔴"}.get(nivel, "⚪")


def mostrar(resultado):
    risco = resultado["risco_automacao"]
    st.subheader(f"{cor_risco(risco['nivel'])} Risco de automação: {risco['nivel']}")
    st.caption(risco["justificativa"])

    st.divider()
    st.subheader("Três pontes possíveis")

    for carreira in resultado["carreiras"]:
        with st.container(border=True):
            st.markdown(f"### {carreira['titulo']}")
            st.write(carreira["por_que_faz_sentido"])

            st.progress(
                carreira["overlap"] / 100,
                text=f"{carreira['overlap']}% das habilidades você já tem",
            )

            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**Você já leva**")
                for s in carreira["skills_aproveitadas"]:
                    st.markdown(f"- {s}")
            with col2:
                st.markdown("**Falta aprender**")
                for s in carreira["skills_faltantes"]:
                    st.markdown(f"- {s}")

            st.markdown(f"**Tempo estimado:** {carreira['tempo_transicao_meses']} meses")
            st.info(f"**Comece esta semana:** {carreira['primeiro_passo_semana']}")

            st.markdown("**Onde estudar de graça**")
            for r in carreira["recursos"]:
                st.markdown(f"- [{r['titulo']}]({r['url']})")


st.title("🌉 Ponte de Carreira")
st.write(
    "Diga o que você faz hoje e o que sabe fazer. "
    "Devolvemos três carreiras vizinhas, o que já serve, o que falta e onde estudar de graça."
)

cache = carregar_cache()
if cache:
    st.caption("Ou veja um perfil de exemplo:")
    colunas = st.columns(len(cache))
    for coluna, nome in zip(colunas, cache):
        if coluna.button(nome, use_container_width=True):
            st.session_state["resultado"] = cache[nome]

cargo = st.text_input("Seu cargo atual", placeholder="Ex: caixa de banco")
skills = st.text_area(
    "Suas habilidades",
    placeholder="Ex: fechamento de caixa, atendimento presencial, sistema interno do banco, "
    "conferência de documentos, venda de consórcio",
    height=100,
)

if st.button("Encontrar minhas pontes", type="primary"):
    chave = pegar_chave()
    if not chave:
        st.error("Chave da API não encontrada. Defina GOOGLE_API_KEY antes de rodar.")
    elif not cargo.strip() or not skills.strip():
        st.warning("Preencha o cargo e pelo menos duas habilidades.")
    else:
        with st.spinner("Analisando seu perfil..."):
            try:
                st.session_state["resultado"] = analisar(cargo, skills, chave)
            except Exception as erro:
                st.error(f"A análise falhou: {erro}")

if "resultado" in st.session_state:
    st.divider()
    mostrar(st.session_state["resultado"])
