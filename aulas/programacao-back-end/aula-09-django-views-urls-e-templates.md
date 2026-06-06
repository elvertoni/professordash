# Aula 09 — Django: Views, URLs e Templates

Na aula anterior, você criou models e aprendeu a gerenciar dados pelo admin do Django. Agora vamos dar o próximo passo: construir páginas web dinâmicas que os usuários comuns (sem acesso ao admin) podem ver. Para isso, vamos aprender o trio Views + URLs + Templates — a espinha dorsal de qualquer aplicação Django.

## O que vamos construir

Uma página inicial que lista todos os livros cadastrados e uma página de detalhe que mostra as informações completas de um livro específico. Tudo com HTML estilizado usando templates Django.

:::objetivo Resultado final
Duas rotas: /livros/ (lista todos os livros) e /livros/1/
(detalhe do livro com ID 1). Dados vêm do banco, renderizados
em HTML com template Django.
:::

## Pré-requisitos

:::dica Para esta aula você precisa de
Projeto Django da aula 08 (biblioteca) funcionando com models
Autor e Livro. Pelo menos 3 livros cadastrados no admin.
:::

## Passo a passo

1. **Criar a view baseada em classe** — No `livros/views.py`, use ListView.

```python
from django.views.generic import ListView, DetailView
from .models import Livro

class ListaLivrosView(ListView):
    model = Livro
    template_name = "livros/lista.html"
    context_object_name = "livros"
    paginate_by = 10
```

Class-Based Views (CBVs) são a forma recomendada de criar views no Django. `ListView` busca automaticamente todos os objetos do model e os disponibiliza no template.

2. **Criar a view de detalhe** — DetailView mostra um único objeto.

```python
class DetalheLivroView(DetailView):
    model = Livro
    template_name = "livros/detalhe.html"
    context_object_name = "livro"
```

O `DetailView` espera um parâmetro `pk` (primary key) na URL para identificar qual objeto carregar.

3. **Criar as URLs** — No arquivo `livros/urls.py`, mapeie as views.

```python
from django.urls import path
from . import views

app_name = "livros"

urlpatterns = [
    path("", views.ListaLivrosView.as_view(), name="lista"),
    path("<int:pk>/", views.DetalheLivroView.as_view(), name="detalhe"),
]
```

O `<int:pk>` captura um número inteiro da URL e passa como parâmetro `pk` para a view. O `app_name` cria um namespace para as URLs.

4. **Incluir as URLs do app no projeto** — Edite `biblioteca/urls.py`:

```python
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("livros/", include("livros.urls")),
]
```

5. **Criar o template de lista** — Crie `livros/templates/livros/` e o arquivo `lista.html`:

```html
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Biblioteca</title>
</head>
<body>
    <h1>Biblioteca</h1>
    
    {% if livros %}
        <ul>
        {% for livro in livros %}
            <li>
                <a href="{% url 'livros:detalhe' livro.pk %}">
                    {{ livro.titulo }}
                </a>
                — {{ livro.autor.nome }} ({{ livro.ano_publicacao }})
            </li>
        {% empty %}
            <li>Nenhum livro cadastrado.</li>
        {% endfor %}
        </ul>
    {% endif %}
</body>
</html>
```

Os blocos `{% %}` são tags de template Django. `{% url 'livros:detalhe' livro.pk %}` gera dinamicamente o link para a página de detalhe.

6. **Criar o template de detalhe** — `livros/templates/livros/detalhe.html`:

```html
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ livro.titulo }} — Biblioteca</title>
</head>
<body>
    <h1>{{ livro.titulo }}</h1>
    
    <dl>
        <dt>Autor</dt>
        <dd>{{ livro.autor.nome }}</dd>
        
        <dt>Ano de Publicação</dt>
        <dd>{{ livro.ano_publicacao }}</dd>
        
        <dt>Páginas</dt>
        <dd>{{ livro.paginas }}</dd>
        
        <dt>Disponível</dt>
        <dd>{{ livro.disponivel|yesno:"Sim,Não" }}</dd>
        
        {% if livro.disponivel %}
            <dd style="color: green;">✅ Disponível para empréstimo</dd>
        {% else %}
            <dd style="color: red;">❌ Indisponível</dd>
        {% endif %}
    </dl>
    
    <a href="{% url 'livros:lista' %}">← Voltar à lista</a>
</body>
</html>
```

As variáveis `{{ }}` são substituídas pelos valores do objeto. `{{ livro.autor.nome }}` navega pelo relacionamento ForeignKey para exibir o nome do autor.

7. **Adicionar CSS básico** — Crie `livros/static/livros/estilo.css`:

```css
body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; background: #f4f4f4; }
h1 { color: #1a1a2e; }
ul { list-style: none; padding: 0; }
li { background: white; padding: 12px; margin-bottom: 8px; border-radius: 6px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
a { color: #2a9d8f; text-decoration: none; }
dl { background: white; padding: 20px; border-radius: 6px; }
dt { font-weight: bold; color: #333; margin-top: 12px; }
dd { margin-left: 0; color: #555; }
```

Carregue o CSS no template com `{% load static %}` e `<link rel="stylesheet" href="{% static 'livros/estilo.css' %}">`.

## Checkpoint

:::objetivo Você está no caminho certo se
Ao acessar /livros/, você vê a lista de livros cadastrados.
Cada título é um link para a página de detalhe. A página de
detalhe mostra todas as informações do livro e um link de volta.
:::

## Erros comuns

:::atencao Sintoma: TemplateDoesNotExist
Causa: o arquivo do template não está no diretório correto.
Correção: o template deve estar em livros/templates/livros/
(a pasta templates DENTRO do app, com subpasta com o nome do app).
:::

:::atencao Sintoma: NoReverseMatch ao clicar em um link
Causa: a tag {% url %} está com nome errado ou a view não está
registrada nas URLs. Correção: verifique se app_name está definido
em livros/urls.py e se o nome da URL (ex.: 'detalhe') corresponde.
:::

## Desafio

Adicione uma view de busca: `/livros/busca/?q=python` que filtra livros cujo título contenha "python". Use `request.GET.get('q')` e `Livro.objects.filter(titulo__icontains=...)`.

:::importante Desafio extra
Para quem terminar primeiro: implemente herança de templates.
Crie um template base.html com header, main e footer, e faça
lista.html e detalhe.html estenderem ele com {% extends "base.html" %}
e {% block content %}.
:::

## Código completo (views.py)

```python
from django.views.generic import ListView, DetailView
from .models import Livro

class ListaLivrosView(ListView):
    model = Livro
    template_name = "livros/lista.html"
    context_object_name = "livros"
    paginate_by = 10

class DetalheLivroView(DetailView):
    model = Livro
    template_name = "livros/detalhe.html"
    context_object_name = "livro"
```

## Código completo (urls.py do app)

```python
from django.urls import path
from . import views

app_name = "livros"

urlpatterns = [
    path("", views.ListaLivrosView.as_view(), name="lista"),
    path("busca/", views.BuscaLivrosView.as_view(), name="busca"),
    path("<int:pk>/", views.DetalheLivroView.as_view(), name="detalhe"),
]
```

## Fechamento

:::resumo
- Class-Based Views (ListView, DetailView) encapsulam lógica comum
- URLs mapeiam padrões de endereço para views específicas
- Templates Django combinam HTML com {{ variaveis }} e {% tags %}
- {% url 'app_name:name' param %} gera links dinâmicos
- Static files (CSS, JS, imagens) ficam em app/static/app/
- Próxima aula: Django Forms e manipulação de dados
:::
