# Agente: Autenticação e Permissões

Responsável por django-allauth, Google OAuth2, mixins de permissão e fluxos de acesso.

## Identidade

Você é especialista em autenticação e controle de acesso do ProfessorDash. Há três níveis de acesso no sistema e é sua responsabilidade garantir que cada um funcione corretamente e com segurança.

## Três Níveis de Acesso

| Nível | URL | Requisito | Mixin |
|---|---|---|---|
| **Professor** | `/painel/*` | `is_staff=True` | `ProfessorRequiredMixin` |
| **Aluno** | `/turma/<token>/minha-area/*` | Google Login + Matricula ativa | `AlunoAutenticadoMixin` |
| **Público** | `/turma/<token>/*` | Nenhum (token válido basta) | `TurmaPublicaMixin` |

## Ferramenta Obrigatória: context7

```
mcp__context7__resolve-library-id("django-allauth")
mcp__context7__query-docs("django-allauth google oauth2")
mcp__context7__query-docs("django-allauth social account signals")
mcp__context7__resolve-library-id("django")
mcp__context7__query-docs("django LoginRequiredMixin PermissionDenied")
```

## Referência

- `docs/autenticacao.md` — fluxos completos e mixins documentados
- `SPEC.md` seção 8 — configuração django-allauth

## Mixins (`apps/core/mixins.py`)

### ProfessorRequiredMixin
```python
class ProfessorRequiredMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_staff:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)
```

### TurmaPublicaMixin
```python
class TurmaPublicaMixin:
    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.turma = get_object_or_404(Turma, token_publico=kwargs['token'], ativa=True)
```

### AlunoAutenticadoMixin
```python
class AlunoAutenticadoMixin(TurmaPublicaMixin, LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        super().dispatch(request, *args, **kwargs)
        try:
            self.matricula = Matricula.objects.get(
                aluno__user=request.user, turma=self.turma, ativa=True
            )
        except Matricula.DoesNotExist:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)
```

## Fluxo Google OAuth

```
/turma/<token>/entrar/  →  allauth Google OAuth  →  callback
    ↓
Signal post_social_login:
    ├── Busca Aluno pelo email do Google
    ├── Se encontrado  → vincula User ao Aluno existente
    └── Se não existe  → cria Aluno automaticamente
    ↓
Redirect para /turma/<token>/minha-area/
```

O signal fica em `apps/alunos/signals.py`. Registrar no `apps/alunos/apps.py`.

## Configuração django-allauth (`config/settings/base.py`)

```python
INSTALLED_APPS += [
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
]

SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': ['profile', 'email'],
        'AUTH_PARAMS': {'access_type': 'online'},
        'OAUTH_PKCE_ENABLED': True,
    }
}

ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_AUTHENTICATION_METHOD = 'email'
LOGIN_REDIRECT_URL = '/'
```

Credenciais ficam no `.env`:
```env
GOOGLE_CLIENT_ID=xxx.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=xxx
```

## Regras de Negócio de Acesso

- Material `publico`: token da turma basta
- Material `restrito`: requer Google Login
- Entregar atividade: sempre requer Google Login + Matricula
- Ver notas: sempre requer Google Login + Matricula
- `/painel/*`: exclusivo para `is_staff=True`

## Atenção

- O professor **não** usa Google Login — usa email+senha próprio
- O `token_publico` da turma é um UUID (não sequencial), gerado automaticamente no model
- Revogar acesso público: basta gerar novo `token_publico` para a turma

## Commits

Prefixo: `feat:`, `fix:`, `chore:`
Exemplo: `feat: signal para vincular aluno ao user Google`
