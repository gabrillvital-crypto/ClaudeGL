# Dashboard Gestão de Terceiros — Zurich Airport

**Documentação técnica e operacional**
Elaborado por: Gabriel Vital | Efcaz CS | 26/05/2026
Atualizado: 26/06/2026

---

## 1. O que foi construído e por quê

Dashboard HTML standalone de conformidade documental de terceiros para a Zurich Airport. Abre direto no navegador — sem servidor, sem login, sem instalação.

Gerado a partir de relatórios exportados da plataforma Efcaz via Metabase. O script Python (pandas + plotly) lê os dados, processa e gera o HTML completo com todos os gráficos, tabelas e filtros embutidos.

---

## 2. Arquivos do projeto

| O que é | Caminho |
| --- | --- |
| Script principal | `Dashboard\relatorio_fornecedores_zurich.py` |
| HTML gerado | `Dashboard\relatorio_fornecedores_zurich.html` |
| Pasta de dados | `Dashboard\data\` |
| Documentação | `Dashboard\Dashboard_Zurich_Documentacao.md` |

### De-para — nomes de arquivo (histórico)

| Antes (versão inicial) | Depois (versão atual) |
| --- | --- |
| `dashboard_zurich.py` | `relatorio_fornecedores_zurich.py` |
| `dashboard_zurich_airport.html` | `relatorio_fornecedores_zurich.html` |
| R4 como `.xlsx` | R4 como `.csv` (XLSX mantido como fallback) |
| 4 relatórios Metabase | 6 relatórios Metabase |

---

## 3. Fontes de dados — 6 relatórios Metabase

| Relatório | Conteúdo | Formato | Nome fixo em `data/` |
| --- | --- | --- | --- |
| R1 | Pendências por solicitação | CSV | `pendencias_zurich.csv` |
| R2 | Terceiros cadastrados | CSV | `terceiros_zurich.csv` |
| R3 | Situação documental por terceiro (última solicitação) | CSV | `situacao_terceiro_zurich.csv` |
| R4 | Situação documental por fornecedor/empresa (última solicitação) | CSV | `situacao_fornecedor_zurich.csv` |
| R5 | Relatório de Códigos de Contrato dos Fornecedores | CSV | `codigos_contrato_fornecedores_zurich.csv` |
| R6 | Situação dos Documentos de Busca Automática | CSV | `busca_automatica_zurich.csv` |

> **R5 (desde 16/06/2026):** substituiu o antigo `fornecedores_zurich.csv` (XLS da plataforma). Colunas: `Documento Fornecedor` (CNPJ), `Fornecedor` (razão social), `Contrato 1`..`Contrato 10`, `Filial`. Usado para totais, seção sem execução e drill-down de contratos. ⚠️ `read_csv_safe()` remove colunas "Contrato N" — o bloco de contratos lê este CSV diretamente para preservá-las.
>
> **R6 (desde 26/06/2026):** preenchido pelo robô de busca automática da Efcaz. Campo-chave: `Situação Documento` (REGULAR / NEUTRO / ALERTA / IRREGULAR). Usado no enriquecimento R4 via lookup `CNPJ + Documento`.

### Colunas relevantes por relatório

**R1 — Pendências:**
`Razão Social`, `Situação da solicitação` (EM_ELABORACAO / APROVADO), `Área da pendência` (TERCEIROS / DOCUMENTOS), `Documento`, `Marcas e representações` (competência), `Pendência`

**R2 — Terceiros:**
`Razão Social`, `CPF/CNPJ`, `Código do aeroporto`, `Cargo`, `Status` (Ativo / Inativo), `Código do contrato vinculado`

**R3 — Situação por Terceiro:**
`Fornecedor Razão Social`, `Terceiro Razão Social`, `Terceiro CPF/CNPJ`, `Fornecedor CPF/CNPJ`, `Documento`, `Status`, `Situação Análise Documento`, `Data de Vencimento`

**R4 — Situação por Fornecedor:**
`Razão Social`, `CNPJ`, `Documento`, `Status`, `Situação Análise Documento`, `Data de Vencimento`

**R5 — Códigos de Contrato:**
`Documento Fornecedor` (CNPJ), `Fornecedor`, `Contrato 1`..`Contrato 10`, `Filial`

**R6 — Busca Automática:**
`Razão Social`, `CNPJ`, `Documento`, `Situação Documento` (REGULAR/NEUTRO/ALERTA/IRREGULAR), `Status`, `Situação Análise Documento`

---

## 4. Regra de classificação de conformidade

### R3 — Situação por Terceiro (vigente desde 27/05/2026)

A coluna **"Situação Análise Documento"** tem prioridade absoluta sobre qualquer outra coluna.

| Situação Análise Documento | Status do doc | Classificação final |
| --- | --- | --- |
| APROVADO | (qualquer) | **Aprovado** |
| REPROVADO | (qualquer) | **Reprovado** |
| NÃO ANALISADO ou ausente | Não anexado | **Não Anexado** |
| NÃO ANALISADO ou ausente | A vencer / Vencido / N/A | **Aguardando análise** |

### R4 — Situação Documental da Empresa (atualizado 26/06/2026)

Enriquecimento via busca automática (R6): lookup por chave composta `CNPJ + Documento`.

**Quando o documento está no R6 (busca automática):**

| Situação Documento (robô) | Situação Análise (BPO) | Status final |
| --- | --- | --- |
| REGULAR | qualquer | **Aprovado** |
| IRREGULAR | qualquer | **Irregular** |
| NEUTRO ou ALERTA | APROVADO | **Aprovado** |
| NEUTRO ou ALERTA | REPROVADO | **Reprovado** |
| NEUTRO ou ALERTA | VENCIDO | **Vencido** |
| NEUTRO ou ALERTA | NÃO ANALISADO ou outro | **Em análise** |

> ⚠️ **Regra crítica — NEUTRO/ALERTA:** a coluna `Situação Análise Documento` usada para desempatar é a do **CSV R6 (busca automática)**, não a do CSV R4. Motivo: o React usa a mesma fonte (R6) e os dois dashboards precisam convergir. Se o R4 CSV mostrar APROVADO mas o R6 ainda mostrar NÃO ANALISADO, o documento é classificado como **Em Análise** até o R6 ser atualizado. Nunca trocar esta fonte para o R4 CSV sem realinhar os dois dashboards.

**Quando NÃO está no R6 (documento manual):**

| Situação Análise Documento | Status | Status final |
| --- | --- | --- |
| APROVADO | — | **Aprovado** |
| REPROVADO | — | **Reprovado** |
| outros | contém "vencer" | **Aprovado** |
| outros | contém "anexado" | **Não Anexado** |
| outros | contém "vencido" | **Vencido** |
| outros | demais | **Em análise** |

### De-para — regra antiga vs atual

| Classificação antiga | Classificação atual |
| --- | --- |
| Conforme | Aprovado |
| Vencido | Aguardando análise (R3) / Vencido (R4) |
| Pendente | Não Anexado |
| *(não existia)* | Reprovado |
| *(não existia)* | Irregular — R4 com busca automática IRREGULAR |

---

## 5. Seções do dashboard (estado atual)

### Seções visíveis

| # | Seção | Descrição |
| --- | --- | --- |
| 1 | **Header** | Título e data/hora de geração |
| 2 | **Filtro global** | Barra teal escura — select Fornecedor sincroniza todas as seções interativas |
| 3 | **KPI cards + Pizzas** | Cards de métricas + 2 gráficos de pizza lado a lado (Terceiros / Fornecedores) |
| 4 | **Conformidade Documental** | % NC por fornecedor (fig7) + stacked bar situação (fig8) — *não respondem ao filtro global* |
| 5 | **Terceiros Cadastrados** | Ativos vs Inativos por fornecedor |
| 6 | **Análise Interativa (drill-down)** | Fornecedor → Terceiro → Documentos, navegação por breadcrumb |
| 7 | **Situação Documental por Terceiro** | Tabela R3 com filtros, 7 KPIs próprios, export Excel/PDF/CSV |
| 8 | **Situação Documental da Empresa** | Tabela R4 com filtros, KPIs próprios (incl. Irregular Débito), export Excel/PDF/CSV |
| 9 | **Detalhamento de Pendências** | Tabela R1 com filtros, export Excel/PDF/CSV |
| 10 | **Contratos por Fornecedor** | Drill-down 3 níveis: cards → lista contratos → tabela terceiros. Export em L2 e L3 (desde 26/06/2026) |
| 11 | **Fornecedor sem interação com a plataforma** | Fornecedores do cadastro sem doc em R3 ou R4 (recolhida por padrão) |

### De-para — seções ocultadas (27/05/2026)

| Seção | Motivo |
| --- | --- |
| Alerta de Auditoria | Hardcoded (NEPOS) — ocultado até parametrização via CSV de auditoria |
| Visão Geral de Pendências | Retirada por alinhamento Débora/Ricardo — dado já aparece nos KPIs |
| Status das Solicitações | Retirada por alinhamento |
| Pendências por Área | Retirada por alinhamento |
| Tipos de Documentos | Retirada por alinhamento |

> As seções ocultadas ainda existem no código (comentadas ou `display:none`) e podem ser reativadas se necessário. A versão completa de referência é o `dashboard_zurich_airport.html`.

---

## 6. KPI cards

### Cards da seção principal (topo)

| ID (JS) | Dado | Fonte | Observação |
| --- | --- | --- | --- |
| `kpi-forn` | Fornecedores com pendências | R1 — razão social únicos | |
| `kpi-totpend` | Total de pendências | R1 — total linhas | |
| `kpi-elab` | Pendente não enviado (EM_ELABORACAO) | R1 — status | |
| `kpi-aprov` | Em análise c/ pendências (APROVADO) | R1 — status | |
| `kpi-reprov` | Docs reprovados | R3 — Status_Cat = Reprovado | |
| `kpi-pend` | Docs pendentes (não enviados) | R3 — Não anexado + Aguardando análise | |
| `kpi-conf` | Docs conformes | R3 — Status_Cat = Aprovado | |
| `kpi-pend-terc` | Pendências de Terceiros | R1 — Área = TERCEIROS | |
| `kpi-pend-doc` | Pendências Doc Fornecedor | R1 — Área = DOCUMENTOS | |
| `kpi-terc-ativo` | Terceiros ativos | R2 — Status = Ativo | |
| *(fixo)* | **Total de Fornecedores** | R5 — CNPJs únicos | Conta por CNPJ, não por Razão Social |
| *(fixo)* | **Fornecedores com Execução** | R4 ∪ R3 — CNPJs com ao menos 1 doc | Adicionado em jun/2026 |

### Cards da seção R4 — Situação Documental da Empresa (atualizado 26/06/2026)

| ID (JS) | Dado | Cor |
| --- | --- | --- |
| `r4-kpi-forn` | Fornecedores com Docs | cinza |
| `r4-kpi-nc` | % Não Conformidade | vermelho |
| `r4-kpi-c` | % Conformidade | verde |
| `r4-kpi-aprov` | Docs Aprovados | verde |
| `r4-kpi-reprov` | Docs Reprovados | vermelho |
| `r4-kpi-irregular` | **Irregular** — busca automática IRREGULAR | laranja |
| `r4-kpi-nao-anex` | Não Anexados | amarelo |
| `r4-kpi-em-anal` | Em Análise | laranja claro |
| `r4-kpi-vencido` | Vencidos | vermelho |

### Cards da seção R3 — Situação Documental por Terceiro

| ID (JS) | Dado |
| --- | --- |
| `sit-kpi-nc` | % Não Conformidade Terceiros |
| `sit-kpi-c` | % Conformidade Terceiros |
| `sit-kpi-aprov` | Docs Aprovados |
| `sit-kpi-reprov` | Docs Reprovados |
| `sit-kpi-nao-anex` | Não Anexado |
| `sit-kpi-aguard-sub` | Aguardando Submissão (EM_ELABORACAO) |
| `sit-kpi-aguard-real` | Em Análise (submetido, aguardando BPO) |
| `sit-kpi-terc` | Terceiros com Docs |

> Todos os KPIs das seções R3 e R4 atualizam dinamicamente ao filtrar por fornecedor no select local.

---

## 7. Gráficos de pizza — conformidade

### Configuração atual

Dois gráficos lado a lado, pizza sólida (não donut), sem texto interno, apenas legenda.

| Pizza | Dados | Fatias |
| --- | --- | --- |
| Conformidade Terceiros | R3 (sit_tabela) | Conforme (= Aprovado) / Não Conforme (todo o resto) |
| Conformidade Fornecedores | R4 (forn_sit_tabela) | Conforme (= Aprovado) / Não Conforme (todo o resto) |

Ambos respondem ao filtro global de fornecedor.

### De-para — pizzas

| Antes | Depois |
| --- | --- |
| 1 donut com 4 fatias (Conforme / Vencido / Pendente / Não Analisado) | 2 pizzas sólidas com 2 fatias (Conforme / Não Conforme) |
| Uma pizza única | Pizza de Terceiros + Pizza de Fornecedores separadas |
| Texto percentual dentro da pizza | Sem texto interno — apenas legenda |
| Não respondia ao filtro global | Responde ao filtro global de fornecedor |

> Terminologia obrigatória: **"Conforme"** e **"Não Conforme"** — definida por Ricardo.

---

## 8. Filtro global

**Onde aparece:** barra fixa teal escuro logo abaixo do header, sempre visível.

**O que filtra:** select de fornecedor sincroniza simultaneamente:

- Todos os KPI cards do topo
- 2 pizzas de conformidade
- Drill-down interativo (nível 1 — cards de fornecedor)
- Tabela R3 (Situação Documental por Terceiro)
- Tabela R4 (Situação Documental da Empresa)
- Tabela R1 (Detalhamento de Pendências)

**Quem aparece no dropdown:** apenas fornecedores com ao menos um registro em R1, R3 ou R4. Fornecedores do cadastro sem atividade aparecem na seção 11, não no filtro.

**O que NÃO filtra (estático):**

- Fig7 — % de Não Conformidade por Fornecedor
- Fig8 — Situação Documental por Fornecedor (stacked bar)

> Fig7 e Fig8 mostram sempre a visão geral de todos os fornecedores — são gerados pelo Python no momento do build e não têm interatividade JS.

---

## 9. Fornecedores com razão social duplicada (CNPJ composite key)

Alguns fornecedores têm a mesma razão social com CNPJs diferentes na base. Para evitar ambiguidade nos filtros, o sistema usa um composite key.

**Como funciona:**

1. O Python detecta no build quais razões sociais têm 2+ CNPJs distintos (cruzando R3 e R5) e gera o mapa `FORN_CNPJ_MAP`
2. Nesses casos, o dropdown mostra: `RAZÃO SOCIAL (CNPJ)`
3. O valor interno é `"nome|||cnpj"` — o JS usa `parseFornVal()` para separar nome e CNPJ
4. O filtro aplica ambos: filtra por nome E por CNPJ, garantindo que só os registros daquele CNPJ específico apareçam

**Casos identificados na base atual (jun/2026):**

- KARUANA SERVICOS AUXILIARES DE TRANSPORTE AEREO LTDA — 3 CNPJs distintos
- TOP SERVICE SERVICOS E SISTEMAS S/A — 3 CNPJs distintos

---

## 10. Seção "Contratos por Fornecedor" — drill-down 3 níveis (desde 26/06/2026)

### Fontes

- **R5** (`codigos_contrato_fornecedores_zurich.csv`): colunas `Contrato 1`..`Contrato 10` — lidas diretamente sem `read_csv_safe`
- **R2** (`terceiros_zurich.csv`): coluna `Código do contrato vinculado` — vincula cada terceiro ao(s) seu(s) contrato(s)

### Estrutura dos 3 níveis

| Nível | O que exibe | Interação |
| --- | --- | --- |
| **L1 — Cards** | Todos os fornecedores: nome, nº contratos, nº terceiros, preview das tags de contrato | Busca por nome · Clicar abre L2 |
| **L2 — Contratos** | Lista de contratos do fornecedor com qtd terceiros, ativos e aeroportos | Chips de filtro (quando >1 contrato) · Export Excel/CSV/PDF · Clicar abre L3 |
| **L3 — Terceiros** | Tabela de terceiros do contrato: Nome, CPF/CNPJ, Cargo, Aeroporto, Status | Export Excel/CSV/PDF |

### Regra de contagem dos contratos (L1)

O card usa a união `f.contratos ∪ Object.keys(f.terceiros_by_contract)` — mesma lógica do L2. Garante que o número exibido antes e depois de expandir seja idêntico.

### Export L2 — formato listagem de terceiros

Colunas: `Contrato | Aeroporto | Nome | CPF/CNPJ | Cargo | Status` (uma linha por terceiro).
PDF: título "Terceiros — [FORNECEDOR]" + "X contratos · Y terceiros" alinhado à direita. Status "Ativo" em verde.

---

## 11. Seção "Fornecedor sem interação com a plataforma"

Adicionada em 03/06/2026. Exibe fornecedores presentes no cadastro (R5) que não possuem nenhum documento registrado em R3 (terceiros) ou R4 (corporativo).

**Lógica:**

1. Coleta CNPJs com atividade: união de CNPJs únicos em R4 e R3
2. Cruza com o cadastro R5: quem está no cadastro mas não na união → sem interação com a plataforma
3. Deduplicação por CNPJ para não repetir filiais

**Uso indicado:** revisão periódica com a Débora para confirmar se esses fornecedores são ativos, inativos ou cadastros a remover.

---

## 12. Terminologia — de-para

| Antes | Depois | Onde aparece |
| --- | --- | --- |
| DOCUMENTOS (área) | FORNECEDOR (área) | Filtro de área no Detalhamento + badge na tabela |
| Conforme | Aprovado | Classificação de status |
| Vencido | Aguardando análise | Classificação de status R3 |
| Pendente | Não anexado | Classificação de status |
| Competência em branco | "A classificar" | Coluna Competência no Detalhamento |
| Filtro "Status" no Detalhamento | Removido | Seção Detalhamento de Pendências |
| Total Fornecedores por Razão Social | Total Fornecedores por CNPJ | Card de topo |

---

## 13. Como rodar — modo manual (atual)

### Passo 1 — Exportar os 6 relatórios do Metabase

| Relatório | Nome no Metabase | Formato |
| --- | --- | --- |
| R1 | Pendências por Solicitação com Documento | CSV |
| R2 | Relatório de Terceiros Cadastrados | CSV |
| R3 | Situação de Preenchimento Documental do Terceiro na Última Solicitação | CSV |
| R4 | Situação de Preenchimento Documental na Última Solicitação do Fornecedor | CSV |
| R5 | Relatório de Códigos de Contrato dos Fornecedores | CSV |
| R6 | Situação dos Documentos de Busca Automática | CSV |

### Passo 2 — Salvar com nomes fixos na pasta data/

Salvar os 6 arquivos em `Dashboard\data\` com os nomes exatos da coluna "Nome fixo" da seção 3. Todos são CSV direto — sem conversão necessária.

### Passo 3 — Rodar o script

```
python relatorio_fornecedores_zurich.py
```

### Passo 4 — Abrir o dashboard

O HTML é gerado em `Dashboard\relatorio_fornecedores_zurich.html`. Abrir no Chrome ou Edge.

---

## 14. Automação via N8N (planejada — a ser configurada por Ricardo/João)

```
[Agendador N8N] — 2x por semana (seg e qui, 08h)
    ↓
