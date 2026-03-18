# PRD — Gerador de Aulas com IA
**Módulo: ProfessorDash · Admin Only**
**Versão 2.0 — Março 2026**

---

## 1. Visão Geral

Módulo interno do ProfessorDash, acessível exclusivamente ao professor (admin), para transformar materiais brutos em aulas estruturadas seguindo o padrão pedagógico consolidado (ProfLobster), com suporte a múltiplos providers de IA via OpenRouter e geração em lote.

**Exemplos de uso:**
> "Utilize o material RCO da Aula 03 de Front-End para gerar a aula desta semana."

> "Utilize essa apostila de JavaScript para gerar 10 aulas da disciplina de Programação Front-End."

---

## 2. Dois Modos de Entrada

O gerador suporta dois modos distintos de entrada de material, que podem ser usados separadamente ou combinados na mesma sessão.

---

### Modo A — Material RCO (Padrão SEED-PR)

Material oficial do governo baixado do RCO (Registro de Classe Online), com estrutura padronizada e previsível:

```
AULA_XX/
├── AULA_XX_<DISCIPLINA>.pptx          ← slides principais
├── AULA_XX_ATIVIDADE_<DISCIPLINA>.docx ← questões da atividade oficial
└── AULA_XX_PRATICA_<DISCIPLINA>.docx   ← atividade prática
```

**Comportamento esperado:**
- O sistema reconhece automaticamente os 3 arquivos e seus papéis
- Extrai TODO o conteúdo dos slides (título, corpo, notas)
- Extrai as questões e alternativas exatamente como estão no DOCX
- Preserva a ordem pedagógica original do PPT
- Complementa com conteúdo gerado pela IA onde o material estiver raso
- Sinaliza na aula o que veio do material e o que foi inferido

**Regra crítica:** o arquivo `ATIVIDADE` sempre vira as questões de fixação. O arquivo `PRATICA` vira a atividade prática. Nunca inverter.

---

### Modo B — Material Livre

Qualquer fonte de informação fora do padrão RCO: livros, apostilas, PDFs, artigos, sites, texto colado diretamente.

**Comportamento esperado:**
- IA analisa o conteúdo e propõe a divisão em N aulas
- Professor revisa e aprova o planejamento antes de gerar
- IA cria do zero: contextualização, analogias, questões, atividade prática
- Referências geradas são verificáveis (não inventadas)

**Formatos suportados:** `.pdf`, `.pptx`, `.ppt`, `.docx`, `.doc`, `.txt`, `.md`, URL pública, texto colado

---

## 3. Fluxo Completo

```
┌──────────────────────────────────────────────────────────────────────┐
│                         MODO A — RCO                                 │
│                                                                      │
│  Upload 3 arquivos     Extração automática    Geração direta         │
│  PPT + ATIV + PRAT  →  sem planejamento    →  1 aula estruturada     │
│                        (estrutura já         (rascunho editável)     │
│                         conhecida)                                   │
└──────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────┐
│                       MODO B — LIVRE                                 │
│                                                                      │
│  Upload(s) ou texto    Análise + proposta     Aprovação humana       │
│  livres             →  de N aulas          →  professor revisa    →  │
│                        (planejamento)         ajusta títulos         │
│                              │                                       │
│                              ▼                                       │
│                        Geração em lote                               │
│                        (1 aula por vez,                              │
│                         progresso em                                 │
│                         tempo real)                                  │
└──────────────────────────────────────────────────────────────────────┘

Em ambos os modos:
Aulas salvas como rascunhos editáveis → associadas à disciplina/turma
```

---

## 4. Interface

### 4.1 Tela Principal `/painel/gerador/`

