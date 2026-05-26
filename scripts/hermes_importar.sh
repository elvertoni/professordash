#!/bin/bash
# ==============================================================================
#  hermes_importar.sh — Script para envio automático de aulas ao ProfessorDash
#  Uso: ./hermes_importar.sh <arquivo.md> <turma_id>
# ==============================================================================

set -e

# Configurações padrão (podem ser sobrescritas por variáveis de ambiente)
DASHBOARD_URL="${PROFESSORDASH_URL:-http://localhost:8000}"
API_TOKEN="${PROFESSORDASH_TOKEN}"

# Validação de argumentos
ARQUIVO="$1"
TURMA_ID="$2"

if [ -z "$ARQUIVO" ] || [ -z "$TURMA_ID" ]; then
    echo "Erro: Argumentos insuficientes."
    echo "Uso: $0 <arquivo.md> <turma_id>"
    exit 1
fi

if [ ! -f "$ARQUIVO" ]; then
    echo "Erro: Arquivo '$ARQUIVO' não encontrado."
    exit 1
fi

if [ -z "$API_TOKEN" ]; then
    echo "Erro: Variável de ambiente PROFESSORDASH_TOKEN não definida."
    exit 1
fi

echo "Enviando '$ARQUIVO' para a turma ID $TURMA_ID em $DASHBOARD_URL..."

# Enviar via curl
RESPONSE=$(curl -s -w "\n%{http_code}" \
  -H "Authorization: Token $API_TOKEN" \
  -H "Accept: application/json" \
  -F "arquivo=@$ARQUIVO" \
  "$DASHBOARD_URL/turmas/$TURMA_ID/aulas/importar/")

# Separar corpo do status HTTP
HTTP_STATUS=$(echo "$RESPONSE" | tail -n 1)
HTTP_BODY=$(echo "$RESPONSE" | head -n -1)

if [ "$HTTP_STATUS" -eq 201 ] || [ "$HTTP_STATUS" -eq 200 ]; then
    echo "Sucesso! Código HTTP: $HTTP_STATUS"
    echo "Detalhes da importação:"
    echo "$HTTP_BODY"
else
    echo "Erro durante a importação (Código HTTP: $HTTP_STATUS)"
    echo "Detalhes do erro:"
    echo "$HTTP_BODY"
    exit 1
fi
