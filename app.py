"""
Interface Streamlit da Ponte de Carreira.

Roda com:  streamlit run app.py

Dois modos:
- Demonstração: usa os perfis de demo_cache.json, não precisa de chave nem de internet.
- Real: chama o Gemini. Precisa de GOOGLE_API_KEY no ambiente ou em .streamlit/secrets.toml.

O modo demonstração já vem marcado quando não há chave configurada.
"""

import html
import json
import os
import time
from pathlib import Path

import streamlit as st

from bridge import analisar, pos_processar

CACHE = Path(__file__).parent / "demo_cache.json"


def esc(t):
    """Escapa o texto antes de entrar no HTML dos cards."""
    return html.escape(str(t))

st.set_page_config(page_title="Ponte de Carreira", page_icon="🌉", layout="centered")

# Streamlit não deixa estilizar os componentes direto, então injetamos CSS e
# montamos os cards como HTML. É o mesmo visual da simulação que já validamos.
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Work+Sans:wght@400;500;600;700;800;900&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Source+Sans+3:wght@400;500;600&display=swap');
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&display=swap');

:root{
  --navy:#0D1B34; --ground:#F5F3EE; --surface:#FFFFFF;
  --ink:#0D1B34; --muted:#64748B; --borda:#E2DDD6;
  --accent:#D97706; --accent-dark:#B45309; --accent-light:#FEF3C7;
  --ok:#15803D; --ok-bg:#F0FDF4;
  --risco:#B91C1C; --risco-bg:#FEF2F2; --risco-borda:#FECACA;
  --display:'Work Sans',sans-serif; --body:'Source Sans 3',sans-serif; --mono:'DM Mono',monospace;
}

#MainMenu, footer, [data-testid="stToolbar"]{visibility:hidden}
[data-testid="stHeader"]{display:none}
[data-testid="stAppViewContainer"] > .main{padding-top:0}
.stApp{background:var(--ground)}
.block-container{padding-top:0 !important; padding-bottom:0 !important; max-width:1080px}
html, body{overflow-x:hidden}

/* Faz o bloco ocupar a largura toda da janela, saindo da coluna do Streamlit. */
.larga{width:100vw; margin-left:calc(50% - 50vw); position:relative}
.interno{max-width:1080px; margin:0 auto; padding:0 2.5rem}

