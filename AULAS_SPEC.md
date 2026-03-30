# AULAS_SPEC.md — Especificação de Alinhamento
## CoimbraBot × ToniAgent × ProfessorDash

> Este documento define o formato canônico de geração e exibição de aulas.
> Todos os geradores (Claude Desktop + ToniAgent) devem seguir este padrão.
> O ProfessorDash é a fonte de verdade de renderização.

---

## 1. Como o ProfessorDash renderiza aulas

O ProfessorDash usa `django-markdownx` para renderizar o campo `Aula.conteudo`.
O template `aula_detalhe.html` aplica CSS customizado que transforma elementos
Markdown em componentes visuais ricos.

### 1.1 Modo Leitura

Markdown renderizado com estilos aplicados via `.md-content`:
- `##` → heading com barra verde à esquerda
- `>` blockquote → citação estilizada
- `---` → separador horizontal
- Tabelas → tabelas estilizadas dark
- Code blocks → fundo escuro monoespaçado

### 1.2 Modo Apresentação

O JavaScript `buildSlides()` divide o conteúdo em slides usando `##` como separador.
Cada `##` = um slide. O conteúdo dentro de cada seção vira o corpo do slide.

### 1.3 Componentes Especiais

O ProfessorDash tem CSS dedicado para estes componentes:

| Componente | CSS class | Visual |
|---|---|---|
| Callout azul | `.c-blue` | Borda azul ciano |
| Callout verde | `.c-green` | Borda verde esmeralda |
| Callout âmbar | `.c-amber` | Borda amarela |
| Callout violeta | `.c-violet` | Borda violeta |
| Callout coral | `.c-coral` | Borda vermelha |
| Roteiro de fala | `.roteiro` | Bloco com gradiente violeta/azul |
| Questão | `.questao` | Card interativo com alternativas |
| Resumo | `.resumo-list` | Lista com checkmarks verdes |

---

## 2. Sintaxe Canônica — Formato de Aula

**TODOS os geradores devem usar este formato.**
O django-markdownx renderiza HTML seguro — use HTML inline para componentes especiais.

### 2.1 Estrutura Completa

