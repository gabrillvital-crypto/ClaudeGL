# Jornada Ongoing — Zurich Airport
**Atualizado em:** 02/06/2026

---

## Perfil do cliente

| Campo | Dado |
|---|---|
| **Cliente** | Zurich Airport |
| **Segmento** | Gestão aeroportuária / BPO de terceiros |
| **Particularidade** | Cliente com dashboard BI customizado — caso de customização avançada |

---

## Contatos

| Nome | Papel |
|---|---|
| **Débora** | Gestora — usuária principal do dashboard |
| **Claudinha** | Gestora — também acessa o dashboard |

---

## Módulos / Serviços contratados

| Serviço | Detalhe |
|---|---|
| Gestão de Terceiros (BPO) | Efcaz gere documentos de prestadores de serviço nos aeroportos |
| Dashboard BI customizado | HTML interativo com drill-down, tabelas e filtros — entregue por Gabriel |

---

## Situação da conta (mai/2026)

| Indicador | Dado |
|---|---|
| Fornecedores com pendências | 14 |
| Terceiros ativos | 1.040 |
| % Não conformidade geral (R3) | ~90% |
| Docs Aprovados | 512 (9,5%) |
| Docs Reprovados | 1.003 |
| Docs Não Analisados / Pendentes | 3.885 |

---

## Marcos da jornada

| Data | Marco |
|---|---|
| 22/05/2026 | Reunião de ajustes — dashboard aprovado internamente como prova de conceito |
| 22/05/2026 | Dados exportados do Metabase (4 CSVs) |
| 26–27/05/2026 | Múltiplas sessões de desenvolvimento — dashboard evoluído (sessões 3–7) |
| 28/05/2026 | Sessões 8–10 — gráficos de pizza, KPIs R3, correções de filtro e dedup |
| 29/05/2026 | Apresentação para Débora às 16h |

---

## Customização técnica entregue

- **Dashboard interativo HTML** (standalone — abre no Chrome sem servidor)
- Drill-down 3 níveis: fornecedor → terceiros → documentos
- Filtro global por fornecedor com sincronização em todos os gráficos
- Export CSV, XLSX e PDF por seção
- Tratamento de CNPJs duplicados (Caruana, Top Service)
- Seção R4 (documentação corporativa dos fornecedores)

---

## Status do deploy

**Bloqueio de governança identificado:** servidor Efcaz gerenciado pela AZ (holding) — sem acesso para time de produto ou CS.

**Alternativa em exploração:** envio do HTML por e-mail via N8N (João trabalhando nisso).

---

## Oportunidade de produto

O dashboard Zurich pode ser replicado para outros clientes como produto Efcaz. Ver memória: `produto_bi_carteira.md`.
