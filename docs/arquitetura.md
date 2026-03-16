# Arquitetura — ProfessorDash

## Stack

| Componente | Versão | Função |
|---|---|---|
| Python | 3.12 | Runtime |
| Django | 5.1.x | Framework principal |
| Gunicorn | 22.x | WSGI server |
| PostgreSQL | 16 | Banco de dados |
| Redis | 7 | Cache de sessão |
| HTMX | 2.x | Interatividade frontend (CDN) |
| Alpine.js | 3.x | Estado local frontend (CDN) |
| Tailwind CSS | 3.x | Estilização (CDN) |
| django-allauth | 65.x | Google OAuth2 |
| django-markdownx | 4.x | Campos Markdown com preview |
| WeasyPrint | 62.x | Exportação PDF do boletim |
| django-import-export | 4.x | Importação CSV de alunos |
| whitenoise | 6.x | Arquivos estáticos |
| Caddy | 2.x | Reverse proxy + HTTPS automático |
| Docker | 26.x | Containerização |

## Infraestrutura (Produção)

```
┌─────────────────────────────────────────────────────────────────┐
│                        Contabo VPS                              │
│                     Ubuntu 24.04 LTS                            │
│                                                                 │
│   ┌─────────┐    ┌──────────────────────────────────────────┐  │
│   │  Caddy  │───▶│         Docker Compose Stack             │  │
│   │ :80/443 │    │                                          │  │
│   └─────────┘    │  ┌────────────┐    ┌─────────────────┐  │  │
│                  │  │  Django    │    │   PostgreSQL 16  │  │  │
│   aulas.         │  │  Gunicorn  │◀──▶│   professordash  │  │  │
│   tonicoimbra    │  │  :8000     │    └─────────────────┘  │  │
│   .com           │  └─────┬──────┘                         │  │
│                  │        │           ┌─────────────────┐  │  │
│                  │        └──────────▶│   Redis 7        │  │  │
│                  │                    │   (cache/sessão) │  │  │
│                  │                    └─────────────────┘  │  │
│                  └──────────────────────────────────────────┘  │
│                                                                 │
│   /srv/professordash/media/   ← uploads (bind mount)           │
└─────────────────────────────────────────────────────────────────┘
```

## Fluxo de Request

```
Browser → Caddy (TLS termination) → Gunicorn → Django → PostgreSQL/Redis
                                             ↓
                                        Media files (Caddy serve direto)
```

Arquivos de mídia (`/media/*`) são servidos diretamente pelo Caddy, sem passar pelo Django.

## Apps Django

| App | Responsabilidade |
|---|---|
| `core` | BaseModel, mixins de autenticação, validators, templatetags |
| `turmas` | Turmas e matrículas |
| `aulas` | Plano de ensino |
| `materiais` | Materiais didáticos e uploads |
| `atividades` | Atividades e entregas dos alunos |
| `avaliacoes` | Notas e feedback |
| `alunos` | Cadastro e importação de alunos |

## Domínio

`aulas.tonicoimbra.com`
