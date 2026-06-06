# Aula 12 — Projeto final: API de catálogo de filmes

Você chegou ao final da trilha de Programação Back-End. Neste projeto final, você vai construir uma API REST completa para um catálogo de filmes, integrando tudo que aprendeu: models, views, serializers, autenticação, permissões, buscas e relacionamentos. O projeto simula um sistema real de backend que poderia alimentar um serviço de streaming ou uma locadora virtual.

## O que vamos construir

Uma API REST para catálogo de filmes com três models (Filme, Diretor, Gênero), relacionamentos N:N, autenticação por token, permissões diferenciadas e endpoints com busca, filtro e paginação.

:::objetivo Resultado final
API completa com: CRUD de filmes, diretores e gêneros; busca por
título e diretor; filtro por gênero; paginação; autenticação para
escrita e leitura pública.
:::

## Pré-requisitos

:::dica Para esta aula você precisa de
Django e DRF instalados. Conhecimento das aulas 08 a 11.
Projeto em branco para começar (crie um novo projeto chamado
catalogo). Vontade de construir algo do zero com supervisão
mínima.
:::

## Passo a passo

1. **Criar o projeto e configurar** — No terminal:

```bash
django-admin startproject catalogo
cd catalogo
python manage.py startapp filmes
```

Adicione `'rest_framework'` e `'filmes'` ao `INSTALLED_APPS`.

2. **Criar os models** — Em `filmes/models.py`:

```python
from django.db import models

class Diretor(models.Model):
    nome = models.CharField(max_length=200)
    data_nascimento = models.DateField(blank=True, null=True)
    nacionalidade = models.CharField(max_length=100, blank=True)
    
    class Meta:
        verbose_name = "Diretor"
        verbose_name_plural = "Diretores"
        ordering = ["nome"]
    
    def __str__(self):
        return self.nome

class Genero(models.Model):
    nome = models.CharField(max_length=100, unique=True)
    
    class Meta:
        verbose_name = "Gênero"
        verbose_name_plural = "Gêneros"
        ordering = ["nome"]
    
    def __str__(self):
        return self.nome

class Filme(models.Model):
    titulo = models.CharField(max_length=300)
    sinopse = models.TextField(blank=True)
    ano_lancamento = models.IntegerField()
    duracao_minutos = models.IntegerField(help_text="Duração em minutos")
    diretor = models.ForeignKey(Diretor, on_delete=models.CASCADE, related_name="filmes")
    generos = models.ManyToManyField(Genero, related_name="filmes")
    data_cadastro = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Filme"
        verbose_name_plural = "Filmes"
        ordering = ["-ano_lancamento", "titulo"]
    
    def __str__(self):
        return self.titulo
```

`ManyToManyField` cria uma tabela intermediária automaticamente. Um filme pode ter vários gêneros e um gênero pode estar em vários filmes.

3. **Criar os Serializers** — Em `filmes/serializers.py`:

```python
from rest_framework import serializers
from .models import Filme, Diretor, Genero

class GeneroSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genero
        fields = ["id", "nome"]

class DiretorSerializer(serializers.ModelSerializer):
    filmes_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Diretor
        fields = ["id", "nome", "data_nascimento", "nacionalidade", "filmes_count"]
    
    def get_filmes_count(self, obj):
        return obj.filmes.count()

class FilmeSerializer(serializers.ModelSerializer):
    diretor_nome = serializers.CharField(source="diretor.nome", read_only=True)
    generos_nomes = serializers.SerializerMethodField()
    
    class Meta:
        model = Filme
        fields = [
            "id", "titulo", "sinopse", "ano_lancamento", "duracao_minutos",
            "diretor", "diretor_nome", "generos", "generos_nomes", "data_cadastro"
        ]
    
    def get_generos_nomes(self, obj):
        return [g.nome for g in obj.generos.all()]
```

4. **Criar as Viewsets** — Com permissões e filtros personalizados:

```python
from rest_framework import viewsets, permissions, filters
from .models import Filme, Diretor, Genero
from .serializers import FilmeSerializer, DiretorSerializer, GeneroSerializer

class DiretorViewSet(viewsets.ModelViewSet):
    queryset = Diretor.objects.all()
    serializer_class = DiretorSerializer
    search_fields = ["nome", "nacionalidade"]
    ordering_fields = ["nome"]

class GeneroViewSet(viewsets.ModelViewSet):
    queryset = Genero.objects.all()
    serializer_class = GeneroSerializer

class FilmeViewSet(viewsets.ModelViewSet):
    queryset = Filme.objects.select_related("diretor").prefetch_related("generos")
    serializer_class = FilmeSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["titulo", "diretor__nome", "sinopse"]
    ordering_fields = ["titulo", "ano_lancamento", "duracao_minutos"]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        genero = self.request.query_params.get("genero")
        if genero:
            queryset = queryset.filter(generos__nome__icontains=genero)
        ano = self.request.query_params.get("ano")
        if ano:
            queryset = queryset.filter(ano_lancamento=ano)
        return queryset
    
    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = [permissions.AllowAny]
        return [p() for p in permission_classes]
```

5. **Configurar rotas e settings** — No `urls.py`:

```python
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from filmes import views

router = DefaultRouter()
router.register(r'api/filmes', views.FilmeViewSet)
router.register(r'api/diretores', views.DiretorViewSet)
router.register(r'api/generos', views.GeneroViewSet)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include(router.urls)),
    path("api-auth/", include("rest_framework.urls")),
]
```

Em `settings.py`, configure REST Framework e CORS (se for consumir de front-end separado):

```python
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
}
```

6. **Povoar o banco com dados de teste** — Crie um management command ou use o shell:

```bash
python manage.py createsuperuser
python manage.py runserver
```

Acesse /admin/ e cadastre diretores, gêneros e filmes. Ou crie um script populate.py:

```python
### populate.py — execute com python manage.py shell < populate.py
from filmes.models import Diretor, Genero, Filme

d1 = Diretor.objects.create(nome="Christopher Nolan", nacionalidade="Britânico")
d2 = Diretor.objects.create(nome="Greta Gerwig", nacionalidade="Americana")

g1 = Genero.objects.create(nome="Ficção Científica")
g2 = Genero.objects.create(nome="Drama")
g3 = Genero.objects.create(nome="Comédia")

f1 = Filme.objects.create(titulo="Interestelar", sinopse="...", ano_lancamento=2014, duracao_minutos=169, diretor=d1)
f1.generos.add(g1, g2)

f2 = Filme.objects.create(titulo="Barbie", sinopse="...", ano_lancamento=2023, duracao_minutos=114, diretor=d2)
f2.generos.add(g2, g3)
```

## Checkpoint

:::objetivo Você está no caminho certo se
Acessar /api/filmes/ mostra a lista paginada com 10 itens por
página. GET /api/filmes/?search=interestelar retorna o filme.
GET /api/filmes/?genero=Drama filtra por gênero. POST, PUT, DELETE
exigem autenticação (token ou sessão).
:::

## Erros comuns

:::atencao Sintoma: erro ao serializar ManyToManyField
Causa: o serializer não tem o campo generos declarado ou está
tentando serializar objetos sem o método __str__.
Correção: use SerializerMethodField ou PrimaryKeyRelatedField
para relacionamentos M:N. Garanta que todos os models tenham
__str__ definido.
:::

:::atencao Sintoma: "duplicate key" ao cadastrar gênero
Causa: o campo nome em Genero tem unique=True e o gênero já existe.
Correção: use get_or_create() no código de povoamento ou trate
a exceção IntegrityError no serializer.
:::

## Desafio

Implemente um endpoint `/api/filmes/estatisticas/` que retorna: total de filmes, média de duração, filme mais antigo, filme mais recente e diretor com mais filmes.

:::importante Desafio extra
Para quem terminar primeiro: adicione documentação automática da
API com drf-spectacular (OpenAPI/Swagger). Instale, configure e
acesse /api/docs/ para ver a documentação interativa.
:::

## Fechamento

:::resumo
- Projeto final integra models, serializers, viewsets e routers
- ManyToManyField cria relacionamentos N:N com tabela intermediária
- Filtros customizados via query_params em get_queryset()
- Permissões diferenciadas por ação (action) no ViewSet
- Paginação, busca e ordenação são configuradas em poucas linhas
- A API REST está pronta para ser consumida por qualquer front-end
- Próxima trilha: Banco de Dados — modelagem e SQL
:::
