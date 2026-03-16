# SPEC — ProfessorDash
**Especificação Técnica v1.0**
**Professor Toni Coimbra · SEED-PR**

---

## 1. Arquitetura Geral

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

**Fluxo de request:**
```
Browser → Caddy (TLS termination) → Gunicorn → Django → PostgreSQL/Redis
                                             ↓
                                        Media files (Caddy serve direto)
```

---

## 2. Stack Detalhada

| Componente | Versão | Pacote/Serviço |
|---|---|---|
| Python | 3.12 | runtime |
| Django | 5.1.x | framework principal |
| Gunicorn | 22.x | WSGI server |
| PostgreSQL | 16 | banco de dados |
| Redis | 7 | cache de sessão |
| HTMX | 2.x | interatividade frontend (CDN) |
| Alpine.js | 3.x | estado local frontend (CDN) |
| Tailwind CSS | 3.x | estilização (CDN play ou CLI) |
| django-allauth | 65.x | autenticação Google OAuth2 |
| django-markdownx | 4.x | campos Markdown com preview |
| python-magic | 0.4.x | validação de tipo de arquivo |
| Pillow | 10.x | processamento de imagens |
| WeasyPrint | 62.x | exportação PDF do boletim |
| django-import-export | 4.x | importação CSV de alunos |
| whitenoise | 6.x | servir arquivos estáticos |
| Caddy | 2.x | reverse proxy + HTTPS |
| Docker | 26.x | containerização |

---

## 3. Estrutura do Projeto

```
professordash/
├── config/                          # configurações Django
│   ├── settings/
│   │   ├── base.py
│   │   ├── production.py
│   │   └── local.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
│
├── apps/
│   ├── core/                        # base, mixins, utils
│   │   ├── models.py                # BaseModel (timestamps)
│   │   ├── mixins.py                # AdminRequiredMixin, etc.
│   │   ├── utils.py                 # geração de tokens, slugs
│   │   └── templatetags/
│   │       └── markdown_extras.py
│   │
│   ├── turmas/                      # gerenciamento de turmas
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   ├── forms.py
│   │   └── templates/turmas/
│   │
│   ├── aulas/                       # plano de ensino
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   ├── forms.py
│   │   └── templates/aulas/
│   │
│   ├── materiais/                   # materiais didáticos
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   ├── forms.py
│   │   ├── storage.py               # lógica de upload
│   │   └── templates/materiais/
│   │
│   ├── atividades/                  # atividades e entregas
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   ├── forms.py
│   │   └── templates/atividades/
│   │
│   ├── avaliacoes/                  # notas e feedback
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   ├── forms.py
│   │   └── templates/avaliacoes/
│   │
│   └── alunos/                      # gestão de alunos
│       ├── models.py
│       ├── views.py
│       ├── urls.py
│       ├── forms.py
│       ├── importers.py             # importação CSV
│       └── templates/alunos/
│
├── templates/
│   ├── base.html
│   ├── base_admin.html              # layout do professor
│   ├── base_aluno.html              # layout do aluno
│   ├── base_publico.html            # layout sem login
│   └── components/                  # fragmentos HTMX
│       ├── _card_turma.html
│       ├── _card_atividade.html
│       ├── _tabela_entregas.html
│       ├── _boletim_grid.html
│       └── _modal_confirm.html
│
├── static/
│   ├── css/
│   │   └── app.css                  # Tailwind custom + overrides
│   ├── js/
│   │   └── app.js                   # Alpine stores globais
│   └── img/
│
├── media/                           # bind mount → /srv/professordash/media
│   ├── materiais/
│   ├── entregas/
│   └── avatares/
│
├── requirements/
│   ├── base.txt
│   ├── production.txt
│   └── local.txt
│
├── docker/
│   ├── Dockerfile
│   ├── entrypoint.sh
│   └── caddy/
│       └── Caddyfile
│
├── docker-compose.yml
├── docker-compose.prod.yml
├── manage.py
└── .env.example
```

