# Agentes — ProfessorDash

Agentes especializados para produção de código. Use o agente certo para cada tarefa.

## Quando usar cada agente

| Agente | Use quando precisar de... |
|---|---|
| [backend.md](backend.md) | Models, views CBV, forms, URLs, lógica de negócio Django |
| [frontend.md](frontend.md) | Templates DTL, Tailwind, HTMX, Alpine.js, componentes |
| [auth.md](auth.md) | Google OAuth, permissões, mixins, fluxos de acesso |
| [devops.md](devops.md) | Docker, Caddy, deploy na VPS, backup, variáveis de ambiente |
| [qa.md](qa.md) | Testes pytest-django, cobertura, validação com Playwright |

## Contexto sempre necessário

Antes de qualquer tarefa, forneça:

```
@CLAUDE.md @TASKS.md @apps/<app-relevante>/models.py
```

Não jogue todos os arquivos — só o necessário para a tarefa atual.
