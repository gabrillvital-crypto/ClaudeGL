# Regras de Negócio — Dashboard Zurich Airport
> Fonte canônica: `Dashboard/relatorio_fornecedores_zurich.py`
> Atualizado em: 11/06/2026

---

## 1. Fontes de Dados

| Arquivo CSV | Conteúdo |
|---|---|
| `fornecedores_zurich.csv` | Cadastro geral dos fornecedores (CNPJ, Razão Social, dados cadastrais) |
| `terceiros_zurich.csv` | Colaboradores/terceiros vinculados a cada fornecedor (Status: Ativo/Inativo) |
| `situacao_terceiro_zurich.csv` | Situação documental dos **terceiros** — R3 |
| `situacao_fornecedor_zurich.csv` | Situação documental das **empresas fornecedoras** — R4 |
| `pendencias_zurich.csv` | Pendências abertas por fornecedor (terceiros e documentação corporativa) |

---

## 2. Mapeamento de Status — R3 (Terceiros)

> **Regra atualizada em 27/05/2026 — Coluna `Situação Análise Documento` tem precedência absoluta.**

A função `map_status_r3` aplica a seguinte lógica **em cascata**:

### Passo 1 — `Situação Análise Documento` (mandatório, sem fallback)
| Valor | Status de Saída |
|---|---|
| `APROVADO` | **Aprovado** |
| `REPROVADO` | **Reprovado** |
| `NÃO ANALISADO` ou ausente | → vai para Passo 2 |

### Passo 2 — Coluna `Status` do documento
| Valor em `Status` | Status de Saída |
|---|---|
| Contém "anexado" (ex: `Não anexado`) | **Não anexado** |
| `A vencer` | **Aguardando análise** |
| `Vencido` | **Aguardando análise** ⚠️ (vencido R3 NÃO vira "Vencido" — entra em Aguardando análise) |
| `N/A` ou vazio (NaN) | **Aguardando análise** |

### Passo 3 — Split de "Aguardando análise" por `Situação Última Solicitação`
| Valor | Status Final Exibível |
|---|---|
| `EM_ELABORACAO` | **Aguardando Submissão** — fornecedor abriu a solicitação mas não clicou em "submeter" |
| Qualquer outro (ex: `APROVADO`) | **Em Análise** — documento submetido, aguardando validação da equipe |

### Resumo dos 5 status R3
| Status | Cor | Significado |
|---|---|---|
| **Aprovado** | Verde | Analisado e validado com sucesso |
| **Reprovado** | Vermelho | Recusado na análise por inconformidade |
| **Não anexado** | Amarelo | Documento obrigatório ainda não enviado |
| **Aguardando Submissão** | Laranja claro | Inserido mas não submetido (EM_ELABORACAO) |
| **Em Análise** | Laranja | Submetido, aguardando validação da equipe |

### Conformidade R3
- **Conforme** = `Status === "Aprovado"`
- **Não Conforme** = todos os demais (Reprovado + Não anexado + Aguardando Submissão + Em Análise)

---

## 3. Mapeamento de Status — R4 (Empresa/Fornecedor)

A função `map_status_r4` usa a coluna `Situação Análise Documento` quando disponível:

| `Situação Análise Documento` | `Status` | Status de Saída |
|---|---|---|
| `APROVADO` | qualquer | **Aprovado** |
| `REPROVADO` | qualquer | **Reprovado** |
| `NÃO ANALISADO` | `A vencer` | **Aprovado** ⚠️ (busca automática válida = equivale a aprovado) |
| `NÃO ANALISADO` | `Não anexado` | **Não Anexado** |
| `NÃO ANALISADO` | `Vencido` | **Vencido** ⚠️ (só R4 tem "Vencido" como status separado) |
| `NÃO ANALISADO` | demais | **Em análise** |

### Resumo dos status R4
| Status | Cor | Significado |
|---|---|---|
| **Aprovado** | Verde | Analisado e aprovado (ou busca automática A vencer) |
| **Reprovado** | Vermelho | Recusado na análise |
| **Não Anexado** | Amarelo | Documento não enviado |
| **Em análise** | Laranja | Aguardando validação |
| **Vencido** | Vermelho | Documento com prazo expirado sem revisão |

### Conformidade R4
- **Conforme** = `Status === "Aprovado"`
- **Não Conforme** = Reprovado + Não Anexado + Em análise + Vencido

---

## 4. Diferença crítica: Vencido em R3 vs R4

| Situação | R3 (Terceiros) | R4 (Empresa) |
|---|---|---|
| Documento com `Status = Vencido` | → entra em "Aguardando análise" → depois "Aguardando Submissão" ou "Em Análise" | → vira **"Vencido"** (status próprio) |

**No R3 não existe "Vencido" como status de saída.** Documentos vencidos de terceiros são tratados como "Aguardando análise" e seu status final depende da `Situação Última Solicitação`.

