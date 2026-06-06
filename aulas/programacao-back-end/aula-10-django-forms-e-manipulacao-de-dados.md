# Aula 10 — Django: Forms e manipulação de dados

Até agora, você criou páginas que exibem dados do banco. Mas como o usuário comum (sem acesso ao admin) pode cadastrar, editar ou deletar livros? A resposta são os formulários Django. Com `ModelForm`, você transforma um model em um formulário HTML completo — com validação, segurança contra CSRF e persistência — em poucas linhas de código.

## O que vamos construir

Um sistema completo de CRUD (Create, Read, Update, Delete) para o model Livro. O usuário poderá cadastrar novos livros via formulário, editar livros existentes e deletar livros, tudo com validação automática do Django.

:::objetivo Resultado final
Páginas em /livros/criar/, /livros/1/editar/ e /livros/1/deletar/
com formulários funcionais que criam, atualizam e removem registros
do banco de dados.
:::

## Pré-requisitos

:::dica Para esta aula você precisa de
Projeto Django das aulas 08 e 09 funcionando. Models Autor e Livro
criados. Pelo menos 1 autor cadastrado no admin para associar aos
livros.
:::

## Passo a passo

1. **Criar o ModelForm** — Em `livros/forms.py`, defina o formulário baseado no model Livro.

```python
from django import forms
from .models import Livro

class LivroForm(forms.ModelForm):
    class Meta:
        model = Livro
        fields = ["titulo", "autor", "ano_publicacao", "paginas", "disponivel"]
        widgets = {
            "ano_publicacao": forms.NumberInput(attrs={"min": 1900, "max": 2026}),
        }
    
    def clean_ano_publicacao(self):
        ano = self.cleaned_data["ano_publicacao"]
        if ano  2026:
            raise forms.ValidationError("O ano não pode ser no futuro.")
        return ano
```

O `ModelForm` gera automaticamente os campos HTML baseados nos tipos dos campos do model. O método `clean_ano_publicacao` é um validador customizado — Django chama métodos `clean_nomecampo()` automaticamente durante a validação.

2. **Criar as views de Criar, Editar e Deletar** — Use as views genéricas do Django.

Em `livros/views.py`:

```python
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, DeleteView
from .models import Livro
from .forms import LivroForm

class CriarLivroView(CreateView):
    model = Livro
    form_class = LivroForm
    template_name = "livros/form.html"
    success_url = reverse_lazy("livros:lista")

class EditarLivroView(UpdateView):
    model = Livro
    form_class = LivroForm
    template_name = "livros/form.html"
    success_url = reverse_lazy("livros:lista")

class DeletarLivroView(DeleteView):
    model = Livro
    template_name = "livros/deletar.html"
    success_url = reverse_lazy("livros:lista")
```

`CreateView` exibe o formulário vazio e salva um novo objeto. `UpdateView` pré-preenche com os dados existentes. `DeleteView` mostra uma tela de confirmação. Todas herdam validação e persistência automáticas.

3. **Adicionar as URLs** — Em `livros/urls.py`:

```python
urlpatterns = [
    path("", views.ListaLivrosView.as_view(), name="lista"),
    path("criar/", views.CriarLivroView.as_view(), name="criar"),
    path("/", views.DetalheLivroView.as_view(), name="detalhe"),
    path("/editar/", views.EditarLivroView.as_view(), name="editar"),
    path("/deletar/", views.DeletarLivroView.as_view(), name="deletar"),
]
```

4. **Criar o template do formulário** — `livros/templates/livros/form.html`:

```html
{% load static %}



    
    
    {% if form.instance.pk %}Editar{% else %}Novo{% endif %} Livro
    


    {% if form.instance.pk %}Editar{% else %}Novo{% endif %} Livro
    
    
        {% csrf_token %}
        
        {% for field in form %}
            
                {{ field.label_tag }}
                {{ field }}
                {% if field.errors %}
                    
                    {% for erro in field.errors %}
                        {{ erro }}
                    {% endfor %}
                    
                {% endif %}
            
        {% endfor %}
        
        Salvar
        Cancelar
    


```

`{% csrf_token %}` é obrigatório em todo formulário Django — é uma proteção contra ataques de falsificação de requisição entre sites. `novalidate` no form desativa a validação nativa do HTML5 para testar a validação do Django.

5. **Criar o template de confirmação de exclusão** — `livros/templates/livros/deletar.html`:

```html
{% load static %}



    
    Deletar Livro
    


    Deletar Livro
    Tem certeza que deseja deletar **{{ object.titulo }}**?
    
        {% csrf_token %}
        Sim, deletar
        Cancelar
    


```

6. **Adicionar CSS para os formulários** — No `estilo.css` existente:

```css
form { background: white; padding: 24px; border-radius: 6px; }
.campo { margin-bottom: 16px; }
.campo label { display: block; font-weight: bold; margin-bottom: 4px; color: #333; }
.campo input, .campo select, .campo textarea { width: 100%; padding: 8px; border: 2px solid #ddd; border-radius: 4px; }
.erros { color: #e63946; font-size: 0.85rem; list-style: none; padding: 0; margin-top: 4px; }
button { background: #2a9d8f; color: white; border: none; padding: 10px 20px; border-radius: 4px; cursor: pointer; margin-right: 8px; }
```

7. **Adicionar links no template de lista** — Atualize `lista.html` para ter links de ação:

```html
{% for livro in livros %}
    
        {{ livro.titulo }}
        — {{ livro.autor.nome }}
        
            ✏️ Editar
            🗑️
        
    
{% endfor %}
+ Novo Livro
```

## Checkpoint

:::objetivo Você está no caminho certo se
Você consegue criar um novo livro pelo /livros/criar/, editar
um existente clicando em Editar, e deletar um livro com confirmação.
A validação impede ano menor que 1450 ou maior que 2026.
:::

## Erros comuns

:::atencao Sintoma: formulário mostra "CSRF token missing"
Causa: falta {% csrf_token %} dentro do .
Correção: adicione {% csrf_token %} em todos os formulários
que usam POST. É obrigatório por segurança.
:::

:::atencao Sintoma: formulário não salva e não mostra erro
Causa: o form pode estar sendo submetido sem validação ou a view
não está encontrando o template certo.
Correção: verifique se o template_name está correto e se o form
está sendo renderizado com erros. Adicione {{ form.errors }} no
template para depuração.
:::

## Desafio

Adicione um campo de busca na lista que filtra livros por título usando um formulário GET. Use `Livro.objects.filter(titulo__icontains=...)`.

:::importante Desafio extra
Para quem terminar primeiro: adicione validação no form que
impeça o mesmo título com o mesmo autor (unique together).
Use a Meta class com unique_together = [['titulo', 'autor']]
no model Livro e trate o erro no form.
:::

## Fechamento

:::resumo
- ModelForm gera formulários HTML automaticamente a partir dos models
- CreateView, UpdateView e DeleteView são views genéricas de CRUD
- {% csrf_token %} protege contra falsificação de requisição
- clean_nomecampo() permite validação customizada por campo
- reverse_lazy resolve URLs para redirect após operações
- Próxima aula: Django REST Framework — construindo APIs
:::
