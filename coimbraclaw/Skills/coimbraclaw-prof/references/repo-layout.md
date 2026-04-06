# Repo Layout - ProfToniCoimbra

Repo local: `/home/devuser/projects/ProfToniCoimbra`

## Caminhos validos

- `1a-serie / analise-e-metodos-para-sistemas`
- `1a-serie / introducao-a-computacao`
- `2a-serie / inovacao-tecnologia-e-empreendedorismo`
- `2a-serie / programacao-front-end`
- `3a-serie / programacao-no-desenvolvimento-de-sistemas`
- `3a-serie / analise-e-projeto-de-sistemas`
- `disciplinas-extras / inteligencia-artificial`

## Estrutura

```text
ProfToniCoimbra/
  manifest.json
  staging/
    pendentes/
    reprovadas/
  publicadas/
    materias/
      1a-serie/
      2a-serie/
      3a-serie/
      disciplinas-extras/
```

## Nome de arquivo

Padrao:

```text
aula-XX-titulo-slug.md
```

Exemplos:

- `aula-01-introducao-ao-html.md`
- `aula-03-casos-de-uso.md`

## Politica de publicacao

- Material final vai para `publicadas/`
- Falha de validacao vai para `staging/reprovadas/`
- O repo deve receber commit local em toda publicacao valida
- Push e opcional; depende do remoto existir no GitHub
