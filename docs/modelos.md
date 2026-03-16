# Modelos de Dados — ProfessorDash

## Relacionamentos

```
Turma
  ├── → Alunos (M2M via Matricula)
  ├── → Aulas
  ├── → Materiais
  └── → Atividades
           └── → Entregas (uma por aluno)

Aula
  └── → Materiais

Aluno
  ├── → User (OneToOne, opcional — vinculado ao Google)
  └── → Matriculas
```

---

## core.BaseModel

Classe abstrata herdada por todos os modelos.

```python
class BaseModel(models.Model):
    criado_em     = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    class Meta:
        abstract = True
```

---

## alunos.Aluno

```python
class Aluno(BaseModel):
    user      = models.OneToOneField(User, null=True, blank=True, on_delete=SET_NULL)
    nome      = models.CharField(max_length=200)
    email     = models.EmailField(unique=True)
    matricula = models.CharField(max_length=30, blank=True)
    avatar    = models.ImageField(upload_to='avatares/', blank=True)
    ativo     = models.BooleanField(default=True)
```

---

## turmas.Turma

```python
class Turma(BaseModel):
    nome          = models.CharField(max_length=200)
    codigo        = models.CharField(max_length=20, unique=True)
    descricao     = models.TextField(blank=True)
    periodo       = models.CharField(max_length=20)   # "1º Semestre"
    ano_letivo    = models.IntegerField()
    token_publico = models.UUIDField(default=uuid4, unique=True)
    ativa         = models.BooleanField(default=True)
    alunos        = models.ManyToManyField('alunos.Aluno', through='Matricula')
```

`token_publico` é usado na URL pública da turma (`/turma/<token>/`).

## turmas.Matricula

```python
class Matricula(BaseModel):
    aluno        = models.ForeignKey(Aluno, on_delete=CASCADE)
    turma        = models.ForeignKey(Turma, on_delete=CASCADE)
    data_entrada = models.DateField(auto_now_add=True)
    ativa        = models.BooleanField(default=True)
    class Meta:
        unique_together = ('aluno', 'turma')
```

---

## aulas.Aula

```python
class Aula(BaseModel):
    turma    = models.ForeignKey(Turma, on_delete=CASCADE, related_name='aulas')
    titulo   = models.CharField(max_length=300)
    numero   = models.PositiveIntegerField()
    data     = models.DateField(null=True, blank=True)
    conteudo = MarkdownxField(blank=True)
    realizada = models.BooleanField(default=False)
    ordem    = models.PositiveIntegerField(default=0)
    class Meta:
        ordering = ['ordem', 'numero']
        unique_together = ('turma', 'numero')
```

---

## materiais.Material

**Tipos:** `pdf`, `zip`, `markdown`, `link`, `arquivo`

**Visibilidade:** `publico` (link da turma basta) | `restrito` (requer Google Login)

```python
class Material(BaseModel):
    turma        = models.ForeignKey(Turma, on_delete=CASCADE)
    aula         = models.ForeignKey(Aula, null=True, blank=True, on_delete=SET_NULL)
    titulo       = models.CharField(max_length=300)
    tipo         = models.CharField(max_length=20, choices=TipoMaterial.choices)
    visibilidade = models.CharField(max_length=20, choices=VisibilidadeMaterial.choices)
    # campos mutuamente exclusivos por tipo:
    arquivo      = models.FileField(upload_to='materiais/%Y/%m/', null=True, blank=True)
    url_externa  = models.URLField(blank=True)
    conteudo_md  = MarkdownxField(blank=True)
    ordem        = models.PositiveIntegerField(default=0)
```

---

## atividades.Atividade

**Tipos de entrega:** `arquivo`, `texto`, `link`

```python
class Atividade(BaseModel):
    turma            = models.ForeignKey(Turma, on_delete=CASCADE)
    aula             = models.ForeignKey(Aula, null=True, blank=True, on_delete=SET_NULL)
    titulo           = models.CharField(max_length=300)
    descricao        = MarkdownxField()
    tipo_entrega     = models.CharField(max_length=20, choices=TipoEntrega.choices)
    prazo            = models.DateTimeField()
    valor_pontos     = models.DecimalField(max_digits=5, decimal_places=2, default=10.0)
    permitir_reenvio = models.BooleanField(default=True)
    publicada        = models.BooleanField(default=True)

    @property
    def esta_aberta(self):
        return self.publicada and timezone.now() <= self.prazo
```

## atividades.Entrega

**Status:** `pendente`, `entregue`, `atrasada`, `avaliada`

Regra: uma entrega por aluno por atividade (`unique_together`).

```python
class Entrega(BaseModel):
    atividade      = models.ForeignKey(Atividade, on_delete=CASCADE)
    aluno          = models.ForeignKey(Aluno, on_delete=CASCADE)
    status         = models.CharField(max_length=20, choices=StatusEntrega.choices)
    arquivo        = models.FileField(upload_to='entregas/%Y/%m/', null=True, blank=True)
    texto          = models.TextField(blank=True)
    url            = models.URLField(blank=True)
    data_envio     = models.DateTimeField(auto_now_add=True)
    nota           = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    feedback       = models.TextField(blank=True)
    data_avaliacao = models.DateTimeField(null=True, blank=True)
    class Meta:
        unique_together = ('atividade', 'aluno')
```

---

## Limites de Upload

- Tamanho máximo: **50MB** por arquivo
- Tipos validados via `python-magic` (MIME type real, não extensão)
- Tipos permitidos para materiais: PDF, ZIP, PPTX, TXT, HTML, MD, PY, JS, CSS, JSON
- Tipos adicionais para entregas: DOC, DOCX