```
┌──────────────────────────────────────────────────────────────────────┐
│  🤖 Gerador de Aulas com IA                           [Admin Only]  │
├──────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  Modo de entrada                                                     │
│  ┌─────────────────────────┐  ┌─────────────────────────────────┐   │
│  │  📋 Material RCO        │  │  📚 Material Livre              │   │
│  │  PPT + Atividade +      │  │  PDF, apostila, livro,          │   │
│  │  Prática (SEED-PR)      │  │  site, texto colado             │   │
│  └─────────────────────────┘  └─────────────────────────────────┘   │
│           [selecionado]                                              │
│                                                                      │
│  ── Modo RCO ──────────────────────────────────────────────────────  │
│                                                                      │
│  ┌────────────────────────────────────────────────────────────┐     │
│  │  📎 PPT da aula (obrigatório)                              │     │
│  │  AULA_03_FRONT_END.pptx                          ✅        │     │
│  └────────────────────────────────────────────────────────────┘     │
│  ┌────────────────────────────────────────────────────────────┐     │
│  │  📎 Atividade (obrigatório)                                │     │
│  │  AULA_03_ATIVIDADE_FRONT_END.docx                ✅        │     │
│  └────────────────────────────────────────────────────────────┘     │
│  ┌────────────────────────────────────────────────────────────┐     │
│  │  📎 Prática (opcional)                                     │     │
│  │  Arraste aqui ou clique                                    │     │
│  └────────────────────────────────────────────────────────────┘     │
│                                                                      │
│  Configuração                                                        │
│  Disciplina/Turma:   [2º A — Programação Front-End        ▼]        │
│  Número da aula:     [  3  ]                                         │
│  Nível:              ● Técnico  ○ Superior  ○ EJA                   │
│  Provider:           ● Claude Sonnet  ○ Gemini 2.5  ○ GPT-4o       │
│                                                                      │
│  Instruções adicionais (opcional):                                   │
│  ┌────────────────────────────────────────────────────────────┐     │
│  │  Ex: "Adicione mais exemplos de código HTML."              │     │
│  └────────────────────────────────────────────────────────────┘     │
│                                                                      │
│                    [  🚀 Gerar Aula  ]                               │
└──────────────────────────────────────────────────────────────────────┘
```

```
┌──────────────────────────────────────────────────────────────────────┐
│  🤖 Gerador de Aulas com IA — Modo Livre                            │
├──────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  Materiais de entrada                                                │
│  ┌────────────────────────────────────────────────────────────┐     │
│  │  📎 Arraste arquivos ou clique para selecionar             │     │
│  │     PDF · PPTX · DOCX · TXT · MD · (máx 50MB total)       │     │
│  └────────────────────────────────────────────────────────────┘     │
│  [+ Adicionar URL]   [+ Colar texto diretamente]                    │
│                                                                      │
│  Configuração                                                        │
│  Disciplina/Turma:   [2º A — Programação Front-End        ▼]        │
│  Número de aulas:    [  10  ] ▲▼                                     │
│  Nível:              ● Técnico  ○ Superior  ○ EJA                   │
│  Foco:               ● Equilibrado  ○ Mais teórico  ○ Mais prático  │
│  Provider:           ● Claude Sonnet  ○ Gemini 2.5  ○ GPT-4o       │
│                                                                      │
│  Instruções adicionais (opcional):                                   │
│  ┌────────────────────────────────────────────────────────────┐     │
│  │  Ex: "Foque em exemplos práticos. Inclua exercícios de     │     │
│  │  código a cada aula."                                       │     │
│  └────────────────────────────────────────────────────────────┘     │
│                                                                      │
│                    [  🔍 Analisar Material  ]                        │
└──────────────────────────────────────────────────────────────────────┘
```

### 4.2 Tela de Planejamento (Modo Livre apenas)