---

## 4. Modelos de Dados

### 4.1 core.BaseModel
```python
class BaseModel(models.Model):
    criado_em  = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
```

---

### 4.2 alunos.Aluno
```python
class Aluno(BaseModel):
    user      = models.OneToOneField(User, null=True, blank=True,
                                     on_delete=models.SET_NULL)
    nome      = models.CharField(max_length=200)
    email     = models.EmailField(unique=True)
    matricula = models.CharField(max_length=30, blank=True)
    avatar    = models.ImageField(upload_to='avatares/', blank=True)
    ativo     = models.BooleanField(default=True)

    def __str__(self): return self.nome
```

---

### 4.3 turmas.Turma
```python
class Turma(BaseModel):
    nome         = models.CharField(max_length=200)
    codigo       = models.CharField(max_length=20, unique=True)
    descricao    = models.TextField(blank=True)
    periodo      = models.CharField(max_length=20)       # "1º Semestre"
    ano_letivo   = models.IntegerField()
    token_publico = models.UUIDField(default=uuid.uuid4, unique=True)
    ativa        = models.BooleanField(default=True)
    alunos       = models.ManyToManyField('alunos.Aluno',
                       through='Matricula', related_name='turmas')

    @property
    def link_publico(self):
        return reverse('turmas:portal', kwargs={'token': self.token_publico})
```

### 4.4 turmas.Matricula
```python
class Matricula(BaseModel):
    aluno        = models.ForeignKey(Aluno, on_delete=models.CASCADE)
    turma        = models.ForeignKey(Turma, on_delete=models.CASCADE)
    data_entrada = models.DateField(auto_now_add=True)
    ativa        = models.BooleanField(default=True)

    class Meta:
        unique_together = ('aluno', 'turma')
```

---

### 4.5 aulas.Aula
```python
class Aula(BaseModel):
    turma    = models.ForeignKey(Turma, on_delete=models.CASCADE,
                                  related_name='aulas')
    titulo   = models.CharField(max_length=300)
    numero   = models.PositiveIntegerField()
    data     = models.DateField(null=True, blank=True)
    conteudo = MarkdownxField(blank=True)    # django-markdownx
    realizada = models.BooleanField(default=False)
    ordem    = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['ordem', 'numero']
        unique_together = ('turma', 'numero')
```

---

### 4.6 materiais.Material

```python
class TipoMaterial(models.TextChoices):
    PDF      = 'pdf',      'PDF / Slides'
    ZIP      = 'zip',      'Arquivo ZIP / Código'
    MARKDOWN = 'markdown', 'Conteúdo Markdown/HTML'
    LINK     = 'link',     'Link Externo'
    ARQUIVO  = 'arquivo',  'Outro Arquivo'

class VisibilidadeMaterial(models.TextChoices):
    PUBLICO   = 'publico',   'Público (link da turma)'
    RESTRITO  = 'restrito',  'Restrito (requer login Google)'

class Material(BaseModel):
    turma        = models.ForeignKey(Turma, on_delete=models.CASCADE,
                                      related_name='materiais')
    aula         = models.ForeignKey('aulas.Aula', null=True, blank=True,
                                      on_delete=models.SET_NULL,
                                      related_name='materiais')
    titulo       = models.CharField(max_length=300)
    descricao    = models.TextField(blank=True)
    tipo         = models.CharField(max_length=20, choices=TipoMaterial.choices)
    visibilidade = models.CharField(max_length=20,
                                     choices=VisibilidadeMaterial.choices,
                                     default=VisibilidadeMaterial.PUBLICO)
    # campos mutuamente exclusivos por tipo
    arquivo      = models.FileField(upload_to='materiais/%Y/%m/',
                                     null=True, blank=True)
    url_externa  = models.URLField(blank=True)
    conteudo_md  = MarkdownxField(blank=True)
    ordem        = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['ordem', 'criado_em']
```

