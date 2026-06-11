# Customização — Dashboard BI de Gestão de Terceiros
**Entregue em:** 29/05/2026
**Tipo:** Dashboard HTML interativo standalone

---

## Arquivos

| Arquivo | Caminho | Descrição |
|---|---|---|
| Script original | `Dashboard\dashboard_zurich.py` | Referência — não alterar |
| Script relatório Débora | `Dashboard\relatorio_fornecedores_zurich.py` | Versão reduzida para a cliente |
| HTML original | `Dashboard\dashboard_zurich_airport.html` | Completo |
| HTML para Débora | `Dashboard\relatorio_fornecedores_zurich.html` | Versão entregue |
| Documentação | `Dashboard\Dashboard_Zurich_Documentacao.md` | |
| Dados | `Dashboard\data\` | 4 CSVs com nomes fixos |

**Pasta base:** `C:\Users\gabriel.evangelista\Documents\ClaudeGL\Dashboard\`

---

## Fontes de dados

| Arquivo | Descrição |
|---|---|
| `pendencias_zurich.csv` (R1) | Pendências por solicitação |
| `terceiros_zurich.csv` (R2) | Terceiros cadastrados por empresa/aeroporto |
| `situacao_terceiro_zurich.csv` (R3) | Situação documental por terceiro |
| `situacao_fornecedor_zurich.csv` (R4) | Situação documental corporativa dos fornecedores |

**Para atualizar:** copiar novos CSVs para `data/` com os nomes fixos → `python relatorio_fornecedores_zurich.py`

---

## O que o dashboard entrega

### KPI Cards (12 cards globais)
Fornecedores com pendências, Total pendências, % Não Conformidade, Docs Vencidos, Docs Pendentes, Docs Conformes, Pend. Terceiros, Pend. Doc. Fornecedor, Terceiros Ativos, Total Fornecedores

### Gráficos
- Pizza: Conforme vs. Não Conforme (terceiros + fornecedores)
- Barras: pendências por fornecedor, documentos por tipo, % NC por fornecedor
- Status por fornecedor (stacked)

### Drill-down interativo (3 níveis)
1. Cards por fornecedor com % não conformidade
2. Lista de terceiros com badges de status
3. Documentos do terceiro com status e data de vencimento

### Tabelas interativas
- Situação documental por trabalhador (R3): filtros + export CSV/XLSX/PDF
- Detalhamento das pendências (R1): filtros + export CSV/XLSX/PDF
- Situação documental por fornecedor (R4): filtros + export

---

## Lógica de status R3 (decisão final)

| Situação Análise Documento | Status exibido |
|---|---|
| APROVADO | Aprovado |
| REPROVADO | Reprovado |
| NÃO ANALISADO / ausente + Não anexado | Não anexado |
| NÃO ANALISADO / ausente + A vencer ou Vencido | Aguardando análise |

---

## Pendências abertas

| # | Item | Status |
|---|---|---|
| P5 | Subtítulo nos gráficos estáticos (fig7, fig8) — "Visão geral — todos os fornecedores" | ⏳ |
| Pizza 4 fatias (Thaís) | Aguarda planilha Ricardo com Aprovado/Reprovado | ⏳ |
| Deploy | Fluxo N8N por e-mail (João) | ⏳ |

---

## Deploy

**Situação:** Servidor Efcaz inacessível (AZ controla). Alternativa: e-mail via N8N.

**Proposta:** N8N extrai CSVs do Metabase → roda Python → lê HTML → envia para Débora e Claudinha como anexo.

**Próximo passo:** João compartilhar erro exato do nó `Execute Command` para diagnóstico.
