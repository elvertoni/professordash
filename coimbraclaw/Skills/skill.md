---
name: coimbraclaw-prof
description: Gerar materiais didáticos em Markdown compatíveis com o ProfessorDash, validar o contrato do renderer, publicar no repositório local ProfToniCoimbra e enviar para o GitHub. Use quando o Toni pedir planejamento de aulas, criação de aula, sequência didática, módulo, unidade, trilha, bimestre ou publicação de material didático para as disciplinas da grade.
updated: 2026-04-04
status: ativa
---

# coimbraclaw-prof

Skill de produção didática do COIMBRACLAW para o fluxo do **ProfessorDash**.

## Skill completa no vault

A versão integral da skill agora está disponível em:

- `COIMBRACLAW/Skills/coimbraclaw-prof/SKILL.md`
- `COIMBRACLAW/Skills/coimbraclaw-prof/scripts/publish_lesson.py`
- `COIMBRACLAW/Skills/coimbraclaw-prof/scripts/validate_lesson.py`
- `COIMBRACLAW/Skills/coimbraclaw-prof/references/repo-layout.md`
- `COIMBRACLAW/Skills/coimbraclaw-prof/_meta.json`

## Status atual

- **ativa**
- **validada em uso real**
- **atualizada no segundo cérebro em 2026-04-04**

## Para que serve

Usar esta skill quando o pedido envolver:

- planejamento de aulas
- geração de aula para o ProfessorDash
- sequência didática
- módulo, unidade, trilha ou bimestre
- publicação de aulas validadas no repositório didático

## Caminhos importantes

- Skill local: `/home/devuser/.openclaw/workspace/skills/coimbraclaw-prof/`
- Repo didático local: `/home/devuser/projects/ProfToniCoimbra`
- Remote esperado: `git@github.com:elvertoni/ProfToniCoimbra.git`
- Layout de referência da skill: `references/repo-layout.md`

## Fluxo correto

### 1. Planejamento

Quando o material ainda não foi aprovado:

1. responder com planejamento curto
2. listar apenas os títulos das aulas
3. pedir aprovação antes de gerar a Aula 1
4. não gerar conteúdo completo nessa etapa

### 2. Geração

Depois da aprovação:

1. gerar uma aula por vez
2. obedecer estritamente ao contrato do ProfessorDash
3. validar com `scripts/validate_lesson.py`
4. publicar com `scripts/publish_lesson.py`
5. atualizar `manifest.json`
6. commitar no repo local
7. tentar push se o remoto existir

## Contrato mínimo do ProfessorDash

- começar com um único `#`
- o primeiro bloco após o título deve ser um parágrafo simples
- não usar frontmatter YAML no arquivo final da aula
- não usar `aside`
- conter `## Questões de fixação`
- conter `## Atividade prática`
- conter `## Fechamento`
- conter exatamente 2 questões: `q1` e `q2`
- cada questão precisa ter exatamente uma alternativa com `data-correta="true"`

## Scripts principais

- `scripts/validate_lesson.py`
- `scripts/publish_lesson.py`

## Uso real já feito

Esta skill já foi usada no fluxo real de produção da disciplina **AMS — Análise e Métodos para Sistemas**:

- aulas **01–20** geradas e publicadas
- revisão transversal concluída depois do primeiro lote
- material enviado ao GitHub do repo didático

## Ajuste técnico importante

Durante o lote AMS 05–20, o validador precisou de correção no regex dos blocos de questão para evitar captura incorreta entre `q1` e `q2`. A correção foi aplicada e o lote completo passou na validação depois disso.

## Observação prática

Se esta nota ficar desatualizada, conferir primeiro a versão operacional em:

`/home/devuser/.openclaw/workspace/skills/coimbraclaw-prof/SKILL.md`