---

### 4.7 atividades.Atividade

```python
class TipoEntrega(models.TextChoices):
    ARQUIVO = 'arquivo', 'Envio de Arquivo'
    TEXTO   = 'texto',   'Texto / Resposta'
    LINK    = 'link',    'Link (GitHub, Replit...)'

class Atividade(BaseModel):
    turma         = models.ForeignKey(Turma, on_delete=models.CASCADE,
                                       related_name='atividades')
    aula          = models.ForeignKey('aulas.Aula', null=True, blank=True,
                                       on_delete=models.SET_NULL)
    titulo        = models.CharField(max_length=300)
    descricao     = MarkdownxField()
    tipo_entrega  = models.CharField(max_length=20,
                                      choices=TipoEntrega.choices,
                                      default=TipoEntrega.ARQUIVO)
    prazo         = models.DateTimeField()
    valor_pontos  = models.DecimalField(max_digits=5, decimal_places=2,
                                         default=10.0)
    permitir_reenvio = models.BooleanField(default=True)
    publicada     = models.BooleanField(default=True)

    @property
    def esta_aberta(self):
        return self.publicada and timezone.now() <= self.prazo
```

---

### 4.8 atividades.Entrega

```python
class StatusEntrega(models.TextChoices):
    PENDENTE  = 'pendente',  'Pendente'
    ENTREGUE  = 'entregue',  'Entregue'
    ATRASADA  = 'atrasada',  'Entregue em Atraso'
    AVALIADA  = 'avaliada',  'Avaliada'

class Entrega(BaseModel):
    atividade    = models.ForeignKey(Atividade, on_delete=models.CASCADE,
                                      related_name='entregas')
    aluno        = models.ForeignKey('alunos.Aluno', on_delete=models.CASCADE,
                                      related_name='entregas')
    status       = models.CharField(max_length=20,
                                     choices=StatusEntrega.choices,
                                     default=StatusEntrega.ENTREGUE)
    arquivo      = models.FileField(upload_to='entregas/%Y/%m/',
                                     null=True, blank=True)
    texto        = models.TextField(blank=True)
    url          = models.URLField(blank=True)
    data_envio   = models.DateTimeField(auto_now_add=True)
    # avaliação
    nota         = models.DecimalField(max_digits=5, decimal_places=2,
                                        null=True, blank=True)
    feedback     = models.TextField(blank=True)
    data_avaliacao = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('atividade', 'aluno')  # uma entrega por aluno
```

---

## 5. URLs e Roteamento

```
/                               → redirect para /painel/ (se admin) ou /entrar/
/entrar/                        → login do professor
/sair/                          → logout

# Google OAuth (django-allauth)
/accounts/                      → allauth urls

# Área do Professor
/painel/                        → dashboard principal
/painel/turmas/                 → listar turmas
/painel/turmas/nova/            → criar turma
/painel/turmas/<id>/            → detalhe da turma
/painel/turmas/<id>/editar/     → editar turma
/painel/turmas/<id>/alunos/     → gerenciar alunos da turma
/painel/turmas/<id>/importar-alunos/  → import CSV

/painel/turmas/<id>/aulas/             → listar aulas
/painel/turmas/<id>/aulas/nova/        → criar aula
/painel/turmas/<id>/aulas/<id>/        → detalhe/editar aula
/painel/turmas/<id>/aulas/reordenar/   → HTMX drag-and-drop

/painel/turmas/<id>/materiais/         → listar materiais
/painel/turmas/<id>/materiais/novo/    → criar material
/painel/turmas/<id>/materiais/<id>/editar/

/painel/turmas/<id>/atividades/        → listar atividades
/painel/turmas/<id>/atividades/nova/   → criar atividade
/painel/turmas/<id>/atividades/<id>/   → detalhe + entregas
/painel/turmas/<id>/atividades/<id>/entregas/zip/  → download ZIP

/painel/turmas/<id>/boletim/           → boletim da turma
/painel/turmas/<id>/boletim/exportar/csv/
/painel/turmas/<id>/boletim/exportar/pdf/

/painel/entregas/<id>/avaliar/         → HTMX: lançar nota + feedback

# Portal Público da Turma (sem login)
/turma/<token>/                 → página pública da turma
/turma/<token>/aulas/           → lista de aulas
/turma/<token>/aulas/<id>/      → detalhe da aula + materiais públicos
/turma/<token>/materiais/       → todos os materiais da turma
/turma/<token>/atividades/      → atividades (só visualização sem login)
/turma/<token>/entrar/          → Google Login (redirect allauth)

# Portal do Aluno (requer Google Login vinculado à turma)
/turma/<token>/minha-area/            → área do aluno
/turma/<token>/atividades/<id>/entregar/  → enviar entrega
/turma/<token>/minhas-notas/          → notas do aluno

# HTMX partials (retornam fragmentos HTML)
/htmx/turmas/<id>/stats/             → estatísticas da turma
/htmx/atividades/<id>/entregas-count/ → contador de entregas
/htmx/painel/feed/                    → feed de atividade recente
```