---

## 5. KPIs — Cálculo de Cada Card

| KPI | Fórmula | Fonte |
|---|---|---|
| **Total de Fornecedores** | `fornecedores_zurich.csv` → CNPJs únicos | Cadastro geral |
| **Fornecedores com Execução** | Total cadastro − Sem execução | CNPJs que aparecem em R3 ou R4 |
| **Docs Esperados Fornecedor** | Total de linhas válidas R4 | `situacao_fornecedor_zurich.csv` |
| **Docs Esperados Terceiros** | Total de linhas válidas R3 | `situacao_terceiro_zurich.csv` |
| **Documentos Aprovados** | R3 Aprovado + R4 Aprovado | R3 + R4 |
| **Documentos Reprovados** | R3 Reprovado + R4 Reprovado | R3 + R4 |
| **Documentos Não Enviados** | R3 Não Anexado + R4 Não Anexado | R3 + R4 |
| **Aguardando Submissão** | R3 EM_ELABORACAO dentro de "Aguardando análise" | **Somente R3** |
| **Em Análise** | R3 Em Análise + R4 Em análise | R3 + R4 |
| **Documentos Vencidos** | R4 Vencido | **Somente R4** |

### Comportamento dos KPIs globais (somem com filtro)
- "Total de Fornecedores" e "Fornecedores com Execução" somem quando um fornecedor específico é selecionado no filtro global
- Os demais 8 cards atualizam dinamicamente conforme o filtro

---

## 6. Donuts de Conformidade

Três donuts exibidos lado a lado:

| Donut | Conforme | Não Conforme |
|---|---|---|
| **Conformidade Fornecedores** | R4 Aprovado | R4 todos os demais |
| **Conformidade Geral** ★ | R3 Aprovado + R4 Aprovado | Todos os não-aprovados de R3 + R4 |
| **Conformidade Terceiros** | R3 Aprovado | R3 todos os demais |

A fórmula do percentual no centro do donut:
```
% Conforme = Aprovados / Total × 100
```

---

## 7. Fornecedores sem Execução

Fornecedores que constam no cadastro (`fornecedores_zurich.csv`) mas **não aparecem em nenhum documento** de R3 ou R4.

Critério: CNPJ do cadastro normalizado NÃO está no conjunto de CNPJs de fornecedores com execução (união de CNPJs R3 + CNPJs R4).

---

## 8. Tabela de Pendências

Fonte: `pendencias_zurich.csv`

| Coluna | Significado |
|---|---|
| `Situação da solicitação` | `EM_ELABORACAO` = pendente (não enviado) / `APROVADO` = em análise com pendências |
| `Área da pendência` | `TERCEIROS` = pendência de terceiros / `DOCUMENTOS` = pendência corporativa |
| `Marcas e representações` | Competência (mês/ano de referência) |
| `Pendência` | Detalhe textual da pendência |

Filtros disponíveis: Fornecedor (multi-select), Área, Competência, Busca textual.

---

## 9. Abreviação de Nomes (`abbrev`)

Nomes de fornecedores são truncados a **40 caracteres** com remoção de sufixos jurídicos:
- Sufixos removidos: `LTDA`, `LTDA.`, `S/A`, `SA`, `EIRELI`, `ME`, `EPP`
- Nomes maiores que 40 chars recebem `...`

---

## 10. Normalização de CNPJ (`normCNPJ`)

1. Remove `.0` pandas (ex: `20845454000170.0` → `20845454000170`)
2. Remove pontos, traços e barras
3. Se resultado for só dígitos com menos de 14 chars → preenche com zeros à esquerda (`zfill(14)`)

---

## 11. Não Conformidade por Empresa (Gráfico de barras R3)

Para cada fornecedor no R3:
```
Total = Aprovado + Reprovado + Não anexado + Aguardando análise
Não Conforme = Reprovado + Não anexado + Aguardando análise
% NC = Não Conforme / Total × 100
```

Cores das barras: Verde ≤ 30% / Amarelo 31–60% / Vermelho > 60%

---

## 12. Filtro Global

- Multi-select por fornecedor com CNPJ exibido quando há filiais (mesmo nome, CNPJs diferentes)
- Quando ativo: atualiza KPIs + donuts + todas as tabelas em simultâneo
- Não afeta os 2 KPIs globais (Total Fornecedores e Com Execução) — esses somem

---

## Alertas de Divergência Conhecidos

- **Vencido R3**: não gera card próprio — entra em "Aguardando análise" e some no split Submissão/Análise
- **R4 A vencer + NÃO ANALISADO**: tratado como **Aprovado** (busca automática ainda válida)
- **Fornecedores com mesmo nome e CNPJs diferentes**: exibidos separadamente no dropdown com CNPJ entre parênteses
