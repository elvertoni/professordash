# Autenticação e Permissões — ProfessorDash

## Níveis de Acesso

```
┌─────────────────────────────────────────────────────────┐
│                   aulas.tonicoimbra.com                 │
├─────────────────┬───────────────────────────────────────┤
│   /painel/*     │   /turma/<token>/                     │
│   Professor     │   Acesso público (sem login)          │
│   is_staff=True │   - Ver aulas                         │
│   Login próprio │   - Materiais públicos                │
│   (email+senha) ├───────────────────────────────────────┤
│                 │   /turma/<token>/minha-area/           │
│                 │   Aluno (Google Login)                 │
│                 │   - Enviar entregas                   │
│                 │   - Ver notas e feedback              │
└─────────────────┴───────────────────────────────────────┘
```

---

## Professor (Admin)

- Usuário Django com `is_staff=True`
- Login em `/entrar/` com email + senha (não Google)
- Sessão armazenada no Redis
- Acesso exclusivo a todas as views `/painel/`
- Mixin: `ProfessorRequiredMixin` (verifica `request.user.is_staff`)

---

## Aluno via Google OAuth

Fluxo completo:

```
Aluno acessa /turma/<token>/entrar/
    ↓
Redirect para Google OAuth (django-allauth)
    ↓
Callback: allauth cria/recupera User + SocialAccount
    ↓
Signal post_social_login:
    ├── Busca Aluno pelo email do Google
    ├── Se encontrado → vincula user ao Aluno
    └── Se não encontrado → cria Aluno automaticamente
    ↓
Redirect para /turma/<token>/minha-area/
```

Para acessar views de aluno autenticado, o `AlunoAutenticadoMixin` verifica:
1. Usuário está logado
2. Existe `Aluno` vinculado ao usuário
3. Existe `Matricula` ativa para o aluno na turma do token da URL

---

## Acesso Público (sem login)

Qualquer pessoa com o link `/turma/<token>/` pode:
- Ver informações da turma
- Listar aulas
- Ver conteúdo das aulas
- Acessar materiais marcados como `publico`

Não pode (requer Google Login):
- Enviar entregas
- Ver notas e feedback
- Acessar materiais marcados como `restrito`

---

## Mixins de Autenticação

```python
# apps/core/mixins.py

class ProfessorRequiredMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_staff:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

class TurmaPublicaMixin:
    """Resolve turma pelo token_publico na URL"""
    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.turma = get_object_or_404(Turma, token_publico=kwargs['token'], ativa=True)

class AlunoAutenticadoMixin(TurmaPublicaMixin, LoginRequiredMixin):
    """Garante que o aluno autenticado pertence à turma"""
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

---

## Configuração django-allauth

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

Credenciais do Google OAuth (`GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`) ficam no `.env`.
