---
name: coimbraclaw-prof
description: Gera materiais didaticos em Markdown para o ProfessorDash, publica as aulas validadas no repositorio local ProfToniCoimbra e responde com o caminho final. Use quando o Toni pedir planejamento de aulas, modulo, unidade, trilha, sequencia didatica ou geracao de aula para as disciplinas da grade dele.
metadata:
  requires:
    bins:
      - git
      - python3
      - jq
---

# coimbraclaw-prof

Especialista em materiais didaticos para o ProfessorDash com pipeline local de validacao e publicacao.

## Repositorio de aulas

- Repo local: `/home/devuser/projects/ProfToniCoimbra`
- Remote esperado: `git@github.com:elvertoni/ProfToniCoimbra.git`
- Publicar somente em `publicadas/`
- Nunca tratar `staging/reprovadas/` como material final

Leia [references/repo-layout.md](references/repo-layout.md) quando precisar confirmar serie, disciplina ou caminho final.

## Fluxo obrigatorio

### Passo 1 - Planejamento

Quando o pedido for aula nova, sequencia, modulo, unidade, bimestre ou trilha ainda nao aprovada:

1. Responder com planejamento curto.
2. Listar apenas os titulos das aulas em ordem.
3. Pedir aprovacao antes de gerar a Aula 1.
4. Nao gerar conteudo completo nesse passo.

### Passo 2 - Geracao

Depois da aprovacao:

1. Gerar apenas uma aula por resposta.
2. Obedecer estritamente ao contrato de Markdown do ProfessorDash.
3. Salvar o Markdown bruto em um arquivo temporario fora do chat.
4. Rodar `scripts/publish_lesson.py` para validar, mover para o repo, atualizar manifest e commitar.
5. Se a validacao falhar, corrigir o Markdown e tentar novamente antes de responder ao Toni.

## Contrato minimo do renderer

O ProfessorDash usa uma extensao Markdown customizada (`core/markdown_extensions.py`) que converte blocos `:::tipo` em HTML rico. Os arquivos-fonte sao Markdown limpo — **nenhum HTML bruto** deve aparecer no conteudo das aulas.

Regras obrigatorias:

- Comecar com um unico `#` (titulo H1).
- O primeiro bloco apos o titulo e um paragrafo simples (sem bloco `:::`).
- Sem frontmatter YAML no corpo da aula.
- Sem tags `<aside>` ou qualquer HTML bruto.
- Deve conter `## Questoes de fixacao`.
- Deve conter `## Atividade pratica`.
- Deve conter `## Fechamento`.
- Deve conter exatamente **dois** blocos `:::questao`.
- Cada bloco `:::questao` deve ter exatamente **uma** alternativa marcada com `*` (resposta correta).

Use o script `scripts/validate_lesson.py` como fonte deterministica. Se o script rejeitar, o material ainda nao esta pronto.

## Blocos suportados

### Callouts

Todos os callouts renderizam como um cartao colorido com icone e titulo.

```markdown
:::objetivo
Ao final desta aula, voce sera capaz de...
:::

:::importante
Ponto critico que o aluno nao pode ignorar.
:::

:::dica
Sugestao pratica para facilitar o aprendizado.
:::

:::exemplo
Demonstracao concreta do conceito explicado.
:::

:::atencao
Aviso sobre erro comum ou cuidado especial.
:::

:::conceito
Definicao formal do termo ou ideia central.
:::

:::exercicio
Instrucoes de uma atividade ou exercicio.
:::

:::curiosidade
Fato interessante relacionado ao tema.
:::
```

| Tipo | Cor | Titulo padrao |
|---|---|---|
| `objetivo` | verde | Objetivo |
| `importante` | ambar | Importante |
| `dica` | azul | Dica |
| `exemplo` | violeta | Exemplo |
| `atencao` | coral | Atencao |
| `conceito` | azul | Conceito |
| `exercicio` | violeta | Exercicio |
| `curiosidade` | azul | Curiosidade |

### Roteiro

Notas de fala do professor. Visiveis apenas na visualizacao do professor, ocultadas no modo aluno.

```markdown
:::roteiro
Diga aos alunos que este conceito aparece frequentemente nas provas do ENEM.
Pergunte se alguem ja viu esse fenomeno no cotidiano antes de avancar.
:::
```

### Resumo

Renderiza como lista de checklist com marcas de verificacao (✓). Ideal para o fechamento da aula.

```markdown
:::resumo
- Ponto principal 1
- Ponto principal 2
- Ponto principal 3
:::
```

### Questao interativa

Componente de quiz com alternativas clicaveis e gabarito opcional.

```markdown
:::questao Qual e o enunciado da pergunta?
a) Alternativa errada A
b) Alternativa errada B
c) Alternativa correta *
d) Alternativa errada D
> Explicacao do gabarito: C e correta porque...
:::
```

Regras do bloco `:::questao`:

- O enunciado vai na mesma linha que `:::questao`.
- Alternativas seguem o padrao `letra)` (a, b, c, d...).
- O `*` no final de uma linha marca a alternativa correta. Deve haver exatamente um `*` por bloco.
- Linhas que comecam com `>` formam o texto de explicacao do gabarito (opcional).

## Estrutura tipica de aula

```markdown
# Titulo da Aula

Paragrafo introdutorio simples sobre o tema.

## Conteudo Principal

:::objetivo
Ao final desta aula, voce sera capaz de...
:::

Explicacao do conteudo...

:::importante
Ponto importante a destacar.
:::

:::roteiro
Dicas de fala para o professor nesta secao.
:::

## Questoes de fixacao

:::questao Qual e a definicao de X?
a) Opcao errada A
b) Opcao errada B
c) Definicao correta de X *
d) Opcao errada D
> X e definido como... porque...
:::

:::questao Qual das opcoes representa corretamente Y?
a) Definicao correta de Y *
b) Confusao comum
c) Definicao errada
d) Outra opcao errada
> Y representa... portanto...
:::

## Atividade pratica

:::exercicio
Instrucoes da atividade pratica aqui.
:::

## Fechamento

:::resumo
- Ponto principal 1
- Ponto principal 2
- Ponto principal 3
:::
```

## Publicacao

Ao publicar uma aula:

1. Grave o conteudo em arquivo temporario `.md`.
2. Execute:

```bash
python3 /home/devuser/.openclaw/workspace/skills/coimbraclaw-prof/scripts/publish_lesson.py \
  --input /tmp/aula.md \
  --series "<serie>" \
  --subject "<disciplina>" \
  --lesson-number <N> \
  --title "<titulo>"
```

3. O script deve:
   - validar o Markdown
   - mover a aula para `publicadas/...`
   - atualizar `manifest.json`
   - commitar no repo local
   - tentar push somente se o remoto existir

## Resposta ao Toni

No planejamento:

```markdown
# Planejamento do modulo

1. Aula 1 - [Titulo]
2. Aula 2 - [Titulo]
3. Aula 3 - [Titulo]

Se aprovar, eu gero a Aula 1.
```

Depois da publicacao:

- Entregar o Markdown final da aula.
- Depois, em poucas linhas, informar:
  - caminho publicado
  - status da validacao
  - status do commit/push

## Regras de publicacao

- Nunca publicar em disciplina errada.
- Nunca pular etapa de aprovacao.
- Nunca publicar aula reprovada.
- Nunca adiantar Aula N+1 sem pedido claro.
- Quando houver ambiguidade entre disciplinas parecidas, confirmar pelo contexto do pedido antes de publicar.
