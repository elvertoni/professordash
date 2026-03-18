"""
System prompt e templates de user prompt para o Gerador de Aulas — ProfessorDash

Persona: ProfLobster — especialista em pedagogia para cursos técnicos de TI.
Padrão: 15 seções obrigatórias em Markdown, prontas para renderizar no ProfessorDash.
"""

# ── System Prompt ─────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """Você é ProfLobster, especialista em pedagogia para cursos técnicos de TI.

Sua missão: transformar material bruto em aulas estruturadas de altíssima qualidade
para alunos do curso técnico em Desenvolvimento de Sistemas (SEED-PR).

REGRAS INEGOCIÁVEIS:
- Nunca resumir — sempre desenvolver com profundidade real
- Nunca omitir o 🎤 Roteiro de fala do professor (3–5 min)
- Nunca omitir gabarito comentado em TODAS as questões
- Analogias acessíveis para alunos de curso técnico (não universitário)
- Sinalizar com [Material] o que veio do material original e com [IA] o que foi inferido
- Referências devem ser reais e verificáveis — nunca inventar títulos ou autores

ESTRUTURA OBRIGATÓRIA (15 seções — todas presentes, nesta ordem):

1.  **Cabeçalho** — Disciplina · Série · Curso (ex: Programação Web · 2º ano · Técnico em DS)
2.  **Título** — Título da aula com emoji temático
3.  **Introdução** — Contextualização: por que este conteúdo importa na vida do aluno
4.  **Competências** — O que o aluno aprende ao final (bullet list com verbos de ação)
5.  **Recapitulação** — Ligação com a aula anterior (pule apenas se for a primeira aula)
6.  **Reflexão** — "Para pensarmos juntos..." — pergunta motivadora aberta
7.  **Conceituação** — Conteúdo principal desenvolvido com profundidade (nunca resumir)
8.  **Analogias** — 2–3 exemplos do cotidiano acessíveis ao nível técnico
9.  **Detalhamento técnico** — Exemplos de código, diagramas em Markdown, casos de uso
10. **🎤 Roteiro de fala do professor** — O que dizer nos primeiros 3–5 min de aula
11. **Atividade prática** — Objetivo claro + ferramentas necessárias + passo a passo numerado
12. **Questões de fixação** — 2–4 questões A/B/C/D com gabarito comentado (OBRIGATÓRIO)
13. **Tarefa para casa** — Atividade de reforço fora da aula (específica e realizável)
14. **Resumo** — "O que vimos hoje" em bullet list com ✔️
15. **Referências** — Fontes reais em formato ABNT simplificado (toggle recolhível em HTML)

Formato de saída: Markdown estruturado, pronto para renderizar no ProfessorDash.
Use headers ## para seções principais e ### para subseções quando necessário.
"""


# ── Modo RCO (Modo A) ─────────────────────────────────────────────────────────

def prompt_rco(
    slides: str,
    atividade: str,
    pratica: str,
    disciplina: str,
    numero: int,
    nivel: str,
    instrucoes: str = "",
    aula_anterior: str = "",
) -> str:
    """
    Gera o user prompt para o Modo RCO (Material SEED-PR).

    O conteúdo dos slides é a fonte principal.
    As questões da ATIVIDADE vão fielmente para a seção 12.
    O conteúdo da PRÁTICA é a base da seção 11.

    Args:
        slides:      Conteúdo extraído do PPTX (obrigatório)
        atividade:   Conteúdo extraído do DOCX de atividade (seção 12)
        pratica:     Conteúdo extraído do DOCX de prática (seção 11)
        disciplina:  Nome da disciplina/turma
        numero:      Número da aula
        nivel:       'tecnico', 'superior' ou 'eja'
        instrucoes:  Instruções adicionais do professor (opcional)
        aula_anterior: Título da aula anterior para recapitulação (opcional)
    """
    nivel_label = {"tecnico": "Curso Técnico", "superior": "Ensino Superior", "eja": "EJA"}.get(
        nivel, nivel
    )

    return f"""Gere a Aula {numero} da disciplina "{disciplina}" ({nivel_label}).

═══════════════════════════════════════════════════════════════
MATERIAL DOS SLIDES — FONTE PRINCIPAL (extraia e desenvolva TUDO)
═══════════════════════════════════════════════════════════════
{slides}

═══════════════════════════════════════════════════════════════
ATIVIDADE OFICIAL — USE FIELMENTE NA SEÇÃO 12 (questões de fixação)
(copie as questões e alternativas exatamente como estão abaixo)
═══════════════════════════════════════════════════════════════
{atividade or "Não fornecida — crie 3 questões A/B/C/D baseadas no conteúdo dos slides."}

═══════════════════════════════════════════════════════════════
ATIVIDADE PRÁTICA — USE COMO BASE DA SEÇÃO 11
═══════════════════════════════════════════════════════════════
{pratica or "Não fornecida — crie uma atividade prática hands-on relacionada ao conteúdo."}

═══════════════════════════════════════════════════════════════
CONFIGURAÇÃO
═══════════════════════════════════════════════════════════════
Aula anterior: {aula_anterior or "Esta é a primeira aula da disciplina."}
Instruções adicionais: {instrucoes or "Nenhuma."}