```markdown
<!-- CABEÇALHO -->
> 📚 **[Disciplina]** • [Série] • Curso Técnico em Desenvolvimento de Sistemas

# 🎯 Aula [N] — [Título da Aula]

[Introdução de 3–5 linhas com **termos-chave em negrito**]

---

<!-- COMPETÊNCIAS -->
<div class="callout c-blue">
<div class="callout-icon">🧠</div>
<div class="callout-body">
<p class="callout-title">Competências e Habilidades</p>
<ul class="callout-text">
<li>Competência 1</li>
<li>Competência 2</li>
<li>Competência 3</li>
</ul>
</div>
</div>

> **Para pensarmos juntos:** [pergunta provocadora com exemplo real]

---

## [Emoji] [Título do Bloco 1]

<div class="callout c-green">
<div class="callout-icon">[Emoji]</div>
<div class="callout-body">
<p class="callout-title">[Termo central]</p>
<p class="callout-text">[Definição clara. Definição clássica: "[citação]"</p>
</div>
</div>

[Desenvolvimento do conteúdo em parágrafos]

---

## [Emoji] [Título do Bloco 2]

<div class="callout c-amber">
<div class="callout-icon">⚠️</div>
<div class="callout-body">
<p class="callout-title">[Conceito A] vs [Conceito B]</p>
<p class="callout-text">[Diferenciação importante]</p>
</div>
</div>

---

## [Emoji] [Título do Bloco 3 — Aplicação Prática]

[Parágrafo introdutório]

1. **Item 1** — descrição
2. **Item 2** — descrição
3. **Item 3** — descrição
4. **Item 4** — descrição
5. **Item 5** — descrição

---

<!-- ANALOGIA -->
<div class="callout c-violet">
<div class="callout-icon">💡</div>
<div class="callout-body">
<p class="callout-title">Analogia</p>
<p class="callout-text">[Analogia concreta e memorável, mínimo 3 linhas]</p>
</div>
</div>

---

<!-- ROTEIRO DE FALA -->
<div class="roteiro">
<div class="roteiro-header">🎤 Roteiro de fala do professor (3–5 min)</div>
<p class="roteiro-texto">"[Texto em primeira pessoa, tom conversacional, mínimo 6 linhas]"</p>
</div>

---

## ❓ Questão de Fixação

<div class="questao" data-idx="q1">
<p class="questao-num">Questão 1</p>
<p class="questao-enunciado">[Enunciado da questão]</p>
<ul class="alternativas">
<li class="alt" data-letra="A"><span class="alt-badge">A</span> [Alternativa A]</li>
<li class="alt" data-letra="B"><span class="alt-badge">B</span> [Alternativa B]</li>
<li class="alt" data-letra="C" data-correta="true"><span class="alt-badge">C</span> [Alternativa C — CORRETA]</li>
<li class="alt" data-letra="D"><span class="alt-badge">D</span> [Alternativa D]</li>
</ul>
<div class="gabarito" data-correta="C">
<span class="gab-texto">[Gabarito comentado com mínimo 2 linhas explicando por que C é correta]</span>
</div>
</div>

---

## 🎯 Atividade Prática — [Nome]

[Descrição da atividade executável em 10–15 minutos]

### Ferramentas sugeridas:
1. [Ferramenta 1] — [URL]
2. [Ferramenta 2] — [URL]
3. [Ferramenta 3] — [URL]

### Estrutura do entregável:
- Item 1
- Item 2
- Item 3

<div class="callout c-green">
<div class="callout-icon">📤</div>
<div class="callout-body">
<p class="callout-title">Entrega</p>
<p class="callout-text">[Formato de entrega]. Nome sugerido: <code>[NomeArquivo_Disciplina_NomeAluno]</code></p>
</div>
</div>

---

## 🎯 Questões da Atividade

<div class="questao" data-idx="q2">
<p class="questao-num">Questão 2</p>
<p class="questao-enunciado">[Questão de aplicação direta]</p>
<ul class="alternativas">
<li class="alt" data-letra="A"><span class="alt-badge">A</span> [Alternativa A]</li>
<li class="alt" data-letra="B" data-correta="true"><span class="alt-badge">B</span> [Alternativa B — CORRETA]</li>
<li class="alt" data-letra="C"><span class="alt-badge">C</span> [Alternativa C]</li>
<li class="alt" data-letra="D"><span class="alt-badge">D</span> [Alternativa D]</li>
</ul>
<div class="gabarito" data-correta="B">
<span class="gab-texto">[Gabarito comentado]</span>
</div>
</div>

<div class="questao" data-idx="q3">
<p class="questao-num">Questão 3</p>
<p class="questao-enunciado">Qual das alternativas NÃO é [conceito]?</p>
<ul class="alternativas">
<li class="alt" data-letra="A"><span class="alt-badge">A</span> [Alternativa A]</li>
<li class="alt" data-letra="B"><span class="alt-badge">B</span> [Alternativa B]</li>
<li class="alt" data-letra="C"><span class="alt-badge">C</span> [Alternativa C]</li>
<li class="alt" data-letra="D" data-correta="true"><span class="alt-badge">D</span> [Alternativa D — CORRETA]</li>
</ul>
<div class="gabarito" data-correta="D">
<span class="gab-texto">[Gabarito comentado]</span>
</div>
</div>

---

<!-- RESUMO -->
<div class="callout c-green">
<div class="callout-icon">📋</div>
<div class="callout-body">
<p class="callout-title">Resumo da Aula — O que vimos hoje</p>
<ul class="resumo-list">
<li><span class="resumo-check">✔️</span> [Conceito 1]</li>
<li><span class="resumo-check">✔️</span> [Conceito 2]</li>
<li><span class="resumo-check">✔️</span> [Aplicação/papel profissional]</li>
<li><span class="resumo-check">✔️</span> Na próxima aula: [título da próxima]</li>
</ul>
</div>
</div>

---

<button class="refs-toggle" onclick="this.nextElementSibling.classList.toggle('open')">
  📚 Referências
</button>
<div class="refs-content">

- AUTOR, Nome. **Título**. Edição. Cidade: Editora, Ano.
- AUTOR, Nome. **Título**. Edição. Cidade: Editora, Ano.
- AUTOR, Nome. **Título**. Edição. Cidade: Editora, Ano.

</div>
```

---

## 3. Mapeamento de Componentes CoimbraBot → ProfessorDash

