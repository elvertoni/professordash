# Decisão: Webhook Reverso Notion → ProfessorDash (S4.6 OPC)

**Status:** ❌ NÃO IMPLEMENTADO (adiado)

## Contexto

S4.6 do PRD_REFATORACAO.md propõe um webhook reverso onde, quando o Toni atualiza uma página no Notion marcada com um trigger específico, o ProfessorDash importa automaticamente o conteúdo como uma nova aula.

## Análise

### Motivos para não implementar agora

1. **Esforço significativo.** O webhook Notion exige:
   - Uma rota pública no ProfessorDash para receber POST do Notion
   - Autenticação via segredo compartilhado (Notion webhook secret)
   - Parsing do payload do Notion API (que difere do Markdown canônico)
   - Mapeamento de propriedades do Notion para os campos do model Aula
   - Tratamento de idempotência (evitar duplicatas)

2. **Baixo valor imediato.** O fluxo atual (Hermes Agent gera .md local, importa via CLI/API) já cobre o caso de uso com menos complexidade. O Hermes pode ler do Notion e submeter ao ProfessorDash — a tradução fica no agente, não no servidor.

3. **Manutenção.** O webhook Notion adiciona um ponto de falha externo (disponibilidade da API Notion, rate limits, mudanças no schema do webhook) sem benefício proporcional ao estágio atual do projeto.

### Fluxo alternativo recomendado

```
Toni edita Notion
    ↓
Hermes Agent lê a página do Notion via API
    ↓
Hermes converte para Markdown canônico (FORMATO_AULAS.md)
    ↓
Hermes chama POST /turmas/<id>/aulas/importar/ (via hermes_importar.sh ou API)
    ↓
ProfessorDash valida e persiste a aula
```

Este fluxo mantém a lógica de conversão e validação centralizada no Hermes/CLI, sem expor um endpoint público adicional no ProfessorDash.

## Decisão

**Não implementar webhook Notion neste ciclo.** Reavaliar quando:
- O número de aulas importadas por semana ultrapassar 20
- Houver demanda explícita do Toni por automação Notion→Dashboard
- A equipe tiver capacidade para implementar e manter o webhook

## Alternativa futura

Se implementado, usar:
- Endpoint: `POST /api/webhook/notion/` (com secret validation)
- Formato: Receber page_id do Notion, buscar conteúdo via Notion API, converter Markdown
- Segurança: HMAC signature verification + rate limiting
