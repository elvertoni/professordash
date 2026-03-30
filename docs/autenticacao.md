# Autenticacao e Permissoes - ProfessorDash

## Visao Geral

O sistema separa autenticao por perfil:

- Professor entra com login local do Django.
- Aluno entra com Google OAuth via `django-allauth`.
- Parte do portal da turma e publica por `token`.
- Acesso a "minha area" e notas exige login e matricula ativa.

## Matriz De Acesso

| Area | Acesso | Regra |
| --- | --- | --- |
| `/entrar/login/` | Professor | `username` ou e-mail + senha |
| `/entrar/password_reset/` | Professor | recuperacao de senha do Django |
| `/painel/*` | Professor | `is_staff=True` |
| `/turma/<token>/` | Publico | token valido da turma ativa |
| `/turma/<token>/entrar/` | Aluno | redireciona para Google OAuth |
| `/turma/<token>/minha-area/` | Aluno autenticado | login + matricula ativa |
| `/turma/<token>/minhas-notas/` | Aluno autenticado | login + matricula ativa |

## Professor

O professor usa autenticacao local em [config/urls.py](/C:/CODE_TONI/professordash/config/urls.py) com as URLs do `django.contrib.auth.urls`.

Regras principais:

- O login principal e `LOGIN_URL = "/entrar/login/"`.
- O painel administrativo e protegido por `ProfessorRequiredMixin`.
- Esse mixin exige `request.user.is_authenticated` e `request.user.is_staff`.
- A tela de login do professor nao exibe o botao Google para evitar ambiguidade com o acesso do aluno.
- Em producao, a sessao usa cache/Redis e os cookies sao marcados como seguros.

Fluxo de recuperacao de senha:

1. O professor acessa `/entrar/password_reset/`.
2. O Django envia o email de redefinicao com os templates padrao ou customizados do projeto.
3. O retorno segue o fluxo padrao de `django.contrib.auth.urls`.
4. Em local, o backend de email e `console`; em producao, o envio usa SMTP.

## Aluno Via Google OAuth

Fluxo real:

```text
/turma/<token>/entrar/
    -> valida se o Google OAuth esta configurado
    -> salva `turma_token` na sessao
    -> redireciona para `google_oauth_start`
    -> allauth executa o login Google
    -> `user_logged_in` vincula ou cria `Aluno`
    -> redireciona para `/turma/<token>/minha-area/`
```

Pontos importantes:

- O OAuth e iniciado por `GoogleOAuthStartView`.
- A configuracao e considerada disponivel quando existem `GOOGLE_CLIENT_ID` e `GOOGLE_CLIENT_SECRET` reais, ou um `SocialApp` Google valido no banco.
- Se o OAuth nao estiver disponivel, o sistema volta para o portal da turma e exibe mensagem de erro.

## Vinculo Do Aluno

O vinculo acontece no signal `user_logged_in` em [alunos/signals.py](/C:/CODE_TONI/professordash/alunos/signals.py).

Comportamento:

- Se o usuario logado tem e-mail e nao e staff, o sistema procura um `Aluno` pelo mesmo e-mail.
- Se encontrar um aluno sem `user`, o vinculo e criado.
- Se nao encontrar, um novo `Aluno` e criado automaticamente com o usuario autenticado.

Observacao:

- O signal e disparado para qualquer login do usuario, nao apenas para Google OAuth.

## Acesso Do Aluno

Para acessar as areas do aluno, o `AlunoAutenticadoMixin` exige:

1. Usuario autenticado.
2. `Aluno` vinculado ao `User`.
3. `Matricula` ativa para a turma do token da URL.

Se a matricula nao existir ou estiver inativa, o sistema retorna `403`.

## Portal Publico

Qualquer pessoa com o token correto pode acessar o portal publico da turma ativa e ver:

- Informacoes da turma.
- Lista de aulas publicas.
- Materiais publicos.
- Lista publica de atividades.

Nao pode:

- Enviar entregas.
- Ver notas.
- Acessar itens restritos sem login Google valido.

## Implementacao

Referencias principais:

```python
class ProfessorRequiredMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not request.user.is_staff:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


class AlunoAutenticadoMixin(TurmaPublicaMixin, LoginRequiredMixin):
    def get_login_url(self):
        return reverse("turmas:entrar", kwargs={"token": self.turma.token_publico})
```

## Configuracao

Trechos relevantes de autenticacao:

- `AUTHENTICATION_BACKENDS` inclui `ModelBackend` e `allauth`.
- `SOCIALACCOUNT_ONLY = True`.
- `SOCIALACCOUNT_EMAIL_VERIFICATION = "none"`.
- `ACCOUNT_EMAIL_VERIFICATION = "none"`.
- `SOCIALACCOUNT_PROVIDERS["google"]["OAUTH_PKCE_ENABLED"] = True`.
- `LOGIN_REDIRECT_URL = "/painel/"`.
- `LOGOUT_REDIRECT_URL = "/"`.

Credenciais do Google OAuth ficam em:

- `GOOGLE_CLIENT_ID`
- `GOOGLE_CLIENT_SECRET`

Se esses valores estiverem ausentes ou ainda com placeholders, a interface esconde o botao de Google e o acesso ao fluxo de aluno e bloqueado.
