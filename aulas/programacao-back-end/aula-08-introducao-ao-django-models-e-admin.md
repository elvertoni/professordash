# Aula 08 — Introdução ao Django: Models e Admin

Depois de aprender lógica, estruturas de dados e orientação a objetos em Python, chegou a hora de construir algo que roda na web. Django é o framework web mais usado no ecossistema Python — ele fornece tudo o que você precisa para criar um site com banco de dados, autenticação, admin e muito mais. Nesta aula prática, vamos criar um projeto Django do zero e definir nossos primeiros models (modelos de dados) com registro no admin.

## O que vamos construir

Um projeto Django chamado `biblioteca` com um app `livros`. Vamos definir dois models: `Autor` e `Livro`, com campos para título, ano, número de páginas e relacionamento entre eles. Tudo registrado no admin do Django para gerenciar os dados.

:::objetivo Resultado final
Um projeto Django funcional onde você acessa /admin/, faz login
e consegue cadastrar autores e livros em um banco SQLite.
:::

## Pré-requisitos

:::dica Para esta aula você precisa de
Python 3, Django instalado (pip install django), terminal.
Conhecimento de POO e Python básico das aulas anteriores.
:::

## Passo a passo

1. **Criar o projeto e o app** — No terminal, execute:

```bash
django-admin startproject biblioteca
cd biblioteca
python manage.py startapp livros
```

O comando `startproject` cria a estrutura do projeto. `startapp` cria um app — cada módulo funcional do projeto.

2. **Registrar o app no settings** — Abra `biblioteca/settings.py` e adicione `'livros'` em `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    # ... outros apps padrão ...
    'livros',  # <-- adicione esta linha
]
```

3. **Criar o model Autor** — No arquivo `livros/models.py`, defina a classe:

```python
from django.db import models

class Autor(models.Model):
    nome = models.CharField(max_length=100, verbose_name="Nome")
    email = models.EmailField(blank=True, null=True, verbose_name="E-mail")
    data_nascimento = models.DateField(blank=True, null=True, verbose_name="Data de Nascimento")
    biografia = models.TextField(blank=True, verbose_name="Biografia")
    
    class Meta:
        verbose_name = "Autor"
        verbose_name_plural = "Autores"
        ordering = ["nome"]
    
    def __str__(self):
        return self.nome
```

Cada classe que herda de `models.Model` vira uma tabela no banco de dados. Os atributos da classe são os campos da tabela. `CharField` vira VARCHAR, `TextField` vira TEXT, `DateField` vira DATE, `EmailField` vira VARCHAR com validação de email.

4. **Criar o model Livro** — Com chave estrangeira para Autor.

```python
class Livro(models.Model):
    titulo = models.CharField(max_length=200, verbose_name="Título")
    autor = models.ForeignKey(
        Autor, 
        on_delete=models.CASCADE, 
        related_name="livros",
        verbose_name="Autor"
    )
    ano_publicacao = models.IntegerField(verbose_name="Ano de Publicação")
    paginas = models.IntegerField(verbose_name="Número de Páginas")
    disponivel = models.BooleanField(default=True, verbose_name="Disponível")
    
    class Meta:
        verbose_name = "Livro"
        verbose_name_plural = "Livros"
        ordering = ["titulo"]
    
    def __str__(self):
        return f"{self.titulo} ({self.autor.nome})"
```

`ForeignKey` cria um relacionamento N:1 (muitos livros para um autor). `on_delete=models.CASCADE` significa: se o autor for deletado, todos os livros dele também são deletados. `related_name="livros"` permite acessar `autor.livros.all()`.

5. **Gerar e executar as migrações** — Django traduz models em SQL.

```bash
python manage.py makemigrations
python manage.py migrate
```

`makemigrations` cria o arquivo de migração (instruções para o banco). `migrate` executa essas instruções, criando as tabelas no banco SQLite.

6. **Registrar os models no admin** — No arquivo `livros/admin.py`:

```python
from django.contrib import admin
from .models import Autor, Livro

class LivroInline(admin.TabularInline):
    model = Livro
    extra = 1

@admin.register(Autor)
class AutorAdmin(admin.ModelAdmin):
    list_display = ["nome", "email", "data_nascimento"]
    search_fields = ["nome", "email"]
    inlines = [LivroInline]

@admin.register(Livro)
class LivroAdmin(admin.ModelAdmin):
    list_display = ["titulo", "autor", "ano_publicacao", "paginas", "disponivel"]
    list_filter = ["disponivel", "autor"]
    search_fields = ["titulo"]
```

7. **Criar superusuário e testar** — Acesse o admin.

```bash
python manage.py createsuperuser
# Preencha: usuário, email, senha
python manage.py runserver
```

Acesse `http://127.0.0.1:8000/admin/` e faça login. Você verá os models Autor e Livro prontos para cadastro.

## Checkpoint

:::objetivo Você está no caminho certo se
O servidor Django roda sem erros. No /admin/, você consegue:
- Cadastrar um autor (ex.: "J.K. Rowling")
- Cadastrar um livro associado a esse autor (ex.: "Harry Potter")
- Editar e excluir registros
- Buscar por nome do autor
:::

## Erros comuns

:::atencao Sintoma: django-admin: command not found
Causa: Django não está instalado ou o ambiente virtual não foi
ativado. Correção: instale com pip install django e ative o
ambiente virtual (source .venv/bin/activate no Linux).
:::

:::atencao Sintoma: "No changes detected" ao rodar makemigrations
Causa: o app não foi registrado em INSTALLED_APPS ou o model
não foi definido no arquivo models.py correto.
Correção: verifique se livros está em INSTALLED_APPS e se a
classe model existe em livros/models.py.
:::

## Desafio

Adicione um model `Categoria` com nome e descrição, e relacione-o com Livro (um livro pode ter uma categoria). Registre no admin e crie algumas categorias.

:::importante Desafio extra
Para quem terminar primeiro: crie uma lista de livros visível
em /livros/ usando uma view ListView. Não precisa de template
elaborado — um HttpResponse simples já vale.
:::

## Fechamento

:::resumo
- Django separa projeto (configuração geral) de apps (funcionalidades)
- Models são classes Python que viram tabelas no banco de dados
- Cada campo (CharField, IntegerField, etc.) define o tipo da coluna
- ForeignKey cria relacionamento N:1 entre tabelas
- makemigrations + migrate traduzem models em SQL
- Admin registrado com @admin.register permite CRUD visual
- Próxima aula: Django — views, URLs e templates
:::