[6x HTTP Request — API Metabase]
  GET /api/card/{id_R1}/query/csv  →  pendencias_zurich.csv
  GET /api/card/{id_R2}/query/csv  →  terceiros_zurich.csv
  GET /api/card/{id_R3}/query/csv  →  situacao_terceiro_zurich.csv
  GET /api/card/{id_R4}/query/csv  →  situacao_fornecedor_zurich.csv
  GET /api/card/{id_R5}/query/csv  →  codigos_contrato_fornecedores_zurich.csv
  GET /api/card/{id_R6}/query/csv  →  busca_automatica_zurich.csv
    ↓
[Write Binary File × 6]
  Salva em /srv/zurich/data/ com nomes fixos
    ↓
[Execute Command]
  python /srv/zurich/relatorio_fornecedores_zurich.py
    ↓
[Move File / Send Email]
  relatorio_fornecedores_zurich.html → Débora + Claudinha
```

**Status atual (jun/2026):** Servidor Efcaz inacessível (controlado pela AZ). Deploy em andamento via e-mail — João investigando erro no nó `Execute Command`. Ver Cenário C do Guia de Deploy.

**O que Ricardo/João precisam fazer:**

1. Gerar API token no Metabase (Admin → API Keys)
2. Anotar os IDs das 6 questões Metabase
3. Configurar os nós HTTP com `Authorization: Bearer {token}`
4. Nó Execute Command executa o Python com o caminho correto do servidor
5. Atualizar `BASE_DIR` no script para o caminho do servidor (1 linha no topo do script)

---

## 15. Opções de acesso para Débora e Claudinha

| Opção | Como funciona | Requisito |
| --- | --- | --- |
| Endpoint estático (recomendado) | URL fixa no servidor Efcaz — sempre atualizado no F5 | Ricardo configurar nginx/IIS |
| E-mail com HTML anexo (atual) | N8N gera e envia por e-mail a cada atualização | João finalizar fluxo N8N |
| Google Drive for Desktop | Arquivo sincroniza automaticamente — reabrir para ver atualização | App instalado nas máquinas |
| Download manual | Baixar o HTML do Drive a cada atualização | Sem instalação |

---

## 16. Histórico de versões

| Data | Sessão | O que mudou |
| --- | --- | --- |
| 26/05/2026 | 1–4 | Build inicial: R1+R2+R3+R4, KPIs, pizza, drill-down, tabelas, filtro global, seções colapsáveis |
| 27/05/2026 | 5–7 | Nova regra de classificação (Aprovado/Reprovado por coluna Análise), R4 migrado para CSV, seções ocultas por alinhamento Débora/Ricardo, filtro de status removido do Detalhamento, área DOCUMENTOS → FORNECEDOR |
| 27/05/2026 | 8–9 | 2 pizzas sólidas lado a lado, card Total de Fornecedores, KPIs na seção R3, terminologia Conforme/Não Conforme (Ricardo), competência vazia → "A classificar", CNPJ composite key para razão social duplicada |
| 28/05/2026 | 10 | Documentação atualizada com de-paras completos |
| 03/06/2026 | 11 | R5 (cadastro XLS) adicionado como 5ª fonte; seção "Fornecedor sem interação" (21 fornecedores); enriquecimento do FORN_CNPJ_MAP; Top Service atualizado para 3 CNPJs |
| 12/06/2026 | — | Atualização de dados. Total Fornecedores: 57 · Aprovados: 1.343 · Reprovados: 2.275 · Ag. Submissão: 1.279 · Em Análise: 58 · Vencidos: 143 |
| 16/06/2026 | 16 | R5 substituído: `fornecedores_zurich.csv` (XLS) → `codigos_contrato_fornecedores_zurich.csv` (CSV). `read_csv_safe()` dropa colunas "Contrato N". Total Fornecedores: 50 (saneamento oficial). |
| 22/06/2026 | 17 | Atualização de dados. Fornecedores c/ pendências: 20 · Total pendências: 3.845 · Reprovados: 2.187 · Vencidos empresa: 160. |
| 26/06/2026 | 19 | R6 adicionado (`busca_automatica_zurich.csv`). Nova lógica R4 com enriquecimento: matrix REGULAR/IRREGULAR/NEUTRO/ALERTA + lookup CNPJ+Documento. Novo KPI "Irregular (Débito)" — 27 detectados. Nova seção "Contratos por Fornecedor" — drill-down 3 níveis (59 fornecedores, 20 com contratos, 1.134 terceiros). Export L2 reformulado: listagem de terceiros por linha. Contagem de contratos no card L1 corrigida. Overflow de chips nos cards corrigido. |
| 26/06/2026 | 20 | **Alinhamento Python ↔ React (5 correções):** (1) KPI "Não Aprovados" passa a incluir Irregulares (r4_irregular) — era só Reprovados; (2) label "Irregular (Débito)" simplificado para "Irregular"; (3) R3 card "Ag. Análise" desmembrado em dois cards separados: `sit-kpi-aguard-sub` (Ag. Submissão) e `sit-kpi-aguard-real` (Em Análise); (4) regra NEUTRO/ALERTA passa a usar `Situação Análise Documento` do **CSV R6** (busca automática) em vez do CSV R4 — 50 docs afetados (45 Aprovado→Em Análise, 5 Reprovado→Em Análise); (5) função legada `map_status_flex` confirmada como código morto — não chamada em nenhum ponto. |

---

*Script: `relatorio_fornecedores_zurich.py` | HTML: `relatorio_fornecedores_zurich.html` | Gerado com Claude Code — Efcaz CS*
