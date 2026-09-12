"""
Catálogo curado de recursos gratuitos.

Por que isso existe: se o LLM gerar os links sozinho, ele inventa URLs que dão 404.
Aqui a IA só ESCOLHE um id desta lista. Se ela devolver um id que não existe, o
item é descartado silenciosamente (função buscar_recursos).

IMPORTANTE: confira cada link antes da demo. Sites mudam de URL.
"""

CATALOGO = {
    "ev_bradesco": {
        "titulo": "Fundação Bradesco — Escola Virtual",
        "url": "https://www.ev.org.br",
        "tipo": "Gratuito online",
        "areas": "Excel, informática básica, finanças, administração, atendimento",
    },
    "escola_virtual_gov": {
        "titulo": "Escola Virtual.Gov (ENAP)",
        "url": "https://www.escolavirtual.gov.br",
        "tipo": "Gratuito online",
        "areas": "gestão pública, dados, projetos, redação oficial, LGPD",
    },
    "sebrae_cursos": {
        "titulo": "Sebrae — Cursos online gratuitos",
        "url": "https://sebrae.com.br/sites/PortalSebrae/cursosonline",
        "tipo": "Gratuito online",
        "areas": "empreendedorismo, vendas, finanças, gestão de pequenos negócios",
    },
    "fgv_gratuitos": {
        "titulo": "FGV — Cursos online gratuitos",
        "url": "https://educacao-executiva.fgv.br/cursos/gratuitos-online",
        "tipo": "Gratuito online",
        "areas": "administração pública, direito, economia e finanças, educação e humanidades, "
        "estratégia e negócios, liderança e pessoas, marketing e vendas, relações internacionais, "
        "tecnologia e ciência de dados",
    },
    "dio": {
        "titulo": "DIO — Bootcamps gratuitos",
        "url": "https://www.dio.me",
        "tipo": "Bootcamp gratuito",
        "areas": "programação, dados, cloud, QA, front-end",
    },
    "curso_em_video": {
        "titulo": "Curso em Vídeo (Gustavo Guanabara)",
        "url": "https://www.cursoemvideo.com",
        "tipo": "Vídeo gratuito",
        "areas": "lógica de programação, Python, HTML/CSS, JavaScript",
    },
    "freecodecamp": {
        "titulo": "freeCodeCamp",
        "url": "https://www.freecodecamp.org",
        "tipo": "Gratuito online",
        "areas": "desenvolvimento web, JavaScript, Python, análise de dados",
    },
    "odin_project": {
        "titulo": "The Odin Project",
        "url": "https://www.theodinproject.com",
        "tipo": "Gratuito online",
        "areas": "desenvolvimento web full-stack",
    },
    "sqlbolt": {
        "titulo": "SQLBolt — SQL interativo",
        "url": "https://sqlbolt.com",
        "tipo": "Prática interativa",
        "areas": "SQL, consulta a banco de dados",
    },
    "kaggle_learn": {
        "titulo": "Kaggle Learn",
        "url": "https://www.kaggle.com/learn",
        "tipo": "Prática interativa",
        "areas": "análise de dados, Python, pandas, machine learning",
    },
    "khan_academy": {
        "titulo": "Khan Academy",
        "url": "https://pt.khanacademy.org",
        "tipo": "Gratuito online",
        "areas": "matemática, estatística, lógica, finanças pessoais",
    },
    "microsoft_learn": {
        "titulo": "Microsoft Learn",
        "url": "https://learn.microsoft.com/pt-br/training/",
        "tipo": "Gratuito + certificação",
        "areas": "Excel, Power BI, Azure, Office, dados",
    },
    "google_atelie": {
        "titulo": "Google Ateliê Digital",
        "url": "https://learndigital.withgoogle.com/ateliedigital",
        "tipo": "Gratuito + certificado",
        "areas": "marketing digital, e-commerce, produtividade, carreira",
    },
    "google_skillshop": {
        "titulo": "Google Skillshop",
        "url": "https://skillshop.withgoogle.com",
        "tipo": "Certificação gratuita",
        "areas": "Google Ads, Analytics, mídia paga",
    },
    "hubspot_academy": {
        "titulo": "HubSpot Academy",
        "url": "https://academy.hubspot.com",
        "tipo": "Certificação gratuita",
        "areas": "vendas, CRM, inbound marketing, atendimento ao cliente",
    },
    "rock_university": {
        "titulo": "Rock Content University",
        "url": "https://rockcontent.com/br/universidade/",
        "tipo": "Gratuito online",
        "areas": "marketing de conteúdo, SEO, redação",
    },
    "canva_design_school": {
        "titulo": "Canva Design School",
        "url": "https://www.canva.com/designschool/",
        "tipo": "Gratuito online",
        "areas": "design gráfico, apresentações, social media",
    },
    "figma_learn": {
        "titulo": "Figma — Learn Design",
        "url": "https://www.figma.com/resources/learn-design/",
        "tipo": "Gratuito online",
        "areas": "UX/UI, prototipagem, design de produto",
    },
    "coursera": {
        "titulo": "Coursera (auditar grátis / bolsa integral)",
        "url": "https://www.coursera.org",
        "tipo": "Auditoria gratuita",
        "areas": "suporte de TI, dados, projetos, UX — certificados profissionais",
    },
    "senai_ead": {
        "titulo": "SENAI EAD — Cursos gratuitos",
        "url": "https://www.senaiead.com.br",
        "tipo": "Gratuito online",
        "areas": "indústria, manutenção, segurança do trabalho, automação, logística",
    },
}


def catalogo_para_prompt() -> str:
    """Vira o bloco de texto que entra no prompt: id | título | áreas."""
    return "\n".join(
        f"{rid} | {r['titulo']} | {r['areas']}" for rid, r in CATALOGO.items()
    )


def buscar_recursos(ids: list) -> list:
    """Converte os ids escolhidos pelo LLM em recursos reais. Ids inválidos caem fora."""
    return [{"id": i, **CATALOGO[i]} for i in ids if i in CATALOGO]