---

## 6. Views e Lógica de Negócio

### 6.1 Mixins de Autenticação

```python
# apps/core/mixins.py

class ProfessorRequiredMixin(LoginRequiredMixin):
    """Garante que apenas o professor acessa views /painel/"""
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_staff:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

class TurmaPublicaMixin:
    """Resolve turma pelo token_publico na URL"""
    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.turma = get_object_or_404(
            Turma, token_publico=kwargs['token'], ativa=True
        )

class AlunoAutenticadoMixin(TurmaPublicaMixin, LoginRequiredMixin):
    """Garante que o aluno autenticado pertence à turma"""
    def dispatch(self, request, *args, **kwargs):
        super().dispatch(request, *args, **kwargs)
        try:
            self.matricula = Matricula.objects.get(
                aluno__user=request.user,
                turma=self.turma,
                ativa=True
            )
        except Matricula.DoesNotExist:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)
```

---

### 6.2 Fluxo de Entrega de Atividade

```
Aluno acessa /turma/<token>/atividades/<id>/entregar/
    ↓
Verifica: aluno autenticado + matriculado + atividade publicada
    ↓
Verifica: já existe Entrega para este aluno?
    ├── Não → exibe formulário de entrega
    └── Sim → verifica permitir_reenvio + prazo
              ├── Pode reenviar → exibe form com dados anteriores
              └── Não pode → exibe mensagem + entrega anterior
    ↓
POST: valida form + calcula status
    ├── timezone.now() <= atividade.prazo → status = ENTREGUE
    └── timezone.now() > atividade.prazo  → status = ATRASADA
    ↓
Salva Entrega → redirect para confirmação
```

---

### 6.3 Geração de ZIP das Entregas

```python
# apps/atividades/views.py

class DownloadEntregasZipView(ProfessorRequiredMixin, View):
    def get(self, request, turma_id, atividade_id):
        atividade = get_object_or_404(Atividade, pk=atividade_id,
                                       turma_id=turma_id)
        entregas = atividade.entregas.filter(
            arquivo__isnull=False
        ).select_related('aluno')

        buffer = BytesIO()
        with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
            for entrega in entregas:
                nome_aluno = slugify(entrega.aluno.nome)
                ext = Path(entrega.arquivo.name).suffix
                filename = f"{nome_aluno}{ext}"
                zf.write(entrega.arquivo.path, filename)

        buffer.seek(0)
        slug_atividade = slugify(atividade.titulo)
        response = HttpResponse(buffer, content_type='application/zip')
        response['Content-Disposition'] = (
            f'attachment; filename="entregas_{slug_atividade}.zip"'
        )
        return response
```

---

