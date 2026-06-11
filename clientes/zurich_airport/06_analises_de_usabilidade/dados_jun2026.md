# Análise de Usabilidade — Jun/2026
**Fonte:** CSVs exportados do Metabase (03/06/2026)

---

## Snapshot dos dados (03/06/2026)

### Geral

| Indicador | Dado |
|---|---|
| Total de Fornecedores (únicos) | **51** |
| Fornecedores com Execução na Plataforma | **38** |
| Fornecedores com Pendências | 16 |
| Total de Pendências | 2.919 |
| Terceiros Ativos Cadastrados | 1.040 |

### Fornecedores corporativos (R4)

| Indicador | Dado |
|---|---|
| Fornecedores com docs | 38 |
| % Não Conformidade | 74,8% |
| Docs Não Analisados | 767 |
| Docs Reprovados | 1.615 |
| Docs Conformes | 813 |

### Terceiros (R3)

| Status | Dado |
|---|---|
| % Não Conformidade geral | 85,1% |
| Docs Pendentes (não enviados) | 3.042 |
| Em Análise (c/ pendências) | 1.347 |

---

## Comparativo Mai × Jun/2026

| Indicador | Mai/2026 | Jun/2026 | Δ |
|---|---|---|---|
| Total Fornecedores | 53 | 51 | -2 |
| Com Execução | 37 | 38 | +1 |
| Com Pendências | 14 | 16 | +2 |
| Total Pendências | 1.276 | 2.919 | +1.643 |
| Fornecedores R4 c/ docs | 33 | 38 | +5 |

> O salto em pendências (1.276 → 2.919) reflete base de dados mais completa no export de jun/2026, não necessariamente deterioração — confirmar com Débora.

---

## Fornecedores com CNPJs duplicados detectados

| Razão Social | CNPJs distintos |
|---|---|
| KARUANA SERVICOS AUXILIARES DE TRANSPORT... | 3 CNPJs |
| TOP SERVICE SERVICOS E SISTEMAS | 3 CNPJs |

---

## Limitações conhecidas dos dados

- **Filtro de competência:** não existe vínculo documento×competência no BD para docs aprovados — limitação do produto
- **Histórico mês a mês:** CSVs só trazem snapshot atual, sem séries históricas
- **Competência vazia:** exibida como "A classificar" no dashboard

---

## Destaque

Auditoria formal da NEPOS SISTEMAS retornou **REPROVADA** (Vix, mar/2026) — card de alerta incluído no dashboard.
