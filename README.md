# Ponte de Carreira

Você digita o cargo atual e o que sabe fazer. A ferramenta devolve três carreiras
vizinhas e viáveis, mostrando quanto do caminho você já andou, o que falta
aprender, quanto tempo leva e onde estudar de graça.

A palavra-chave é **ponte**, não salto: toda sugestão é alcançável em até 18 meses
estudando em paralelo ao trabalho atual.

---

## Rodar

```bash
pip install streamlit
streamlit run app.py
```

Abre em `http://localhost:8501`. Não precisa de chave de API nem de internet.

Para parar: `Ctrl + C` no terminal.

### Se der erro

| Erro | Solução |
|---|---|
| `pip não é reconhecido` | `python -m pip install streamlit` |
| `streamlit não é reconhecido` | `python -m streamlit run app.py` |
| `No such file or directory: 'app.py'` | o terminal não está na pasta do projeto; use `cd` |
| cores erradas | a pasta `.streamlit` precisa estar junto do `app.py` |

---

## Arquivos

| Arquivo | O que faz |
|---|---|
| `app.py` | Interface: CSS, seções da página e montagem dos cards |
| `bridge.py` | Prompt, schema JSON, chamada da API e cálculo do overlap |
| `recursos.py` | Catálogo de 20 cursos gratuitos reais |
| `demo_cache.json` | Três perfis pré-gerados |
| `.streamlit/config.toml` | Cores base do tema |
| `gerar_cache.py` | Regera o cache chamando a API (não usado na demo) |
| `design.md` | Especificação visual |
| `briefing.md` | Descrição do produto |
| `simulacao.html` | Protótipo em HTML puro, abre com duplo clique |

Não apague o `bridge.py`: o `app.py` importa o `pos_processar` dele em toda
execução. Sem ele a aplicação não abre.

---

## Como funciona

```
cargo + habilidades
        ↓
com chave de API: bridge.analisar()  →  Gemini com response_schema
sem chave:        escolher_mock()    →  perfil de demo_cache.json
        ↓
bridge.pos_processar()  →  calcula o % de overlap
                        →  troca ids por links reais do catálogo
        ↓
cards montados em HTML no app.py
```

A decisão entre um caminho e outro é automática: se `GOOGLE_API_KEY` existir no
ambiente, chama a API; se não, usa os perfis prontos. Nesse caso aparece a legenda
"Resultado de exemplo" acima dos cards.

### As três decisões que valem no pitch

**1. A IA não gera os links, ela escolhe.**
O modelo recebe uma lista fixa de 20 recursos gratuitos reais e só pode escolher
ids dessa lista. Se inventar um id, `buscar_recursos()` descarta. O problema
clássico de URL alucinada não existe aqui, porque o modelo nunca escreve uma URL.

**2. O percentual é calculado, não opinado.**
Perguntar "qual a porcentagem de aproveitamento?" para um LLM devolve chute. Em
vez disso pedimos as duas listas de habilidades e calculamos em Python:

```python
overlap = len(aproveitadas) / (len(aproveitadas) + len(faltantes))
```

Dá para contar os itens do card e conferir o número na tela.

**3. O prompt proíbe habilidade genérica.**
"Comunicação", "proatividade" e "trabalho em equipe" estão banidos no prompt. É
o que faz a resposta parecer saída de ChatGPT. O modelo é obrigado a citar coisas
verificáveis: "fechamento de caixa", "operação de sistema ERP". Junto com o campo
`primeiro_passo_semana`, é o que transforma sugestão em ação.

---

## Antes de apresentar

- [ ] Os números da seção "Os dados" (78%, 72%, 67%, 64%) vieram do protótipo do
      Figma e **não foram verificados**. Ou encontre a fonte real, ou remova a
      seção. Estatística com fonte inventada na tela é o que mais derruba
      credibilidade em arguição.
- [ ] O `demo_cache.json` foi escrito à mão, não é saída real do modelo. Se
      perguntarem, diga isso.
- [ ] Testar os três botões de exemplo com o Wi-Fi desligado
- [ ] Ensaiar a demo com cronômetro: ela deve caber em 90 segundos

---

## O que dizer sobre a integração

A integração com o Gemini está implementada — prompt estruturado, schema JSON e
catálogo de recursos, tudo no `bridge.py`. A aplicação roda em modo demonstração
com respostas pré-geradas para não depender do Wi-Fi do evento.

Isso é verdade e explica o modo demo como decisão de engenharia, não como
limitação.

---

## Próximos passos

- Ligar a API de verdade e rodar `gerar_cache.py` para os exemplos virarem saída
  real do modelo
- Campo de ressalva por carreira ("exige turno", "salário inicial menor"), para o
  resultado não soar como vendedor de curso
- Cruzar o tempo de transição com dados de vaga real em vez de estimativa
- Migrar para React: o `bridge.py` e o `recursos.py` continuam sendo o núcleo, só
  a camada de interface muda