```
┌──────────────────────────────────────────────────────────────────────┐
│  📋 Planejamento Proposto — Front-End (10 aulas)                    │
├──────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  📄 Material analisado: apostila_frontend.pdf (342 págs)            │
│  🧵 Tema central: Desenvolvimento Web com HTML, CSS e JavaScript    │
│  🔗 Fio condutor: Do básico ao projeto prático completo             │
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │  01  Introdução à Web e HTML Semântico              [✏️ editar]│  │
│  │  02  CSS: Seletores, Box Model e Flexbox            [✏️ editar]│  │
│  │  03  CSS Avançado: Grid e Responsividade            [✏️ editar]│  │
│  │  04  JavaScript: Fundamentos e Tipos de Dados       [✏️ editar]│  │
│  │  05  DOM: Seleção e Manipulação de Elementos        [✏️ editar]│  │
│  │  06  Eventos e Interatividade                       [✏️ editar]│  │
│  │  07  Formulários, Validação e localStorage          [✏️ editar]│  │
│  │  08  Fetch API e Consumo de APIs REST               [✏️ editar]│  │
│  │  09  Introdução ao React: Componentes e Props       [✏️ editar]│  │
│  │  10  Projeto Final: Landing Page Completa           [✏️ editar]│  │
│  └──────────────────────────────────────────────────────────────┘   │
│                                                                      │
│  ⚠️  Observações da IA:                                              │
│  • Material cobre bem aulas 1–7. Aulas 8–10 foram complementadas    │
│    com conteúdo inferido além do material original.                 │
│                                                                      │
│  [← Ajustar configuração]       [✅ Aprovar e Gerar Aulas]          │
└──────────────────────────────────────────────────────────────────────┘
```

### 4.3 Tela de Geração (tempo real)

```
┌──────────────────────────────────────────────────────────────────────┐
│  ⚡ Gerando aulas...  7 / 10                                        │
│  ██████████████████████████░░░░░░░░  70%                            │
│                                                                      │
│  ✅  Aula 01 — Introdução à Web e HTML Semântico                    │
│  ✅  Aula 02 — CSS: Seletores, Box Model e Flexbox                  │
│  ✅  Aula 03 — CSS Avançado: Grid e Responsividade                  │
│  ✅  Aula 04 — JavaScript: Fundamentos e Tipos de Dados             │
│  ✅  Aula 05 — DOM: Seleção e Manipulação de Elementos              │
│  ✅  Aula 06 — Eventos e Interatividade                             │
│  ⏳  Aula 07 — Formulários, Validação e localStorage  (gerando...)  │
│  ○   Aula 08                                                         │
│  ○   Aula 09                                                         │
│  ○   Aula 10                                                         │
│                                                                      │
│  Provider: Claude Sonnet · Tokens: ~18.400 · Custo est: ~$0.14     │
│                                                                      │
│  [⏸ Pausar]                                      [✅ Ver aulas]     │
└──────────────────────────────────────────────────────────────────────┘
```

---

## 5. Padrão de Aula Gerada (15 seções obrigatórias)

Toda aula gerada — independente do modo ou provider — segue este padrão:

| # | Seção | Descrição |
|---|---|---|
| 1 | **Cabeçalho** | Disciplina · Série · Curso |
| 2 | **Título** | Com emoji temático |
| 3 | **Introdução** | Contextualização — por que essa aula importa |
| 4 | **Competências** | O que o aluno aprende (bullet list) |
| 5 | **Recapitulação** | Ligação com aula anterior (quando aplicável) |
| 6 | **Reflexão** | "Para pensarmos juntos..." — pergunta motivadora |
| 7 | **Conceituação** | Conteúdo principal desenvolvido com profundidade |
| 8 | **Analogias** | Exemplos do cotidiano acessíveis ao nível técnico |
| 9 | **Detalhamento** | Exemplos técnicos, código, diagramas em Markdown |
| 10 | **🎤 Roteiro de fala** | O que dizer nos primeiros 3–5 min de aula |
| 11 | **Atividade prática** | Objetivo + ferramentas + passo a passo numerado |
| 12 | **Questões** | 2–4 questões A/B/C/D com gabarito comentado |
| 13 | **Tarefa para casa** | Reforço do conteúdo fora da aula |
| 14 | **Resumo** | "O que vimos hoje" — bullet list com ✔️ |
| 15 | **Referências** | Fontes reais e verificáveis (toggle recolhível) |

**Regras inegociáveis:**
- Nunca omitir o `🎤 Roteiro de fala do professor`
- Nunca omitir gabarito comentado nas questões
- Conteúdo desenvolvido com profundidade — nunca resumir
- Analogias acessíveis para o nível técnico da turma
- Sinalizar o que veio do material vs. o que foi inferido

---

## 6. Arquitetura Técnica