ATENÇÃO:
- Use o conteúdo dos slides como esqueleto — desenvolva cada tópico com profundidade real
- As questões da seção 12 devem vir do arquivo ATIVIDADE, copiadas fielmente
- A atividade prática da seção 11 deve usar o arquivo PRÁTICA como base
- Gere a aula COMPLETA com as 15 seções obrigatórias, sem omitir nenhuma
"""


# ── Modo Livre — Planejamento (Modo B, passo 1) ───────────────────────────────

def prompt_planejar(
    conteudo: str,
    num_aulas: int,
    disciplina: str,
    nivel: str,
    foco: str,
    instrucoes: str = "",
    max_chars: int = 10000,
) -> str:
    """
    Gera o user prompt para análise e proposta de planejamento (Modo Livre).
    A resposta esperada é JSON puro com campos: tema_central, fio_condutor,
    observacoes, aulas[].

    Args:
        conteudo:   Texto extraído do(s) material(is) enviado(s)
        num_aulas:  Número de aulas desejadas
        disciplina: Nome da disciplina
        nivel:      'tecnico', 'superior' ou 'eja'
        foco:       'equilibrado', 'teorico' ou 'pratico'
        instrucoes: Instruções adicionais (opcional)
        max_chars:  Limite de caracteres do conteúdo enviado ao LLM
    """
    foco_label = {
        "equilibrado": "equilibrado (teoria e prática em partes iguais)",
        "teorico":     "mais teórico (conceitos aprofundados)",
        "pratico":     "mais prático (exercícios e projetos)",
    }.get(foco, foco)

    nivel_label = {
        "tecnico":  "Curso Técnico",
        "superior": "Ensino Superior",
        "eja":      "EJA",
    }.get(nivel, nivel)

    return f"""Analise o material abaixo e proponha uma divisão em {num_aulas} aulas
para a disciplina "{disciplina}" ({nivel_label}, foco: {foco_label}).

MATERIAL:
{conteudo[:max_chars]}

Responda APENAS com um JSON válido, sem texto antes ou depois, no formato:
{{
  "tema_central": "...",
  "fio_condutor": "...",
  "observacoes": "...",
  "aulas": [
    {{"numero": 1, "titulo": "...", "topicos_principais": ["...", "..."]}},
    {{"numero": 2, "titulo": "...", "topicos_principais": ["...", "..."]}},
    ...
  ]
}}

Regras:
- Progressão lógica do simples ao complexo
- Cada aula deve ter um foco claro e coeso (não misturar temas)
- Se o material não cobrir todas as {num_aulas} aulas, sinalize em "observacoes"
- Títulos objetivos e descritivos (ex: "CSS Grid: Layout de 12 colunas")
- Instruções adicionais: {instrucoes or "Nenhuma."}
"""


# ── Modo Livre — Geração individual (Modo B, passo 2) ────────────────────────

def prompt_aula_livre(
    aula: dict,
    total: int,
    conteudo: str,
    disciplina: str,
    nivel: str,
    foco: str,
    aula_anterior: str = "",
    instrucoes: str = "",
    max_chars: int = 8000,
) -> str:
    """
    Gera o user prompt para geração de uma aula individual no Modo Livre.
    Chamado em loop para cada aula do planejamento aprovado.

    Args:
        aula:           Dict com 'numero', 'titulo', 'topicos_principais'
        total:          Total de aulas no lote
        conteudo:       Texto extraído do material de referência
        disciplina:     Nome da disciplina
        nivel:          'tecnico', 'superior' ou 'eja'
        foco:           'equilibrado', 'teorico' ou 'pratico'
        aula_anterior:  Título da aula anterior para recapitulação
        instrucoes:     Instruções adicionais do professor
        max_chars:      Limite de caracteres do material de referência
    """
    topicos = aula.get("topicos_principais", [])
    topicos_str = "\n".join(f"  - {t}" for t in topicos) if topicos else "  (definido no título)"

    foco_label = {
        "equilibrado": "equilibrado",
        "teorico":     "mais teórico",
        "pratico":     "mais prático",
    }.get(foco, foco)

    nivel_label = {
        "tecnico":  "Curso Técnico",
        "superior": "Ensino Superior",
        "eja":      "EJA",
    }.get(nivel, nivel)

    return f"""Gere a Aula {aula["numero"]} de {total} da disciplina "{disciplina}".

TÍTULO DA AULA: {aula["titulo"]}

TÓPICOS A COBRIR:
{topicos_str}

CONFIGURAÇÃO:
- Nível: {nivel_label}
- Foco: {foco_label}
- Aula anterior: {aula_anterior or "Esta é a primeira aula."}

MATERIAL DE REFERÊNCIA (use como base — não copie literalmente):
{conteudo[:max_chars]}

INSTRUÇÕES ADICIONAIS: {instrucoes or "Nenhuma."}

Gere a aula COMPLETA com as 15 seções obrigatórias.
Não resuma — desenvolva o conteúdo com profundidade real.
Crie questões A/B/C/D originais com gabarito comentado.
Crie uma atividade prática hands-on específica para este tópico.
"""
