# Aula 11 — Django REST Framework: Construindo APIs

Até agora, suas aplicações Django servem HTML — páginas para humanos lerem. Mas e quando você precisa que outros sistemas (um app mobile, um front-end React, outro servidor) consumam seus dados? Para isso existem APIs REST. O Django REST Framework (DRF) é a biblioteca mais usada para transformar seu Django em uma API RESTful completa, com serializers, viewsets e autenticação em poucas linhas de código.

## O que vamos construir

Uma API REST completa para o sistema de biblioteca: endpoints para listar, criar, editar e deletar autores e livros, com dados em JSON, navegação por URLs e autenticação por token.

:::objetivo Resultado final
Endpoints funcionais: GET/POST /api/autores/, GET/PUT/DELETE
/api/autores/1/, GET/POST /api/livros/, GET/PUT/DELETE
/api/livros/1/. Tudo retornando JSON.
:::

## Pré-projetos

:::dica Para esta aula você precisa de
Projeto Django das aulas 08-10 funcionando. DRF instalado:
pip install djangorestframework. Models Autor e Livro.
:::

## Passo a passo

1. **Instalar e configurar o DRF** — Adicione 'rest_framework' no INSTALLED_APPS.

```python
INSTALLED_APPS = [
    # ...
    'rest_framework',
    'livros',
]
```

2. **Criar os Serializers** — Serializers transformam objetos Python em JSON (e vice-versa). Em `livros/serializers.py`:

```python
from rest_framework import serializers
from .models import Autor, Livro

class AutorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Autor
        fields = ["id", "nome", "email", "data_nascimento"]

class LivroSerializer(serializers.ModelSerializer):
    autor_nome = serializers.CharField(source="autor.nome", read_only=True)
    
    class Meta:
        model = Livro
        fields = ["id", "titulo", "autor", "autor_nome", "ano_publicacao", "paginas", "disponivel"]
```

`ModelSerializer` é o equivalente do ModelForm para APIs: gera automaticamente os campos baseados no model. O campo `autor_nome` é um campo adicional que não está no model, mas é populado a partir do relacionamento.

3. **Criar as Viewsets** — ViewSets combinam listagem, criação, detalhe, atualização e deleção em uma única classe. Em `livros/views.py`:

```python
from rest_framework import viewsets
from .models import Autor, Livro
from .serializers import AutorSerializer, LivroSerializer

class AutorViewSet(viewsets.ModelViewSet):
    queryset = Autor.objects.all()
    serializer_class = AutorSerializer

class LivroViewSet(viewsets.ModelViewSet):
    queryset = Livro.objects.all()
    serializer_class = LivroSerializer
```

`ModelViewSet` fornece automaticamente as ações: list(), create(), retrieve(), update(), partial_update(), destroy(). Seis endpoints com 6 linhas de código.

4. **Criar as rotas com Router** — Em `livros/urls.py`:

```python
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'api/autores', views.AutorViewSet)
router.register(r'api/livros', views.LivroViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
```

O `DefaultRouter` gera automaticamente todas as URLs REST:

```
GET    /api/autores/        → listar autores
POST   /api/autores/        → criar autor
GET    /api/autores/1/      → detalhe do autor
PUT    /api/autores/1/      → atualizar autor (completo)
PATCH  /api/autores/1/      → atualizar autor (parcial)
DELETE /api/autores/1/      → deletar autor
```

5. **Testar no navegador** — Rode o servidor e acesse:

```bash
python manage.py runserver
```

Abra `http://127.0.0.1:8000/api/livros/` no navegador. O DRF fornece uma interface visual (Browsable API) onde você pode testar todos os endpoints.

:::exemplo Testando com curl
```bash
# Listar livros
curl http://127.0.0.1:8000/api/livros/

# Criar autor (POST com JSON)
curl -X POST http://127.0.0.1:8000/api/autores/ \
  -H "Content-Type: application/json" \
  -d '{"nome": "Machado de Assis", "email": "machado@example.com"}'

# Detalhe do autor
curl http://127.0.0.1:8000/api/autores/1/
```
:::

6. **Adicionar filtros e busca** — DRF permite filtrar com poucas linhas.

```python
from rest_framework import filters

class LivroViewSet(viewsets.ModelViewSet):
    queryset = Livro.objects.all()
    serializer_class = LivroSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["titulo", "autor__nome"]
    ordering_fields = ["titulo", "ano_publicacao"]
```

Agora você pode buscar: `GET /api/livros/?search=harry` e ordenar: `GET /api/livros/?ordering=-ano_publicacao`.

7. **Adicionar autenticação por Token** — Proteja a API.

Em `settings.py`:

```python
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ],
}
```

Depois execute `python manage.py migrate` e crie tokens pelo admin ou por código.

## Checkpoint

:::objetivo Você está no caminho certo se
Acessar /api/livros/ no navegador mostra a lista de livros em
JSON com formato legível. É possível criar autor via POST e
ver os dados em tempo real. Os endpoints GET, POST, PUT, DELETE
funcionam corretamente.
:::

## Erros comuns

:::atencao Sintoma: 404 em todas as rotas da API
Causa: as rotas do router não estão incluídas no urlpatterns
do projeto. Correção: verifique se livros/urls.py está incluído
em biblioteca/urls.py com include("livros.urls") e se o router
está registrado com os paths corretos.
:::

:::atencao Sintoma: "Serializer does not exist" ou erro de field
Causa: o serializer referência um campo que não existe no model
ou a sintaxe source="..." está errada. Correção: verifique se
o nome dos campos corresponde exatamente ao que está no model.
:::

## Desafio

Crie um endpoint personalizado `/api/livros/disponiveis/` que retorna apenas os livros com disponivel=True. Use `@action(detail=False)` no ViewSet.

:::importante Desafio extra
Para quem terminar primeiro: implemente paginação customizada na
API que retorna 5 itens por página com links para anterior/próximo.
O DRF já tem isso embutido — configure em settings.py com
DEFAULT_PAGINATION_CLASS e PAGE_SIZE.
:::

## Fechamento

:::resumo
- Django REST Framework transforma Django em uma API REST em minutos
- ModelSerializer gera campos JSON automaticamente a partir do model
- ModelViewSet fornece 6 ações REST em uma classe
- DefaultRouter gera URLs REST automaticamente
- SearchFilter, OrderingFilter adicionam busca e ordenação
- TokenAuthentication protege a API com autenticação
- Próxima aula: projeto final — API de catálogo de filmes
:::