### 6.1 Estrutura de arquivos

```
apps/gerador/
├── models.py
├── views.py
├── urls.py
├── extractors/
│   ├── __init__.py
│   ├── pdf.py          # pdfplumber
│   ├── pptx.py         # python-pptx
│   ├── docx.py         # python-docx
│   ├── url.py          # newspaper3k / BeautifulSoup
│   └── rco.py          # detector e montador do padrão RCO
├── providers.py        # OpenRouter — multi-model
├── prompts.py          # system prompt + templates por modo
├── pipeline.py         # orquestrador do fluxo completo
└── templates/gerador/
    ├── index.html
    ├── planejamento.html
    └── gerando.html
```

### 6.2 Models

```python
class SessaoGeracao(BaseModel):
    disciplina     = models.ForeignKey('turmas.Turma', on_delete=CASCADE)
    modo           = models.CharField(choices=[('rco','RCO'),('livre','Livre')])
    num_aulas      = models.IntegerField(default=1)
    nivel          = models.CharField(max_length=20)    # tecnico, superior, eja
    foco           = models.CharField(max_length=20)    # equilibrado, teorico, pratico
    provider       = models.CharField(max_length=30)    # claude, gemini, gpt4o
    instrucoes     = models.TextField(blank=True)
    planejamento   = models.JSONField(null=True)         # proposta da IA (Modo Livre)
    status         = models.CharField(max_length=20)    # rascunho|planejando|gerando|concluido
    tokens_usados  = models.IntegerField(default=0)
    custo_estimado = models.DecimalField(max_digits=8, decimal_places=4, default=0)

class MaterialEntrada(BaseModel):
    sessao             = models.ForeignKey(SessaoGeracao, on_delete=CASCADE)
    tipo               = models.CharField(max_length=20)  # pdf|pptx|docx|url|texto
    papel_rco          = models.CharField(max_length=20, blank=True)  # slides|atividade|pratica
    arquivo            = models.FileField(upload_to='gerador/inputs/', blank=True)
    url                = models.URLField(blank=True)
    texto_livre        = models.TextField(blank=True)
    conteudo_extraido  = models.TextField()
    ordem              = models.IntegerField(default=0)
```

### 6.3 Extratores

```python
# apps/gerador/extractors/rco.py

def detectar_papel_rco(filename: str) -> str:
    """Identifica o papel do arquivo no padrão RCO pelo nome."""
    nome = filename.upper()
    if 'ATIVIDADE' in nome:
        return 'atividade'
    if 'PRATICA' in nome or 'PRÁTICA' in nome:
        return 'pratica'
    if nome.endswith('.PPTX') or nome.endswith('.PPT'):
        return 'slides'
    return 'outro'

def extrair_rco(arquivos: dict) -> dict:
    """
    Recebe {'slides': file, 'atividade': file, 'pratica': file}
    Retorna conteúdo estruturado por papel.
    """
    return {
        'slides':    extrair_pptx(arquivos['slides']),
        'atividade': extrair_docx(arquivos.get('atividade')),
        'pratica':   extrair_docx(arquivos.get('pratica')),
    }
```

```python
# apps/gerador/extractors/pdf.py
import pdfplumber

def extrair_pdf(arquivo) -> str:
    texto = []
    with pdfplumber.open(arquivo) as pdf:
        for pagina in pdf.pages:
            t = pagina.extract_text()
            if t:
                texto.append(t.strip())
    return '\n\n'.join(texto)
```

```python
# apps/gerador/extractors/pptx.py
from pptx import Presentation

def extrair_pptx(arquivo) -> str:
    prs = Presentation(arquivo)
    slides = []
    for i, slide in enumerate(prs.slides, start=1):
        partes = [f"--- Slide {i} ---"]
        for shape in slide.shapes:
            if shape.has_text_frame:
                for para in shape.text_frame.paragraphs:
                    texto = para.text.strip()
                    if texto:
                        partes.append(texto)
        # Notas do slide
        if slide.has_notes_slide:
            nota = slide.notes_slide.notes_text_frame.text.strip()
            if nota:
                partes.append(f"[Nota: {nota}]")
        slides.append('\n'.join(partes))
    return '\n\n'.join(slides)
```