### 6.4 Exportação do Boletim

```python
# apps/avaliacoes/views.py

class ExportarBoletimCSVView(ProfessorRequiredMixin, View):
    def get(self, request, turma_id):
        turma = get_object_or_404(Turma, pk=turma_id)
        atividades = turma.atividades.filter(publicada=True).order_by('prazo')
        alunos = turma.alunos.filter(matricula__ativa=True).order_by('nome')

        response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
        response['Content-Disposition'] = (
            f'attachment; filename="boletim_{turma.codigo}.csv"'
        )

        writer = csv.writer(response)
        header = ['Aluno', 'Matrícula'] + [a.titulo for a in atividades] + ['Média']
        writer.writerow(header)

        for aluno in alunos:
            notas = []
            for atividade in atividades:
                entrega = Entrega.objects.filter(
                    atividade=atividade, aluno=aluno
                ).first()
                notas.append(entrega.nota if entrega and entrega.nota else '')

            notas_numericas = [n for n in notas if isinstance(n, (int, float))]
            media = sum(notas_numericas) / len(notas_numericas) if notas_numericas else ''
            writer.writerow([aluno.nome, aluno.matricula] + notas + [media])

        return response
```

---

## 7. Templates e HTMX

### 7.1 Padrão de Template Base

```html
<!-- templates/base_admin.html -->
<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <title>{% block title %}ProfessorDash{% endblock %}</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <script src="https://unpkg.com/htmx.org@2.0.0/dist/htmx.min.js"></script>
  <script src="https://unpkg.com/alpinejs@3.x.x/dist/cdn.min.js" defer></script>
</head>
<body class="bg-gray-50">
  {% include "components/_sidebar.html" %}
  <main class="ml-64 p-8">
    {% if messages %}
      {% include "components/_messages.html" %}
    {% endif %}
    {% block content %}{% endblock %}
  </main>
</body>
</html>
```

---

### 7.2 Padrões HTMX Utilizados

```html
<!-- Inline edit de nota (sem reload de página) -->
<form
  hx-post="/painel/entregas/{{ entrega.id }}/avaliar/"
  hx-target="#entrega-{{ entrega.id }}"
  hx-swap="outerHTML"
>
  <input type="number" name="nota" min="0" max="10" step="0.1"
         value="{{ entrega.nota|default:'' }}">
  <button type="submit">Salvar</button>
</form>

<!-- Busca ao vivo de alunos -->
<input
  type="search"
  name="q"
  hx-get="/painel/turmas/{{ turma.id }}/alunos/"
  hx-trigger="keyup changed delay:300ms"
  hx-target="#lista-alunos"
  hx-swap="innerHTML"
  placeholder="Buscar aluno..."
>

<!-- Reordenação de aulas (drag-and-drop) -->
<ul
  id="lista-aulas"
  hx-post="/painel/turmas/{{ turma.id }}/aulas/reordenar/"
  hx-trigger="end"
  hx-swap="none"
  x-data="sortable()"
>
  {% for aula in aulas %}
    <li data-id="{{ aula.id }}" class="cursor-grab">
      {{ aula.numero }} — {{ aula.titulo }}
    </li>
  {% endfor %}
</ul>

<!-- Confirmação de exclusão via modal -->
<button
  hx-get="/painel/turmas/{{ turma.id }}/confirmar-exclusao/"
  hx-target="#modal"
  hx-swap="innerHTML"
>
  Excluir turma
</button>
<div id="modal"></div>
```

---

### 7.3 Alpine.js Stores

```javascript
// static/js/app.js

document.addEventListener('alpine:init', () => {

  // Sidebar collapse
  Alpine.store('sidebar', {
    collapsed: false,
    toggle() { this.collapsed = !this.collapsed }
  })

  // Tabs em páginas de detalhe de turma
  Alpine.store('tabs', {
    active: 'aulas',
    set(tab) { this.active = tab }
  })

  // Confirmação de ações destrutivas
  Alpine.store('confirm', {
    show: false,
    message: '',
    action: null,
    open(msg, fn) {
      this.message = msg
      this.action = fn
      this.show = true
    },
    confirm() { this.action?.(); this.show = false },
    cancel() { this.show = false }
  })
})
```

