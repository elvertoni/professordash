# Aula 05 — Manipulação de arquivos e exceções

Seu programa pode processar dados que estão dentro do código, mas a coisa fica interessante quando ele lê dados de arquivos externos — planilhas CSV, arquivos JSON, logs de sistema. Nesta aula prática, você vai aprender a ler e escrever arquivos CSV e JSON, além de tratar erros que podem acontecer durante essas operações usando try/except. Vamos construir um sistema de cadastro de alunos que salva e carrega dados de um arquivo.

## O que vamos construir

Um sistema de cadastro de alunos que roda no terminal: o usuário adiciona alunos (nome, idade, curso) e os dados são salvos em um arquivo CSV. Ao reiniciar o programa, os alunos cadastrados anteriormente são carregados automaticamente.

:::objetivo Resultado final
Um script Python que gerencia uma lista de alunos persistente
em arquivo CSV. O programa lê os dados existentes ao iniciar,
permite adicionar novos e salva automaticamente.
:::

## Pré-requisitos

:::dica Para esta aula você precisa de
Python 3 instalado, editor de código, terminal. Conhecimento de
listas, dicionários, funções e loops. Um arquivo .py em branco.
:::

## Passo a passo

1. **Criar a estrutura de dados e o menu** — Comece com um dicionário vazio e loop de opções.

```python
import csv
import os

ARQUIVO = "alunos.csv"
alunos = []

def exibir_menu():
    print("\n=== Cadastro de Alunos ===")
    print("1. Listar alunos")
    print("2. Adicionar aluno")
    print("3. Remover aluno")
    print("4. Sair")
    return input("Escolha: ")

while True:
    opcao = exibir_menu()
    if opcao == "4":
        print("Encerrando...")
        break
```

2. **Ler dados do CSV ao iniciar** — Use o módulo csv e trate o caso do arquivo não existir.

```python
def carregar_dados():
    if not os.path.exists(ARQUIVO):
        print("Arquivo não encontrado. Iniciando com lista vazia.")
        return []
    
    with open(ARQUIVO, "r", encoding="utf-8") as arquivo:
        leitor = csv.DictReader(arquivo)
        return list(leitor)

alunos = carregar_dados()
```

`csv.DictReader` lê o CSV e transforma cada linha em um dicionário, usando a primeira linha como nome das chaves. O `with` garante que o arquivo seja fechado automaticamente.

3. **Salvar dados no CSV** — Escreva a lista de dicionários de volta no arquivo.

```python
def salvar_dados():
    if not alunos:
        return
    
    with open(ARQUIVO, "w", encoding="utf-8", newline="") as arquivo:
        cabecalho = ["nome", "idade", "curso"]
        escritor = csv.DictWriter(arquivo, fieldnames=cabecalho)
        escritor.writeheader()
        escritor.writerows(alunos)
```

4. **Adicionar e listar alunos** — Funções básicas de CRUD.

```python
def listar_alunos():
    if not alunos:
        print("Nenhum aluno cadastrado.")
        return
    print("\nAlunos cadastrados:")
    for i, aluno in enumerate(alunos, 1):
        print(f"{i}. {aluno['nome']} | {aluno['idade']} anos | {aluno['curso']}")

def adicionar_aluno():
    nome = input("Nome: ")
    idade = input("Idade: ")
    curso = input("Curso: ")
    alunos.append({"nome": nome, "idade": idade, "curso": curso})
    salvar_dados()
    print(f"Aluno {nome} cadastrado com sucesso!")
```

5. **Tratar erros com try/except** — Arquivos podem falhar por muitos motivos.

```python
def carregar_dados_seguro():
    try:
        return carregar_dados()
    except FileNotFoundError:
        print("Arquivo não encontrado. Começando do zero.")
        return []
    except PermissionError:
        print("Erro: sem permissão para ler o arquivo.")
        return []
    except csv.Error as e:
        print(f"Erro ao ler CSV: {e}")
        return []
```

:::exemplo Try/except/else/finally
```python
try:
    arquivo = open("dados.txt", "r")
    conteudo = arquivo.read()
except FileNotFoundError:
    print("Arquivo não existe.")
else:
    print("Arquivo lido com sucesso!")
    print(conteudo)
finally:
    # Roda sempre, com ou sem erro
    if 'arquivo' in locals():
        arquivo.close()
```
:::

6. **Criar o main loop completo** — Integre tudo.

```python
def main():
    global alunos
    alunos = carregar_dados_seguro()
    
    while True:
        opcao = exibir_menu()
        
        if opcao == "1":
            listar_alunos()
        elif opcao == "2":
            adicionar_aluno()
        elif opcao == "3":
            remover_aluno()
        elif opcao == "4":
            print("Dados salvos. Até mais!")
            break
        else:
            print("Opção inválida.")

if __name__ == "__main__":
    main()
```