```python
# apps/gerador/extractors/docx.py
from docx import Document

def extrair_docx(arquivo) -> str:
    if not arquivo:
        return ''
    doc = Document(arquivo)
    return '\n'.join(
        p.text.strip() for p in doc.paragraphs if p.text.strip()
    )
```

### 6.4 Provider (OpenRouter)

```python
# apps/gerador/providers.py
from openai import OpenAI  # OpenRouter é compatível com SDK OpenAI

MODELOS = {
    'claude':  'anthropic/claude-sonnet-4-5',
    'gemini':  'google/gemini-2.5-pro',
    'gpt4o':   'openai/gpt-4o',
}

client = OpenAI(
    base_url='https://openrouter.ai/api/v1',
    api_key=settings.OPENROUTER_API_KEY,
)

def gerar_aula(system: str, user: str, provider: str = 'claude') -> tuple[str, int]:
    """Retorna (conteudo_markdown, tokens_usados)."""
    resposta = client.chat.completions.create(
        model=MODELOS[provider],
        messages=[
            {'role': 'system', 'content': system},
            {'role': 'user',   'content': user},
        ],
        max_tokens=4096,
    )
    conteudo = resposta.choices[0].message.content
    tokens   = resposta.usage.total_tokens
    return conteudo, tokens
```

### 6.5 System Prompt

```python
# apps/gerador/prompts.py

SYSTEM_PROMPT = """
Você é ProfLobster, especialista em pedagogia para cursos técnicos de TI.

Sua missão: transformar material bruto em aulas estruturadas de altíssima qualidade
para alunos do curso técnico em Desenvolvimento de Sistemas.

REGRAS INEGOCIÁVEIS:
- Nunca resumir — sempre desenvolver com profundidade real
- Nunca omitir o 🎤 Roteiro de fala do professor (3–5 min)
- Nunca omitir gabarito comentado em todas as questões
- Analogias acessíveis para alunos de curso técnico
- Sinalizar o que veio do material vs. o que foi inferido/complementado
- Referências devem ser reais e verificáveis — nunca inventar

ESTRUTURA OBRIGATÓRIA (15 seções):
1.  Cabeçalho — Disciplina · Série · Curso
2.  Título com emoji temático
3.  Introdução contextualizadora
4.  Competências e habilidades (bullet list)
5.  Recapitulação da aula anterior (quando aplicável)
6.  Reflexão / "Para pensarmos juntos..."
7.  Conceituação principal (desenvolvida, nunca resumida)
8.  Analogias e conexões com o cotidiano
9.  Detalhamento técnico (exemplos, código, diagramas em Markdown)
10. 🎤 Roteiro de fala do professor (3–5 min)
11. Atividade prática (objetivo + ferramentas + passo a passo numerado)
12. Questões de fixação A/B/C/D (mínimo 2, máximo 4) com gabarito comentado
13. Tarefa para casa
14. Resumo da aula (bullet list com ✔️)
15. Referências (fontes reais em formato ABNT simplificado)

Formato de saída: Markdown estruturado, pronto para renderizar no ProfessorDash.
"""

# ── Modo RCO ──────────────────────────────────────────────────────────

def prompt_rco(slides: str, atividade: str, pratica: str,
               disciplina: str, numero: int, nivel: str,
               instrucoes: str = '') -> str:
    return f"""
Gere a Aula {numero} da disciplina {disciplina} (nível: {nivel}).

MATERIAL DOS SLIDES (fonte principal — extraia TUDO):
{slides}

ATIVIDADE OFICIAL (use exatamente estas questões e alternativas na seção 12):
{atividade or 'Não fornecida — crie questões baseadas no conteúdo dos slides.'}

ATIVIDADE PRÁTICA (use como base para a seção 11):
{pratica or 'Não fornecida — crie uma atividade prática relacionada ao conteúdo.'}

INSTRUÇÕES ADICIONAIS:
{instrucoes or 'Nenhuma.'}

IMPORTANTE:
- Use o conteúdo dos slides como esqueleto — desenvolva cada tópico com profundidade
- As questões da seção 12 devem vir do arquivo ATIVIDADE, copiadas fielmente
- A atividade prática da seção 11 deve vir do arquivo PRÁTICA
- Gere a aula COMPLETA com as 15 seções obrigatórias
"""

# ── Modo Livre — Planejamento ─────────────────────────────────────────

def prompt_planejar(conteudo: str, num_aulas: int, disciplina: str,
                    nivel: str, foco: str, instrucoes: str = '') -> str:
    return f"""
Analise o material abaixo e proponha uma divisão em {num_aulas} aulas
para a disciplina de {disciplina} (nível: {nivel}, foco: {foco}).

MATERIAL:
{conteudo[:10000]}

Responda APENAS com um JSON no formato:
{{
  "tema_central": "...",
  "fio_condutor": "...",
  "observacoes": "...",
  "aulas": [
    {{"numero": 1, "titulo": "...", "topicos_principais": ["...", "..."]}},
    ...
  ]
}}

Regras:
- Progressão lógica do simples ao complexo
- Cada aula deve ter um foco claro e coeso
- Se o material não cobrir todas as aulas, sinalize em "observacoes"
- Títulos objetivos e descritivos
"""

# ── Modo Livre — Geração de cada aula ────────────────────────────────

def prompt_aula_livre(aula: dict, total: int, conteudo: str,
                      disciplina: str, nivel: str, foco: str,
                      aula_anterior: str = '', instrucoes: str = '') -> str:
    return f"""
Gere a Aula {aula['numero']} de {total} da disciplina {disciplina}.

TÍTULO: {aula['titulo']}
TÓPICOS: {', '.join(aula.get('topicos_principais', []))}
NÍVEL: {nivel}
FOCO: {foco}
AULA ANTERIOR: {aula_anterior or 'Esta é a primeira aula.'}

MATERIAL DE REFERÊNCIA:
{conteudo[:8000]}

INSTRUÇÕES ADICIONAIS:
{instrucoes or 'Nenhuma.'}

Gere a aula COMPLETA com as 15 seções obrigatórias.
Não resuma — desenvolva com profundidade real.
Crie questões e atividade prática originais baseadas no conteúdo.
"""
```