---

## 8. Autenticação e Permissões

### 8.1 Professor (Admin)
- Usuário Django com `is_staff=True`
- Login via `/entrar/` com email + senha
- Sessão armazenada no Redis
- Acesso exclusivo a todas as views `/painel/`

### 8.2 Aluno via Google OAuth
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

### 8.3 Configuração django-allauth
```python
# settings/base.py

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

---

## 9. Upload e Armazenamento de Arquivos

### 9.1 Configuração
```python
# settings/base.py

MEDIA_URL  = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Limites de upload
FILE_UPLOAD_MAX_MEMORY_SIZE = 50 * 1024 * 1024   # 50MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 50 * 1024 * 1024
```

### 9.2 Validação de Arquivos
```python
# apps/core/validators.py

TIPOS_PERMITIDOS_MATERIAL = [
    'application/pdf',
    'application/zip',
    'application/x-zip-compressed',
    'application/vnd.ms-powerpoint',
    'application/vnd.openxmlformats-officedocument.presentationml.presentation',
    'text/plain', 'text/html', 'text/markdown',
    'text/x-python', 'text/javascript', 'text/css',
    'application/json',
]

TIPOS_PERMITIDOS_ENTREGA = [
    *TIPOS_PERMITIDOS_MATERIAL,
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
]

def validar_arquivo(arquivo, tipos_permitidos):
    mime = magic.from_buffer(arquivo.read(1024), mime=True)
    arquivo.seek(0)
    if mime not in tipos_permitidos:
        raise ValidationError(f'Tipo de arquivo não permitido: {mime}')
    if arquivo.size > 50 * 1024 * 1024:
        raise ValidationError('Arquivo muito grande. Máximo: 50MB')
```

### 9.3 Caddy servindo media (produção)
```caddyfile
# docker/caddy/Caddyfile