/* ── Barra de topo ───────────────────────────────────────── */
.barra{background:var(--navy); border-bottom:1px solid rgba(255,255,255,.06)}
.barra .interno{display:flex; align-items:center; justify-content:space-between; padding-top:.9rem; padding-bottom:.9rem}
.marca-topo{display:flex; align-items:center; gap:.7rem; font-family:var(--display); font-weight:800; color:#fff; font-size:1.05rem}
.marca-topo .logo{
  width:30px; height:30px; border-radius:8px; display:flex; align-items:center; justify-content:center;
  background:linear-gradient(135deg,#D97706,#B45309); color:#fff; font-size:.95rem; font-weight:700;
}
.barra .links{display:flex; align-items:center; gap:1.6rem}
.barra .links a{color:rgba(255,255,255,.6); font-size:.9rem; text-decoration:none}
.barra .links a:hover{color:#fff}
.barra .links a.cta{
  background:linear-gradient(135deg,#D97706,#B45309); color:#fff; font-family:var(--display);
  font-weight:700; padding:.6rem 1.2rem; border-radius:10px; box-shadow:0 4px 16px rgba(217,119,6,.35);
}
html, body, [class*="css"]{font-family:var(--body); color:var(--ink)}

/* ── Cabeçalho ───────────────────────────────────────────── */
.hero{
  background:linear-gradient(160deg,#0D1B34 0%,#162340 50%,#1a2d50 100%);
  padding:4.5rem 0 4rem; margin-bottom:3.5rem; position:relative; overflow:hidden;
}
.hero::before{
  content:""; position:absolute; inset:0; opacity:.04; pointer-events:none;
  background-image:linear-gradient(rgba(255,255,255,.8) 1px,transparent 1px),
    linear-gradient(90deg,rgba(255,255,255,.8) 1px,transparent 1px);
  background-size:60px 60px;
}
.hero::after{
  content:""; position:absolute; top:-40%; right:-10%; width:320px; height:320px; border-radius:50%;
  background:radial-gradient(circle,#D97706,transparent 70%); opacity:.2; filter:blur(40px);
}
.hero .tag{
  display:inline-block; font-family:var(--mono); font-size:.7rem; letter-spacing:.12em;
  text-transform:uppercase; color:rgba(255,255,255,.5); border:1px solid rgba(255,255,255,.12);
  background:rgba(255,255,255,.05); border-radius:99px; padding:.3rem .75rem; margin-bottom:1.1rem;
}
.hero h1{
  font-family:var(--display); font-weight:900; font-size:clamp(2.4rem,5.5vw,4.2rem); line-height:1.02;
  letter-spacing:-.035em; color:#fff; margin:0 0 1.2rem; position:relative; max-width:16ch;
}
.hero h1 em{font-style:normal; color:#FBBF24}
.hero p{color:rgba(255,255,255,.65); font-size:1.15rem; line-height:1.6; max-width:46ch; margin:0; position:relative}

/* ── Formulário ──────────────────────────────────────────── */
[data-testid="stWidgetLabel"] p{
  font-family:var(--mono); font-size:.7rem; text-transform:uppercase;
  letter-spacing:.12em; font-weight:600; color:var(--muted);
}
.stTextInput input, .stTextArea textarea{
  background:#FAFAF8; border:1px solid var(--borda); border-radius:12px;
  font-family:var(--body); font-size:.95rem; padding:.8rem 1rem;
}
.stTextInput input:focus, .stTextArea textarea:focus{
  border-color:var(--accent); box-shadow:0 0 0 3px rgba(217,119,6,.1);
}
.stButton button{
  border-radius:99px; border:1px solid var(--borda); background:transparent;
  color:var(--muted); font-weight:500; font-size:.9rem; padding:.45rem 1.1rem;
}
.stButton button:hover{border-color:var(--accent); color:var(--accent-dark); background:var(--accent-light)}
.stButton button[kind="primary"], [data-testid="stBaseButton-primary"]{
  background:linear-gradient(135deg,#D97706,#B45309); color:#fff; border:none;
  font-family:var(--display); font-weight:700; font-size:1rem; padding:.85rem 1.8rem;
  border-radius:12px; box-shadow:0 4px 16px rgba(217,119,6,.3);
}

[data-testid="stVerticalBlockBorderWrapper"]:has(.stTextArea){
  background:var(--surface); border:1px solid var(--borda) !important; border-radius:16px;
  padding:1.6rem; box-shadow:0 4px 24px rgba(0,0,0,.06); margin-bottom:2rem;
}

/* ── Diagnóstico de risco ────────────────────────────────── */
.risco-card{
  background:linear-gradient(135deg,#FEF2F2,#FFF5F5); border:1.5px solid var(--risco-borda);
  border-radius:16px; padding:1.5rem; margin-bottom:1.6rem;
}
.risco-card.baixo{background:linear-gradient(135deg,#F0FDF4,#F7FEF9); border-color:#BBF7D0}
.risco-card .olho{
  font-family:var(--mono); font-size:.7rem; text-transform:uppercase; letter-spacing:.12em;
  font-weight:600; color:var(--risco); margin-bottom:.3rem;
}
.risco-card.baixo .olho{color:var(--ok)}
.risco-card h2{font-family:var(--display); font-weight:700; font-size:1.5rem; margin:0 0 .7rem; color:var(--navy)}
.risco-card .pilula{
  float:right; font-family:var(--mono); font-size:.72rem; font-weight:600; background:#FEE2E2;
  color:var(--risco); padding:.35rem .8rem; border-radius:99px;
}
.risco-card p{margin:0; font-size:.93rem; line-height:1.6; color:#7F1D1D}
.risco-card.baixo p{color:#14532D}

/* ── Cabeçalho da lista ──────────────────────────────────── */
.secao h2{font-family:var(--display); font-weight:700; font-size:1.5rem; margin:0 0 .25rem; color:var(--navy)}
.secao p{font-size:.9rem; color:var(--muted); margin:0 0 1.2rem}

/* ── Card de carreira ────────────────────────────────────── */
.ponte{
  background:var(--surface); border:1px solid var(--borda); border-radius:16px;
  overflow:hidden; margin-bottom:1.1rem; box-shadow:0 1px 4px rgba(0,0,0,.04);
}
.ponte .faixa{height:4px}
.ponte .corpo{padding:1.5rem}
.ponte .olho{
  font-family:var(--mono); font-size:.72rem; color:var(--muted); margin-bottom:.6rem;
}
.ponte h3{
  font-family:var(--display); font-weight:700; font-size:1.3rem; line-height:1.2;
  margin:0 0 .6rem; color:var(--navy);
}
.ponte .motivo{font-size:.92rem; line-height:1.6; color:var(--muted); margin:0 0 1.1rem}

.ponte .meses{
  float:right; width:64px; height:64px; border-radius:14px; margin:0 0 .6rem 1rem;
  display:flex; flex-direction:column; align-items:center; justify-content:center;
}
.ponte .meses .n{font-family:var(--display); font-weight:900; font-size:1.35rem; line-height:1}
.ponte .meses .u{font-family:var(--mono); font-size:.55rem; text-transform:uppercase; letter-spacing:.08em; margin-top:2px}

.match{display:flex; justify-content:space-between; align-items:center; margin-bottom:.5rem}
.match span{font-family:var(--mono); font-size:.72rem; color:var(--muted)}
.match b{font-family:var(--mono); font-size:.9rem}
.trilho{height:8px; border-radius:99px; background:var(--borda); overflow:hidden; margin-bottom:1.4rem}
.trilho div{height:100%; border-radius:99px}

.detalhes{border-top:1px solid var(--borda); background:#FAFAF8; padding:1.4rem 1.5rem}
.grade{display:grid; grid-template-columns:1fr 1fr; gap:1.5rem; margin-bottom:1.4rem}
.grade .olho{
  font-family:var(--mono); font-size:.7rem; text-transform:uppercase; letter-spacing:.12em;
  font-weight:600; margin-bottom:.7rem;
}
.grade .olho.tem{color:var(--ok)} .grade .olho.falta{color:var(--accent)}
.grade ul{list-style:none; margin:0; padding:0}
.grade li{position:relative; padding-left:1.5rem; margin-bottom:.5rem; font-size:.9rem; line-height:1.4}
.grade li::before{
  position:absolute; left:0; top:0; width:1.05rem; height:1.05rem; border-radius:50%;
  display:flex; align-items:center; justify-content:center; font-size:.6rem; font-weight:700;
}
.grade .tem-lista li::before{content:"✓"; background:var(--ok-bg); color:var(--ok)}
.grade .falta-lista li::before{content:"→"; background:var(--accent-light); color:var(--accent)}

.passo{background:var(--accent-light); border-radius:12px; padding:.9rem 1.1rem; margin-bottom:1.4rem}
.passo .olho{
  font-family:var(--mono); font-size:.7rem; text-transform:uppercase; letter-spacing:.12em;
  font-weight:600; color:var(--accent-dark); margin-bottom:.25rem;
}
.passo p{margin:0; font-size:.92rem; line-height:1.5; color:#78350F}

.recursos .olho{
  font-family:var(--mono); font-size:.7rem; text-transform:uppercase; letter-spacing:.12em;
  font-weight:600; margin-bottom:.7rem;
}
.recursos a{
  display:block; background:var(--surface); border:1px solid var(--borda); border-radius:12px;
  padding:.75rem 1rem; margin-bottom:.5rem; font-size:.9rem; font-weight:500;
  color:var(--ink); text-decoration:none;
}
.recursos a:hover{border-color:var(--accent); color:var(--accent-dark)}

.rodape-nota{
  font-family:var(--mono); font-size:.72rem; line-height:1.6; color:var(--muted);
  margin-top:1.2rem; padding-bottom:1rem;
}

@media (max-width:640px){
  .hero{padding:1.8rem 1.4rem} .hero h1{font-size:1.9rem}
  .grade{grid-template-columns:1fr; gap:1.1rem}
  .ponte .meses{width:54px; height:54px}
}

/* ── Como funciona ───────────────────────────────────────── */
.olho-secao{
  font-family:var(--mono); font-size:.7rem; text-transform:uppercase; letter-spacing:.12em;
  color:var(--accent); margin-bottom:.5rem;
}
.titulo-bloco{
  font-family:var(--display); font-weight:800; font-size:1.75rem; line-height:1.2;
  color:var(--navy); margin:0 0 1.4rem;
}
.passos{display:grid; grid-template-columns:repeat(3,1fr); gap:1rem; margin-bottom:2.6rem}
.passo-card{
  background:var(--surface); border:1px solid var(--borda); border-radius:14px; padding:1.3rem;
}
.passo-card .num{
  font-family:var(--mono); font-size:.72rem; color:var(--accent); margin-bottom:.6rem;
}
.passo-card h4{
  font-family:var(--display); font-weight:700; font-size:1rem; line-height:1.3;
  margin:0 0 .5rem; color:var(--navy);
}
.passo-card p{font-size:.87rem; line-height:1.55; color:var(--muted); margin:0}

/* ── Os dados ────────────────────────────────────────────── */
.dados{background:var(--navy); padding:4rem 0; margin-bottom:3.5rem}
.dados .grade-dados{display:grid; grid-template-columns:1fr 1fr; gap:3rem; align-items:start}
.dados .olho-secao{color:rgba(217,119,6,.85)}
.dados h2{
  font-family:var(--display); font-weight:800; font-size:1.75rem; line-height:1.2;
  color:#fff; margin:0 0 .9rem;
}
.dados .texto{color:rgba(255,255,255,.6); font-size:.95rem; line-height:1.6; margin:0 0 1.5rem; max-width:60ch}
.dados-linha{
  background:rgba(255,255,255,.05); border:1px solid rgba(255,255,255,.07);
  border-radius:12px; padding:1rem 1.1rem; margin-bottom:.6rem;
}
.dados-linha .cargo{font-size:.9rem; font-weight:600; color:#fff}
.dados-linha .fonte{font-family:var(--mono); font-size:.68rem; color:rgba(255,255,255,.3)}
.dados-linha .pct{
  float:right; font-family:var(--display); font-weight:800; font-size:1.4rem; color:#FBBF24;
}
.dados-linha .trilho-escuro{
  height:6px; border-radius:99px; background:rgba(255,255,255,.08); overflow:hidden; margin-top:.7rem;
}
.dados-linha .trilho-escuro div{
  height:100%; border-radius:99px; background:linear-gradient(90deg,#D97706,#FBBF24);
}

/* ── Card recolhível ─────────────────────────────────────── */
details.mais{border-top:1px solid var(--borda)}
details.mais summary{
  list-style:none; cursor:pointer; padding:.85rem 1.5rem; background:#FAFAF8;
  font-family:var(--display); font-weight:600; font-size:.88rem; color:var(--navy);
  display:flex; justify-content:space-between; align-items:center;
}
details.mais summary::-webkit-details-marker{display:none}
details.mais summary::after{
  content:"▾"; font-size:.7rem; width:1.4rem; height:1.4rem; border-radius:50%;
  display:flex; align-items:center; justify-content:center; background:rgba(0,0,0,.05);
  transition:transform .2s;
}
details.mais[open] summary::after{transform:rotate(180deg)}
details.mais summary:hover{background:#F3F1EC}

/* ── Etiqueta de tipo do curso ───────────────────────────── */
.recursos a{display:flex; justify-content:space-between; align-items:center; gap:.8rem}
.recursos .tipo{
  flex-shrink:0; font-family:var(--mono); font-size:.66rem; font-weight:500;
  padding:.25rem .6rem; border-radius:99px;
}

/* ── Rodapé ──────────────────────────────────────────────── */
.rodape{background:var(--navy); padding:2.5rem 0; margin-top:4rem}
.rodape .marca{font-family:var(--display); font-weight:800; font-size:1.05rem; color:#fff}
.rodape .sub{font-family:var(--mono); font-size:.7rem; color:rgba(255,255,255,.35); margin-top:.15rem}
.rodape .aviso{
  font-family:var(--mono); font-size:.68rem; color:rgba(255,255,255,.25);
  margin-top:1.2rem; padding-top:1rem; border-top:1px solid rgba(255,255,255,.06);
}

@media (max-width:640px){
  .passos{grid-template-columns:1fr}
  .interno{padding:0 1.2rem}
  .dados .grade-dados{grid-template-columns:1fr; gap:1.6rem}
  .barra .links a:not(.cta){display:none}
  .hero{padding:3rem 0 2.5rem}
  .titulo-bloco, .dados h2{font-size:1.4rem}
}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)


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


# Palavras que ligam o que o usuário digitou a um dos perfis do cache.
# É só para o modo demonstração: no modo real quem decide é o Gemini.
PALAVRAS = {
    "Caixa de banco": ["caixa", "banco", "bancári", "agência", "financeir", "tesourari"],
    "Motorista de aplicativo": ["motorista", "uber", "99", "entregador", "moto", "dirig", "frete"],
    "Atendente de call center": ["atendente", "call", "telemarketing", "sac", "suporte", "recepcion"],
}


def escolher_mock(cargo, cache):
    """
    Devolve o perfil do cache que casa com o cargo digitado, ou None.
    Devolver None é de propósito: mostrar o perfil errado sem avisar
    faria a ferramenta parecer que inventa resposta.
    """
    texto = cargo.lower()
    for nome, palavras in PALAVRAS.items():
        if nome in cache and any(p in texto for p in palavras):
            return cache[nome]
    return None


# Texto que cada botão de exemplo joga nos campos, igual ao usado em gerar_cache.py.
TEXTO_PERFIL = {
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
        "atendimento telefônico, sistema de CRM, registro de chamados, "
        "negociação de dívida, script de retenção",
    ),
}


# Cor de destaque por posição do card, como no design.
CORES = ["#0F766E", "#6D28D9", "#1D4ED8"]


def mostrar(resultado):
    risco = resultado["risco_automacao"]
    nivel = risco["nivel"]
    st.markdown(
        f'<div class="risco-card {nivel}">'
        f'<span class="pilula">risco {esc(nivel)}</span>'
        f'<div class="olho">Diagnóstico do cargo</div>'
        f'<h2>Automação nos próximos 5 anos</h2>'
        f"<p>{esc(risco['justificativa'])}</p></div>",
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="secao"><h2>Três caminhos a partir daqui</h2>'
        "<p>Cada um pode ser alcançado em até 18 meses estudando em paralelo "
        "ao trabalho atual.</p></div>",
        unsafe_allow_html=True,
    )

    for i, c in enumerate(resultado["carreiras"]):
        cor = CORES[i % len(CORES)]
        tem = "".join(f"<li>{esc(s)}</li>" for s in c["skills_aproveitadas"])
        falta = "".join(f"<li>{esc(s)}</li>" for s in c["skills_faltantes"])
        links = "".join(
            f'<a href="{esc(r["url"])}" target="_blank">'
            f'<span>{esc(r["titulo"])}</span>'
            f'<span class="tipo" style="background:{cor}18;color:{cor}">{esc(r.get("tipo", ""))}</span>'
            f"</a>"
            for r in c["recursos"]
        )
        st.markdown(
            f'<div class="ponte">'
            f'<div class="faixa" style="background:{cor}"></div>'
            f'<div class="corpo">'
            f'<div class="meses" style="background:{cor}12;border:1.5px solid {cor}33;color:{cor}">'
            f'<span class="n">{c["tempo_transicao_meses"]}</span><span class="u">meses</span></div>'
            f'<div class="olho">caminho {i + 1}</div>'
            f'<h3>{esc(c["titulo"])}</h3>'
            f'<p class="motivo">{esc(c["por_que_faz_sentido"])}</p>'
            f'<div class="match"><span>quanto você já tem</span>'
            f'<b style="color:{cor}">{c["overlap"]}%</b></div>'
            f'<div class="trilho"><div style="width:{c["overlap"]}%;background:{cor}"></div></div>'
            f"</div>"
            f'<details class="mais"><summary>Ver habilidades, o que aprender e onde estudar</summary>'
            f'<div class="detalhes">'
            f'<div class="grade">'
            f'<div><div class="olho tem">O que você já sabe</div>'
            f'<ul class="tem-lista">{tem}</ul></div>'
            f'<div><div class="olho falta">O que falta aprender</div>'
            f'<ul class="falta-lista">{falta}</ul></div></div>'
            f'<div class="passo"><div class="olho">Comece esta semana</div>'
            f'<p>{esc(c["primeiro_passo_semana"])}</p></div>'
            f'<div class="recursos"><div class="olho" style="color:{cor}">Onde estudar</div>'
            f"{links}</div></div></details></div>",
            unsafe_allow_html=True,
        )

    st.markdown(
        '<p class="rodape-nota">Os prazos são estimativas e dependem do tempo semanal '
        "dedicado ao estudo. Os cursos listados são gratuitos e verificados.</p>",
        unsafe_allow_html=True,
    )


# ── Seções de conteúdo do design ─────────────────────────────────────────────

PASSOS = [
    ("01", "Informe seu cargo e habilidades",
     "Sem formulário longo. Só o cargo atual e o que você sabe fazer, sem filtrar."),
    ("02", "Receba o diagnóstico",
     "A ferramenta avalia o risco de automação do seu cargo e identifica quais "
     "competências são transferíveis."),
    ("03", "Veja três caminhos próximos",
     "Cada sugestão mostra quanto do caminho você já andou, o que falta aprender, "
     "o tempo estimado e onde estudar de graça."),
]

# ATENÇÃO: estes números vieram do protótipo do Figma e NÃO foram verificados.
# Confira a fonte ou troque por dados reais antes de apresentar.
RISCO_CARGOS = [
    ("Caixas e operadores de caixa", 78, "fonte a verificar"),
    ("Operadores de telemarketing", 72, "fonte a verificar"),
    ("Motoristas de aplicativo", 67, "fonte a verificar"),
    ("Assistentes administrativos", 64, "fonte a verificar"),
]


def secao_como_funciona():
    cards = "".join(
        f'<div class="passo-card"><div class="num">{n}</div>'
        f"<h4>{esc(t)}</h4><p>{esc(d)}</p></div>"
        for n, t, d in PASSOS
    )
    st.markdown(
        '<div id="como-funciona"></div><div class="olho-secao">Como funciona</div>'
        '<h2 class="titulo-bloco">Uma ponte, não um salto</h2>'
        f'<div class="passos">{cards}</div>',
        unsafe_allow_html=True,
    )


def secao_dados():
    linhas = "".join(
        f'<div class="dados-linha"><span class="pct">{p}%</span>'
        f'<div class="cargo">{esc(c)}</div><div class="fonte">{esc(f)}</div>'
        f'<div class="trilho-escuro"><div style="width:{p}%"></div></div></div>'
        for c, p, f in RISCO_CARGOS
    )
    st.markdown(
        '<div id="os-dados"></div><div class="dados larga"><div class="interno">'
        '<div class="grade-dados"><div>'
        '<div class="olho-secao">O contexto</div>'
        "<h2>A automação já está acontecendo</h2>"
        '<p class="texto">A maioria não vai perder o emprego da noite para o dia. '
        "Mas vai ver a renda comprimir e a vaga sumir no próximo ciclo de contratação. "
        "Agir antes é mais fácil do que agir depois.</p></div>"
        f"<div>{linhas}</div></div></div></div>",
        unsafe_allow_html=True,
    )


def rodape():
    st.markdown(
        '<div class="rodape larga"><div class="interno">'
        '<div class="marca">Ponte de Carreira</div>'
        '<div class="sub">Ferramenta gratuita de recolocação profissional</div>'
        '<div class="aviso">Sem cadastro · Sem armazenamento de dados · '
        "Os prazos são estimativas e dependem do tempo semanal dedicado ao estudo.</div></div></div>",
        unsafe_allow_html=True,
    )


st.markdown(
    '<div class="barra larga"><div class="interno">'
    '<div class="marca-topo"><span class="logo">&#8594;</span>Ponte</div>'
    '<div class="links"><a href="#como-funciona">Como funciona</a>'
    '<a href="#os-dados">Os dados</a>'
    '<a class="cta" href="#ferramenta">Analisar meu perfil</a></div>'
    "</div></div>"
    '<div class="hero larga"><div class="interno">'
    '<div class="tag">Ferramenta gratuita &middot; Sem cadastro</div>'
    "<h1>Onde mais o que você sabe fazer <em>vale?</em></h1>"
    "<p>Informe seu cargo atual e o que você sabe fazer. Em segundos, você recebe três "
    "caminhos reais — com o que falta aprender, quanto tempo leva e onde estudar de graça.</p>"
    "</div></div>",
    unsafe_allow_html=True,
)

secao_como_funciona()
secao_dados()

st.markdown(
    '<div id="ferramenta"></div><div class="olho-secao">A ferramenta</div>'
    '<h2 class="titulo-bloco">Analise seu perfil agora</h2>',
    unsafe_allow_html=True,
)

cache = carregar_cache()

with st.container(border=True):
    modo_demo = st.checkbox(
        "Modo demonstração (dados de exemplo, sem chamar a API)",
        value=pegar_chave() is None,
    )

    if cache:
        st.caption("Carregar um exemplo")
        colunas = st.columns(len(cache))
        for coluna, nome in zip(colunas, cache):
            if coluna.button(nome, use_container_width=True):
                st.session_state["resultado"] = cache[nome]
                st.session_state["mockado"] = True
                # preenche os campos com o perfil escolhido
                if nome in TEXTO_PERFIL:
                    st.session_state["cargo"], st.session_state["skills"] = TEXTO_PERFIL[nome]

    cargo = st.text_input(
        "Cargo atual",
        placeholder="Ex: caixa de banco, motorista, atendente…",
        key="cargo",
    )
    skills = st.text_area(
        "O que você sabe fazer",
        placeholder="Liste sem filtro: atendimento, conferência de documentos, uso de sistemas, "
        "organização, comunicação com clientes…",
        height=100,
        key="skills",
    )

    enviar = st.button("Ver meus caminhos", type="primary", use_container_width=True)

if enviar:
    chave = pegar_chave()
    if not cargo.strip() or not skills.strip():
        st.warning("Preencha o cargo e pelo menos duas habilidades.")
    elif modo_demo:
        with st.spinner("Analisando seu perfil..."):
            time.sleep(1)  # só para a demo não parecer instantânea demais
            resultado = escolher_mock(cargo, cache)
        if resultado:
            st.session_state["resultado"] = resultado
            st.session_state["mockado"] = True
        else:
            # Limpa o resultado anterior: sem isso o card da busca passada
            # continua na tela embaixo do aviso, parecendo a resposta deste cargo.
            st.session_state.pop("resultado", None)
            st.warning(
                f"Não temos resultado pré-gerado para \"{cargo}\". "
                "Use um dos perfis de exemplo acima, ou desmarque o modo demonstração "
                "para analisar esse cargo de verdade."
            )
    elif not chave:
        st.error("Chave da API não encontrada. Defina GOOGLE_API_KEY ou marque o modo demonstração.")
    else:
        with st.spinner("Analisando seu perfil..."):
            try:
                st.session_state["resultado"] = analisar(cargo, skills, chave)
                st.session_state["mockado"] = False
            except Exception as erro:
                st.error(f"A análise falhou: {erro}")

if "resultado" in st.session_state:
    st.divider()
    if st.session_state.get("mockado"):
        st.caption("Resultado de exemplo — o modo demonstração está ligado.")
    mostrar(st.session_state["resultado"])

rodape()