### 6.6 Pipeline de Geração

```python
# apps/gerador/pipeline.py

def executar_modo_rco(sessao: SessaoGeracao) -> Aula:
    """Modo A: gera 1 aula a partir dos 3 arquivos RCO."""
    materiais = sessao.materialentrada_set.all()
    conteudo  = {m.papel_rco: m.conteudo_extraido for m in materiais}

    user_prompt = prompt_rco(
        slides     = conteudo.get('slides', ''),
        atividade  = conteudo.get('atividade', ''),
        pratica    = conteudo.get('pratica', ''),
        disciplina = sessao.disciplina.nome,
        numero     = sessao.num_aulas,
        nivel      = sessao.nivel,
        instrucoes = sessao.instrucoes,
    )

    markdown, tokens = gerar_aula(SYSTEM_PROMPT, user_prompt, sessao.provider)

    sessao.tokens_usados = tokens
    sessao.status = 'concluido'
    sessao.save()

    return Aula.objects.create(
        turma    = sessao.disciplina,
        titulo   = extrair_titulo(markdown),
        numero   = sessao.num_aulas,
        conteudo = markdown,
        realizada = False,
    )


def executar_modo_livre(sessao: SessaoGeracao):
    """Modo B: gera N aulas em lote com SSE."""
    conteudo    = juntar_conteudo(sessao.materialentrada_set.all())
    planejamento = sessao.planejamento['aulas']
    total_tokens = 0
    titulo_anterior = ''

    for aula_info in planejamento:
        sessao.status = 'gerando'
        sessao.save()

        user_prompt = prompt_aula_livre(
            aula           = aula_info,
            total          = len(planejamento),
            conteudo       = conteudo,
            disciplina     = sessao.disciplina.nome,
            nivel          = sessao.nivel,
            foco           = sessao.foco,
            aula_anterior  = titulo_anterior,
            instrucoes     = sessao.instrucoes,
        )

        markdown, tokens = gerar_aula(SYSTEM_PROMPT, user_prompt, sessao.provider)
        total_tokens += tokens

        Aula.objects.create(
            turma     = sessao.disciplina,
            titulo    = aula_info['titulo'],
            numero    = aula_info['numero'],
            conteudo  = markdown,
            realizada = False,
        )

        titulo_anterior = aula_info['titulo']
        yield aula_info['numero']  # sinaliza progresso via SSE

    sessao.tokens_usados = total_tokens
    sessao.status = 'concluido'
    sessao.save()
```