aulas.tonicoimbra.com {
    # Arquivos de mídia servidos diretamente (sem passar pelo Django)
    handle /media/* {
        root * /srv/professordash
        file_server
        header Content-Disposition "attachment"
    }

    # Demais requests → Gunicorn
    reverse_proxy app:8000
}
```

---

## 10. Docker e Deploy

### 10.1 Dockerfile
```dockerfile
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y \
    libmagic1 libpango-1.0-0 libpangoft2-1.0-0 \
    libgdk-pixbuf2.0-0 libffi-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements/production.txt .
RUN pip install --no-cache-dir -r production.txt

COPY . .

RUN python manage.py collectstatic --noinput

EXPOSE 8000

ENTRYPOINT ["/app/docker/entrypoint.sh"]
CMD ["gunicorn", "config.wsgi:application", \
     "--bind", "0.0.0.0:8000", "--workers", "3"]
```

### 10.2 docker-compose.prod.yml
```yaml
version: "3.9"

services:
  app:
    build: .
    env_file: .env
    volumes:
      - /srv/professordash/media:/app/media
      - /srv/professordash/static:/app/staticfiles
    depends_on:
      - db
      - redis
    restart: unless-stopped

  db:
    image: postgres:16-alpine
    env_file: .env
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    restart: unless-stopped

  caddy:
    image: caddy:2-alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./docker/caddy/Caddyfile:/etc/caddy/Caddyfile
      - /srv/professordash/media:/srv/professordash/media:ro
      - /srv/professordash/static:/srv/professordash/static:ro
      - caddy_data:/data
    depends_on:
      - app
    restart: unless-stopped

volumes:
  postgres_data:
  caddy_data:
```

### 10.3 entrypoint.sh
```bash
#!/bin/bash
set -e

echo "Aguardando PostgreSQL..."
while ! nc -z db 5432; do sleep 0.5; done

echo "Executando migrations..."
python manage.py migrate --noinput

echo "Criando superuser se não existir..."
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(email='$DJANGO_SUPERUSER_EMAIL').exists():
    User.objects.create_superuser('$DJANGO_SUPERUSER_EMAIL', '$DJANGO_SUPERUSER_PASSWORD')
    print('Superuser criado.')
"

exec "$@"
```

### 10.4 .env.example
```env
# Django
SECRET_KEY=change-me-in-production
DEBUG=False
ALLOWED_HOSTS=aulas.tonicoimbra.com,localhost
DJANGO_SUPERUSER_EMAIL=toni@tonicoimbra.com
DJANGO_SUPERUSER_PASSWORD=senha-segura-aqui

# Banco de dados
POSTGRES_DB=professordash
POSTGRES_USER=prof
POSTGRES_PASSWORD=senha-db-aqui
DATABASE_URL=postgresql://prof:senha-db-aqui@db:5432/professordash

# Redis
REDIS_URL=redis://redis:6379/0

# Google OAuth (console.cloud.google.com)
GOOGLE_CLIENT_ID=xxx.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=xxx

# Email (opcional — para notificações futuras)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
```

---

## 11. Backup

```bash
# /etc/cron.d/professordash-backup

# Dump PostgreSQL diário às 2h
0 2 * * * root docker exec professordash-db-1 \
  pg_dump -U prof professordash | gzip \
  > /srv/backups/db_$(date +\%Y\%m\%d).sql.gz

# Backup de arquivos de media às 3h
0 3 * * * root tar -czf \
  /srv/backups/media_$(date +\%Y\%m\%d).tar.gz \
  /srv/professordash/media/

# Manter apenas últimos 30 dias
0 4 * * * root find /srv/backups/ -mtime +30 -delete
```

---

## 12. Variáveis de Ambiente por Ambiente

| Variável | Local | Produção |
|---|---|---|
| `DEBUG` | `True` | `False` |
| `DATABASE_URL` | SQLite ou Postgres local | Postgres no container |
| `ALLOWED_HOSTS` | `localhost,127.0.0.1` | `aulas.tonicoimbra.com` |
| `MEDIA_ROOT` | `./media` | `/app/media` (bind mount) |
| `REDIS_URL` | `redis://localhost:6379/0` | `redis://redis:6379/0` |

---

## 13. Convenções de Código

- **PEP 8** + **Black** (formatter) + **Ruff** (linter)
- **Commits**: `feat:`, `fix:`, `refactor:`, `docs:`, `chore:`
- **Branches**: `main` (produção), `dev` (desenvolvimento), `feature/<nome>`
- **Testes**: pytest + pytest-django, cobertura mínima de 60% nas views críticas
- **Views**: Class-Based Views em toda a aplicação (consistência)
- **Forms**: Django Forms para toda validação (nunca validar só no JS)
- **Queries N+1**: usar `select_related` / `prefetch_related` obrigatoriamente nas listagens

---

## 14. Checklist de Segurança

- [ ] `DEBUG=False` em produção
- [ ] `SECRET_KEY` única e segura (32+ chars aleatórios)
- [ ] `CSRF_COOKIE_SECURE=True` + `SESSION_COOKIE_SECURE=True`
- [ ] `X_FRAME_OPTIONS='DENY'`
- [ ] `SECURE_BROWSER_XSS_FILTER=True`
- [ ] Rate limiting no endpoint de upload (django-ratelimit)
- [ ] Validação de MIME type nos uploads (python-magic)
- [ ] Arquivos de entrega servidos com `Content-Disposition: attachment`
- [ ] Google OAuth configurado apenas para domínio do professor (opcional)
- [ ] Logs de acesso ativados no Caddy

---

*Versão 1.0 — Março 2026*