## Checkpoint

:::objetivo Você está no caminho certo se
Ao executar o programa, adicionar alguns alunos e sair, um arquivo
alunos.csv é criado com os dados. Ao executar novamente, os alunos
aparecem listados sem precisar cadastrar de novo.
:::

## Erros comuns

:::atencao Sintoma: o CSV fica com linhas em branco entre os registros
Causa: no Windows, o open precisa de newline="" para evitar linhas
extras. Correção: adicione newline="" na abertura do arquivo para
escrita: open(ARQUIVO, "w", newline="").
:::

:::atencao Sintoma: erro de codificação com caracteres acentuados
Causa: o Python está usando encoding padrão do sistema, que pode
não ser UTF-8. Correção: sempre use encoding="utf-8" ao abrir
arquivos com texto em português.
:::

## Desafio

Adicione uma função `exportar_json()` que lê o CSV e cria um arquivo `alunos.json` com os mesmos dados no formato JSON.

:::importante Desafio extra
Para quem terminar primeiro: adicione validação para impedir
cadastro de alunos com nome vazio ou idade que não seja número.
Use try/except para converter a idade e exibir mensagem clara
de erro se o valor for inválido.
:::

## Código completo

```python
import csv
import os
import json

ARQUIVO_CSV = "alunos.csv"
alunos = []

def carregar_dados():
    with open(ARQUIVO_CSV, "r", encoding="utf-8") as arquivo:
        leitor = csv.DictReader(arquivo)
        return list(leitor)

def carregar_dados_seguro():
    try:
        return carregar_dados()
    except FileNotFoundError:
        return []
    except PermissionError:
        print("Sem permissão para ler o arquivo.")
        return []
    except csv.Error as e:
        print(f"Erro no CSV: {e}")
        return []

def salvar_dados():
    with open(ARQUIVO_CSV, "w", encoding="utf-8", newline="") as arquivo:
        cabecalho = ["nome", "idade", "curso"]
        escritor = csv.DictWriter(arquivo, fieldnames=cabecalho)
        escritor.writeheader()
        escritor.writerows(alunos)

def listar_alunos():
    if not alunos:
        print("Nenhum aluno cadastrado.")
        return
    print("\nAlunos cadastrados:")
    for i, aluno in enumerate(alunos, 1):
        print(f"{i}. {aluno['nome']} | {aluno['idade']} anos | {aluno['curso']}")

def adicionar_aluno():
    nome = input("Nome: ").strip()
    if not nome:
        print("Nome não pode ser vazio.")
        return
    idade = input("Idade: ").strip()
    if not idade.isdigit():
        print("Idade deve ser um número.")
        return
    curso = input("Curso: ").strip()
    alunos.append({"nome": nome, "idade": idade, "curso": curso})
    salvar_dados()
    print(f"Aluno {nome} cadastrado com sucesso!")

def remover_aluno():
    listar_alunos()
    if not alunos:
        return
    try:
        idx = int(input("Número do aluno para remover: ")) - 1
        removido = alunos.pop(idx)
        salvar_dados()
        print(f"Aluno {removido['nome']} removido.")
    except (ValueError, IndexError):
        print("Número inválido.")

def exportar_json():
    with open("alunos.json", "w", encoding="utf-8") as arquivo:
        json.dump(alunos, arquivo, ensure_ascii=False, indent=2)
    print("Dados exportados para alunos.json")

def exibir_menu():
    print("\n=== Cadastro de Alunos ===")
    print("1. Listar alunos")
    print("2. Adicionar aluno")
    print("3. Remover aluno")
    print("4. Exportar JSON")
    print("5. Sair")
    return input("Escolha: ")

def main():
    global alunos
    alunos = carregar_dados_seguro()
    
    while True:
        opcao = exibir_menu()
        if opcao == "1":
            listar_alunos()
        elif opcao == "2":
            adicionar_aluno()
        elif opcao == "3":
            remover_aluno()
        elif opcao == "4":
            exportar_json()
        elif opcao == "5":
            print("Dados salvos. Até mais!")
            break
        else:
            print("Opção inválida.")

if __name__ == "__main__":
    main()
```

## Fechamento

:::resumo
- open() com with gerencia arquivos de forma segura (fecha automaticamente)
- csv.DictReader e csv.DictWriter trabalham com dicionários e CSV
- encoding="utf-8" é obrigatório para caracteres acentuados
- try/except captura e trata erros sem travar o programa
- else roda quando não há erro; finally roda sempre
- Próxima aula: introdução à orientação a objetos
:::
