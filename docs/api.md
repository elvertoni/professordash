# API de Importação de Aulas — ProfessorDash v2.0

O ProfessorDash disponibiliza uma API simples para importação de aulas em formato Markdown (`.md`).
Esta API foi projetada para integração direta com agentes como o Hermes Agent ou Claude Desktop.

---

## 🔑 Autenticação

A autenticação é feita via Token de API no cabeçalho HTTP de todas as requisições:

```http
Authorization: Token <sua_chave_de_api>
```

Os tokens são vinculados a um usuário professor do sistema e podem ser gerenciados através do Django Admin na seção **Tokens de API**.

---

## 🔌 Endpoint: Importar Aula

### Detalhes do Endpoint

- **URL:** `/turmas/<turma_id>/aulas/importar/`
- **Método:** `POST`
- **Content-Type:** `multipart/form-data`

### Parâmetros da Requisição

| Parâmetro | Tipo | Localização | Descrição |
|---|---|---|---|
| `turma_id` | `inteiro` | URL | O ID correspondente à turma no banco de dados. |
| `arquivo` | `file` | Form-Data | O arquivo Markdown (`.md`) a ser importado. |

---

## 📤 Exemplos de Uso

### 1. Chamada via `curl`

```bash
curl -X POST http://localhost:8000/turmas/1/aulas/importar/ \
  -H "Authorization: Token 9a8b7c6d5e4f3g2h1i0j" \
  -H "Accept: application/json" \
  -F "arquivo=@aula-07.md"
```

### 2. Chamada via Python (biblioteca `requests`)

```python
import requests

url = "http://localhost:8000/turmas/1/aulas/importar/"
token = "9a8b7c6d5e4f3g2h1i0j"
caminho_arquivo = "aula-07.md"

headers = {
    "Authorization": f"Token {token}",
    "Accept": "application/json"
}

with open(caminho_arquivo, "rb") as f:
    files = {"arquivo": f}
    response = requests.post(url, headers=headers, files=files)

print(response.status_code)
print(response.json())
```

### 3. Chamada via Script Wrapper (`hermes_importar.sh`)

O script wrapper [hermes_importar.sh](file:///C:/Users/coimb/Desktop/professordash/scripts/hermes_importar.sh) automatiza esta chamada para o agente Hermes:

```bash
# Exportar variáveis de ambiente necessárias
export PROFESSORDASH_URL="http://localhost:8000"
export PROFESSORDASH_TOKEN="9a8b7c6d5e4f3g2h1i0j"

# Executar script
./scripts/hermes_importar.sh aula-07.md 1
```

---

## 📥 Respostas da API

### Sucesso (`201 Created`)

Retornará detalhes do registro criado:

```json
{
  "success": true,
  "aula_id": 42,
  "titulo": "Aula 07 — Persistência com localStorage",
  "url": "http://localhost:8000/painel/turmas/1/aulas/42/"
}
```

### Falha na Autenticação (`401 Unauthorized`)

Retornado se o token for inválido ou omitido:

```json
{
  "error": "Token de API inválido."
}
```

### Erro de Validação de Formato (`400 Bad Request`)

O validador interno analisa o Markdown contra o `FORMATO_AULAS.md`. Se houver violações graves (como título H1 em falta ou erros estruturais em questões interativas), a requisição é rejeitada:

```json
{
  "error": "Erro de validação de Markdown.",
  "details": [
    "Deve haver exatamente um título H1 ('# Título'). Encontrados: 0.",
    "Questão 1: Deve conter exatamente uma alternativa correta demarcada com '*' no final. Encontradas: 0."
  ]
}
```