| CoimbraBot (formato antigo) | ProfessorDash (formato canônico) |
|---|---|
| `<aside>🧠 **Competências**</aside>` | `<div class="callout c-blue">` |
| `<aside>💡 **Analogia:**</aside>` | `<div class="callout c-violet">` |
| `<aside>🎤 **Roteiro de fala**</aside>` | `<div class="roteiro">` |
| `<aside>❓ **Questão de Fixação**</aside>` | `<div class="questao" data-idx="qN">` |
| `<aside>🎯 **Atividade Prática**</aside>` | Seção `##` + callout c-green para entrega |
| `<aside>📋 **Resumo**</aside>` | `<div class="callout c-green">` + `.resumo-list` |
| `<aside>📤 **Entrega:**</aside>` | `<div class="callout c-green">` |

### Cores por contexto

| Contexto | Cor | CSS class |
|---|---|---|
| Definição principal | Azul ciano | `c-blue` |
| Competências, resumo, entrega | Verde | `c-green` |
| Atenção, diferenciação | Âmbar | `c-amber` |
| Analogia, roteiro | Violeta | `c-violet` |
| Erros comuns, cuidado | Coral | `c-coral` |

---

## 4. Modo Apresentação — Como os Slides São Gerados

O JavaScript `buildSlides()` divide o conteúdo em slides assim:

```
Cada ## heading = novo slide
Conteúdo até o próximo ## = corpo do slide
```

**Para slides bem formados:**
- Cada seção `##` deve ter conteúdo focado (1-2 conceitos)
- Evitar seções muito longas (mais de 5 parágrafos)
- Questões e callouts aparecem bem nos slides
- O título `##` vira o header do slide

**Seções que viram slides naturalmente:**
```
## 💻 O que é Engenharia de Software?     → Slide 1
## 🔬 Conceitos Fundamentais              → Slide 2
## 👨‍💻 O Papel do Analista                → Slide 3
## 🔄 Processos e Abordagens             → Slide 4
## ❓ Questão de Fixação                  → Slide 5
## 🎯 Atividade Prática                   → Slide 6
## 📋 Resumo                              → Slide 7
```

---

## 5. Instruções para os Geradores

### 5.1 Claude Desktop (este chat)

Ao gerar uma aula:
1. Usar o formato canônico da seção 2
2. Substituir TODOS os `<aside>` pelos componentes HTML do ProfessorDash
3. Garantir que cada `##` representa um slide coerente
4. Publicar direto no Banco de Aulas via Notion API

### 5.2 ToniAgent (VPS / Telegram)

Ao gerar uma aula via `/prof`:
1. Usar o mesmo formato canônico
2. Salvar `.md` em `~/projects/materiais/<disciplina>/aula-N-titulo.md`
3. Perguntar se publica no Notion
4. Perguntar se importa direto no ProfessorDash via API

### 5.3 Importação no ProfessorDash

O ProfessorDash já tem `AulaImportarMdView` em:
```
POST /turmas/<pk>/aulas/importar/
```

O ToniAgent pode chamar essa URL via `run_command` com curl:
```bash
curl -X POST https://aulas.tonicoimbra.com/turmas/<pk>/aulas/importar/ \
  -H "X-CSRFToken: <token>" \
  -b "sessionid=<session>" \
  -F "arquivo=@/path/to/aula.md"
```

---

## 6. Checklist de Qualidade por Aula

Antes de publicar, verificar:

- [ ] Cabeçalho com disciplina, série e curso
- [ ] Título H1 com emoji 🎯
- [ ] Introdução de 3–5 linhas com termos em negrito
- [ ] Callout c-blue para competências
- [ ] Pergunta provocadora em blockquote
- [ ] Mínimo 3 seções `##` de conteúdo
- [ ] Callout c-violet para analogia
- [ ] Bloco `.roteiro` para fala do professor (mínimo 6 linhas)
- [ ] Mínimo 1 questão interativa `.questao` com gabarito comentado
- [ ] Atividade prática com ferramentas e entregável
- [ ] Mínimo 2 questões da atividade com gabarito
- [ ] Callout c-green para resumo com `.resumo-list`
- [ ] Referências ABNT reais (mínimo 3)
- [ ] Cada seção `##` representa um slide coerente para apresentação

---

## 7. Arquivo de Configuração para o ToniAgent

Adicionar em `~/.toniagent/config/app.json`:

```json
{
  "professordash_url": "https://aulas.tonicoimbra.com",
  "professordash_api_key": "SEU_TOKEN_AQUI"
}
```

E adicionar no `skill.md` do professor a referência a este arquivo
como fonte de verdade do formato de aulas.