### 6.7 View com SSE (progresso em tempo real)

```python
# apps/gerador/views.py

class GerarAulasView(ProfessorRequiredMixin, View):
    def get(self, request, sessao_id):
        sessao = get_object_or_404(SessaoGeracao, pk=sessao_id)

        def stream():
            if sessao.modo == 'rco':
                executar_modo_rco(sessao)
                yield f"data: {json.dumps({'aula': 1, 'total': 1, 'status': 'concluido'})}\n\n"
            else:
                total = len(sessao.planejamento['aulas'])
                for n in executar_modo_livre(sessao):
                    yield f"data: {json.dumps({'aula': n, 'total': total})}\n\n"
                yield f"data: {json.dumps({'status': 'concluido'})}\n\n"

        return StreamingHttpResponse(stream(), content_type='text/event-stream')
```

---

## 7. URLs

```
/painel/gerador/                        → tela principal
/painel/gerador/upload/                 → POST: upload e extração de arquivos
/painel/gerador/planejar/               → POST: análise e planejamento (Modo Livre)
/painel/gerador/<id>/aprovar/           → POST: aprovação do planejamento
/painel/gerador/<id>/gerar/             → GET: SSE de geração em tempo real
/painel/gerador/<id>/preview/<n>/       → preview da aula N gerada
/painel/gerador/<id>/salvar/            → POST: confirmar e publicar rascunhos
/painel/gerador/historico/              → sessões anteriores
```

---

## 8. Dependências Python

```txt
# requirements/base.txt (adicionar)
python-pptx==1.0.2
python-docx==1.1.2
pdfplumber==0.11.4
newspaper3k==0.2.8
beautifulsoup4==4.12.3
openai==1.51.0          # compatível com OpenRouter
```

```env
# .env
OPENROUTER_API_KEY=sk-or-...
```

---

## 9. Critérios de Aceite (MVP)

**Modo RCO:**
- [ ] Sistema reconhece automaticamente o papel de cada arquivo pelo nome
- [ ] Extrai todo o conteúdo dos slides, incluindo notas
- [ ] Questões da `ATIVIDADE` são usadas fielmente na seção 12
- [ ] Conteúdo da `PRATICA` é base da seção 11
- [ ] Aula gerada em menos de 60 segundos

**Modo Livre:**
- [ ] Upload aceita PDF, PPTX, DOCX, TXT, MD e URL
- [ ] Planejamento proposto é coerente com o material enviado
- [ ] Professor edita títulos antes de aprovar
- [ ] Progress bar atualiza em tempo real (SSE)
- [ ] Geração em lote funciona de 1 a 20 aulas sem erro

**Ambos:**
- [ ] Aulas salvas como rascunhos editáveis na disciplina
- [ ] Padrão de 15 seções obrigatórias respeitado em 100% das gerações
- [ ] Suporte a Claude, Gemini e GPT-4o via OpenRouter
- [ ] Estimativa de tokens/custo exibida ao final

---

## 10. Roadmap v2

| Feature | Descrição |
|---|---|
| Regenerar aula | Refazer só uma aula do lote |
| Ajuste pós-geração | "Adicione mais código na aula 3" |
| Import Google Drive | Selecionar pasta RCO direto do Drive |
| Quiz interativo | Questões viram atividade do ProfessorDash |
| Histórico de sessões | Reutilizar gerações anteriores |
| Templates por disciplina | Padrões específicos por matéria |

---

*Versão 2.0 — Março 2026*
