# Convenções de Código — ProfessorDash

## Padrões de Código

### Python

- **Formatter**: Black (padrão, 88 caracteres por linha)
- **Linter**: Ruff
- **PEP 8**: Obrigatório

```bash
black .
ruff check . --fix
```

### Views

- **Padrão**: Class-Based Views (CBV) em toda a aplicação
- Herdar de mixins apropriados (`ProfessorRequiredMixin`, `AlunoAutenticadoMixin`, etc.)
- Sempre usar `get_object_or_404` para acessar objetos por ID

```python
class TurmaDetailView(ProfessorRequiredMixin, DetailView):
    model = Turma
    template_name = 'turmas/detalhe.html'
    context_object_name = 'turma'
```

### Forms

- Usar Django Forms para toda validação (nunca validar só no JavaScript)
- Validação de arquivo via `clean_arquivo()` no form

```python
class MaterialForm(forms.ModelForm):
    def clean_arquivo(self):
        arquivo = self.cleaned_data.get('arquivo')
        if arquivo:
            validar_arquivo(arquivo, TIPOS_PERMITIDOS_MATERIAL)
        return arquivo
```

### Queries

- Sempre usar `select_related()` / `prefetch_related()` em listagens (N+1)
- Exemplo:

```python
turma.materiais.select_related('aula').order_by('ordem')
Entrega.objects.filter(atividade=atividade).select_related('aluno')
```

---

## Git

### Branches

| Padrão | Uso |
|---|---|
| `main` | Produção (stable) |
| `dev` | Desenvolvimento |
| `feature/<nome>` | Nova funcionalidade |
| `fix/<nome>` | Bug fix |

### Commits

Padrão: `<tipo>: <mensagem curta>`

| Tipo | Exemplo |
|---|---|
| `feat` | `feat: crud de materiais` |
| `fix` | `fix: validação de MIME type` |
| `refactor` | `refactor: extrair lógica de upload` |
| `docs` | `docs: atualizar README` |
| `chore` | `chore: atualizar requirements.txt` |
| `test` | `test: testes para Entrega model` |

Sempre fazer commit com mensagem clara. Não usar `git commit --amend` sem motivo.

---

## Testes

### Framework

- **pytest** + **pytest-django**
- Cobertura mínima: **60%** nas views críticas
- Estar em `tests/` ou `test_*.py` no mesmo diretório do código

### Estrutura

```python
# tests/test_atividades_views.py

import pytest
from django.test import Client
from atividades.models import Atividade

@pytest.mark.django_db
class TestAtividadeDetailView:
    def test_aluno_pode_ver_atividade_aberta(self, aluno_logado, atividade_aberta):
        client = Client()
        response = client.get(f'/turma/{atividade_aberta.turma.token_publico}/atividades/{atividade_aberta.id}/')
        assert response.status_code == 200
```

---

## Templates

### Padrão DTL (Django Template Language)

- Usar `{% load static %}` para assets
- Usar `{% url 'view-name' %}` para URLs (nunca hardcode)
- Componentes em `templates/components/_*.html`

### HTMX

- Sempre usar `hx-` para interatividade
- Views HTMX retornam fragmentos HTML (não HTML completo)

```html
<!-- View retorna um fragmento para ser inserido no DOM -->
<form hx-post="/painel/entregas/{{ entrega.id }}/avaliar/"
      hx-target="#entrega-{{ entrega.id }}"
      hx-swap="outerHTML">
  <input type="number" name="nota" min="0" max="10" step="0.1">
  <button type="submit">Salvar</button>
</form>
```

### Alpine.js

- Usar para estado local simples (sidebar collapse, abas, modais)
- Nunca para lógica de negócio (sempre no backend)

```javascript
// static/js/app.js
Alpine.store('sidebar', {
  collapsed: false,
  toggle() { this.collapsed = !this.collapsed }
})
```

---

## Estrutura de Pasta

```
apps/<app>/
├── models.py
├── views.py
├── urls.py
├── forms.py
├── admin.py
├── tests.py
└── templates/<app>/
    ├── lista.html
    ├── detalhe.html
    └── componentes/
        └── _card.html
```

---

## Markdown nos Modelos

- Campos markdown: use `MarkdownxField` (django-markdownx)
- Renderizar markdown no template: `{{ objeto.conteudo|safe }}`
- django-markdownx já renderiza HTML seguro automaticamente

```python
class Aula(BaseModel):
    conteudo = MarkdownxField(blank=True)
```

---

## Upload de Arquivos

- Sempre validar MIME type com `python-magic` (não extensão)
- Máximo: **50MB** por arquivo
- Pastas de upload:
  - Materiais: `materiais/%Y/%m/`
  - Entregas: `entregas/%Y/%m/`
  - Avatares: `avatares/`

---

## Ambiente Local vs Produção

| Variável | Local | Produção |
|---|---|---|
| `DEBUG` | `True` | `False` |
| `DATABASE_URL` | SQLite ou Postgres local | `postgresql://...@db:5432/...` |
| `ALLOWED_HOSTS` | `localhost,127.0.0.1` | `aulas.tonicoimbra.com` |
| `MEDIA_ROOT` | `./media` | `/app/media` (bind mount) |
| `REDIS_URL` | `redis://localhost:6379/0` | `redis://redis:6379/0` |

---

## Rodando Localmente

```bash
# Banco e Redis via Docker, Django local
docker compose -f docker-compose.dev.yml up -d db redis

# Migrations
python manage.py migrate

# Criar superuser
python manage.py createsuperuser

# Rodar servidor
python manage.py runserver

# Rodar testes
pytest
pytest --cov=apps --cov-report=html
```

---

## CI/CD

Não há GitHub Actions configurado no MVP. Deploy é manual via:
```bash
git push origin main
ssh vps "cd /srv/professordash && git pull && docker compose -f docker-compose.prod.yml up -d --build"
```

(Futuramente: GitHub Actions para testes automáticos e deploy automático)
