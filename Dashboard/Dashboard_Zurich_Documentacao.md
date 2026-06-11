# Dashboard Gestão de Terceiros — Zurich Airport
**Documentação técnica e operacional**
Elaborado por: Gabriel Vital | Efcaz CS | 26/05/2026
Atualizado: 03/06/2026 (sessão 11 — novos dados jun/2026, novos cards, seção sem interação com a plataforma)

---

## 1. O que foi construído e por quê

Dashboard HTML standalone de conformidade documental de terceiros para a Zurich Airport. Abre direto no navegador — sem servidor, sem login, sem instalação.

Gerado a partir de 5 relatórios exportados da plataforma Efcaz via Metabase. O script Python (pandas + plotly) lê os dados, processa e gera o HTML completo com todos os gráficos, tabelas e filtros embutidos.

---

## 2. Arquivos do projeto

| O que é | Caminho |
|---|---|
| Script principal | `Dashboard\relatorio_fornecedores_zurich.py` |
| HTML gerado | `Dashboard\relatorio_fornecedores_zurich.html` |
| Pasta de dados | `Dashboard\data\` |
| Documentação | `Dashboard\Dashboard_Zurich_Documentacao.md` |

### De-para — nomes de arquivo (histórico)

| Antes (versão inicial) | Depois (versão atual) |
|---|---|
| `dashboard_zurich.py` | `relatorio_fornecedores_zurich.py` |
| `dashboard_zurich_airport.html` | `relatorio_fornecedores_zurich.html` |
| R4 como `.xlsx` | R4 como `.csv` (XLSX mantido como fallback) |
| 4 relatórios Metabase | 5 relatórios Metabase (+ R5 cadastro de fornecedores) |

---

## 3. Fontes de dados — 5 relatórios Metabase

| Relatório | Conteúdo | Formato | Nome fixo (N8N) |
|---|---|---|---|
| R1 | Pendências por solicitação | CSV | `pendencias_zurich.csv` |
| R2 | Terceiros cadastrados | CSV | `terceiros_zurich.csv` |
| R3 | Situação documental por terceiro (última solicitação) | CSV | `situacao_terceiro_zurich.csv` |
| R4 | Situação documental por fornecedor/empresa (última solicitação) | CSV | `situacao_fornecedor_zurich.csv` |
| R5 | Cadastro completo de fornecedores (XLS exportado da plataforma) | CSV/XLS | `fornecedores_zurich.csv` |

> **R5:** exportado como XLS da plataforma e convertido para CSV antes de salvar em `data/`. Colunas relevantes: `Nome` (→ Razão Social) e `Documento` (→ CPF/CNPJ). Usado exclusivamente para os cards de totais e a seção de fornecedores sem interação com a plataforma.

### Colunas relevantes por relatório

**R1 — Pendências:**
`Razão Social`, `Situação da solicitação` (EM_ELABORACAO / APROVADO), `Área da pendência` (TERCEIROS / DOCUMENTOS), `Documento`, `Marcas e representações` (competência), `Pendência`

**R2 — Terceiros:**
`Razão Social`, `Status` (Ativo / Inativo)

**R3 — Situação por Terceiro:**
`Fornecedor Razão Social`, `Terceiro Razão Social`, `Terceiro CPF/CNPJ`, `Fornecedor CPF/CNPJ`, `Documento`, `Status`, `Situação Análise Documento`, `Data de Vencimento`

**R4 — Situação por Fornecedor:**
`Razão Social`, `CNPJ`, `Documento`, `Status`, `Situação Análise Documento`, `Data de Vencimento`

**R5 — Cadastro de Fornecedores:**
`Nome` (Razão Social), `Documento` (CPF/CNPJ)

---

## 4. Regra de classificação de conformidade

### Regra atual (vigente desde 27/05/2026)

A coluna **"Situação Análise Documento"** tem prioridade absoluta sobre qualquer outra coluna.

| Situação Análise Documento | Status do doc | Classificação final |
|---|---|---|
| APROVADO | (qualquer) | **Aprovado** |
| REPROVADO | (qualquer) | **Reprovado** |
| NÃO ANALISADO ou ausente | Não anexado | **Não anexado** |
| NÃO ANALISADO ou ausente | A vencer | **Aguardando análise** |
| NÃO ANALISADO ou ausente | Vencido | **Aguardando análise** |
| NÃO ANALISADO ou ausente | N/A ou vazio | **Aguardando análise** |

> **Importante:** Vencido e A vencer ambos caem em "Aguardando análise" — a decisão final sobre conformidade é do analista via "Situação Análise Documento", não da data de vencimento. "Situação da Última Solicitação" foi descartada do cálculo.

### De-para — regra antiga vs atual

| Classificação antiga | Classificação atual |
|---|---|
| Conforme | Aprovado |
| Vencido | Aguardando análise |
| Pendente | Não anexado |
| *(não existia)* | Reprovado |
| *(não existia)* | Aguardando análise |

---

## 5. Seções do dashboard (estado atual)

### Seções visíveis

| # | Seção | Descrição |
|---|---|---|
| 1 | **Header** | Título e data/hora de geração |
| 2 | **Filtro global** | Barra teal escura — select Fornecedor sincroniza todas as seções interativas |
| 3 | **KPI cards + Pizzas** | 13 cards de métricas + 2 gráficos de pizza lado a lado (Terceiros / Fornecedores) |
| 4 | **Conformidade Documental** | % NC por fornecedor (fig7) + stacked bar situação (fig8) — *não respondem ao filtro global* |
| 5 | **Terceiros Cadastrados** | Ativos vs Inativos por fornecedor |
| 6 | **Análise Interativa (drill-down)** | Fornecedor → Terceiro → Documentos, navegação por breadcrumb |
| 7 | **Situação Documental por Terceiro** | Tabela R3 com filtros, 7 KPIs próprios, export Excel/PDF/CSV |
| 8 | **Situação Documental da Empresa** | Tabela R4 com filtros, 6 KPIs próprios, export Excel/PDF/CSV |
| 9 | **Detalhamento de Pendências** | Tabela R1 com filtros, export Excel/PDF/CSV |
| 10 | **Fornecedor sem interação com a plataforma** | Tabela de fornecedores do cadastro sem nenhum doc em R3 ou R4 (recolhida por padrão) |

### De-para — seções ocultadas (27/05/2026)

| Seção | Motivo |
|---|---|
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
|---|---|---|---|
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

### Cards da seção R4 — Situação Documental da Empresa

| ID (JS) | Dado |
|---|---|
| `r4-kpi-forn` | Fornecedores com Docs |
| `r4-kpi-nc` | % Não Conformidade |
| `r4-kpi-c` | % Conformidade |
| `r4-kpi-aprov` | Docs Aprovados |
| `r4-kpi-reprov` | Docs Reprovados |
| `r4-kpi-nao-anal` | Docs Não Analisados |

### Cards da seção R3 — Situação Documental por Terceiro

| ID (JS) | Dado |
|---|---|
| `sit-kpi-nc` | % Não Conformidade Terceiros |
| `sit-kpi-c` | % Conformidade Terceiros |
| `sit-kpi-aprov` | Docs Aprovados |
| `sit-kpi-reprov` | Docs Reprovados |
| `sit-kpi-nao-anex` | Não Anexado |
| `sit-kpi-aguard` | Aguardando Análise |
| `sit-kpi-terc` | Terceiros com Docs |

> Todos os KPIs das seções R3 e R4 atualizam dinamicamente ao filtrar por fornecedor no select local.

---

## 7. Gráficos de pizza — conformidade

### Configuração atual

Dois gráficos lado a lado, pizza sólida (não donut), sem texto interno, apenas legenda.

| Pizza | Dados | Fatias |
|---|---|---|
| Conformidade Terceiros | R3 (sit_tabela) | Conforme (= Aprovado) / Não Conforme (todo o resto) |
| Conformidade Fornecedores | R4 (forn_sit_tabela) | Conforme (= Aprovado) / Não Conforme (todo o resto) |

Ambos respondem ao filtro global de fornecedor.

### De-para — pizzas

| Antes | Depois |
|---|---|
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

**Quem aparece no dropdown:** apenas fornecedores com ao menos um registro em R1, R3 ou R4. Fornecedores do cadastro sem atividade aparecem na seção "Sem Execução" (seção 10), não no filtro.

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

## 10. Seção "Fornecedor sem interação com a plataforma na Plataforma"

Adicionada em 03/06/2026. Exibe fornecedores presentes no cadastro (R5) que não possuem nenhum documento registrado em R3 (terceiros) ou R4 (corporativo).

**Lógica:**
1. Coleta CNPJs com atividade: união de CNPJs únicos em R4 e R3
2. Cruza com o cadastro R5: quem está no cadastro mas não na união → sem interação com a plataforma
3. Deduplicação por CNPJ para não repetir filiais

**Uso indicado:** revisão periódica com a Débora para confirmar se esses fornecedores são ativos, inativos ou cadastros a remover.

---

## 11. Terminologia — de-para

| Antes | Depois | Onde aparece |
|---|---|---|
| DOCUMENTOS (área) | FORNECEDOR (área) | Filtro de área no Detalhamento + badge na tabela |
| Conforme | Aprovado | Classificação de status |
| Vencido | Aguardando análise | Classificação de status |
| Pendente | Não anexado | Classificação de status |
| Competência em branco | "A classificar" | Coluna Competência no Detalhamento |
| Filtro "Status" no Detalhamento | Removido | Seção Detalhamento de Pendências |
| Total Fornecedores por Razão Social | Total Fornecedores por CNPJ | Card de topo |

---

## 12. Como rodar — modo manual (atual)

### Passo 1 — Exportar os 5 relatórios do Metabase / Plataforma

| Relatório | Nome no Metabase / Origem | Formato |
|---|---|---|
| R1 | Pendências por Solicitação com Documento | CSV |
| R2 | Relatório de Terceiros Cadastrados | CSV |
| R3 | Situação de Preenchimento Documental do Terceiro na Última Solicitação | CSV |
| R4 | Situação de Preenchimento Documental na Última Solicitação do Fornecedor | CSV |
| R5 | Relatório de Fornecedores (exportado da plataforma como XLS) | XLS → converter para CSV |

### Passo 2 — Salvar com nomes fixos na pasta data/

Salvar os 5 arquivos em `Dashboard\data\` com os nomes exatos da coluna "Nome fixo" da seção 3.

> Para o R5 (XLS): abrir com pandas (`header=1`), renomear coluna `Nome` → `Razão Social` e `Documento` → `CPF/CNPJ`, salvar como CSV UTF-8-sig com nome `fornecedores_zurich.csv`.

### Passo 3 — Rodar o script

```
python relatorio_fornecedores_zurich.py
```

### Passo 4 — Abrir o dashboard

O HTML é gerado em `Dashboard\relatorio_fornecedores_zurich.html`. Abrir no Chrome ou Edge.

---

## 13. Automação via N8N (planejada — a ser configurada por Ricardo/João)

```
[Agendador N8N] — 2x por semana (seg e qui, 08h)
    ↓
[5x HTTP Request — API Metabase + Plataforma]
  GET /api/card/{id_R1}/query/csv  →  pendencias_zurich.csv
  GET /api/card/{id_R2}/query/csv  →  terceiros_zurich.csv
  GET /api/card/{id_R3}/query/csv  →  situacao_terceiro_zurich.csv
  GET /api/card/{id_R4}/query/csv  →  situacao_fornecedor_zurich.csv
  Export R5 (plataforma)           →  fornecedores_zurich.csv
    ↓
[Write Binary File × 5]
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
2. Anotar os IDs das 4 questões Metabase + endpoint do R5
3. Configurar os nós HTTP com `Authorization: Bearer {token}`
4. Nó Execute Command executa o Python com o caminho correto do servidor
5. Atualizar `BASE_DIR` no script para o caminho do servidor (1 linha no topo do script)

---

## 14. Opções de acesso para Débora e Claudinha

| Opção | Como funciona | Requisito |
|---|---|---|
| Endpoint estático (recomendado) | URL fixa no servidor Efcaz — sempre atualizado no F5 | Ricardo configurar nginx/IIS |
| E-mail com HTML anexo (atual) | N8N gera e envia por e-mail a cada atualização | João finalizar fluxo N8N |
| Google Drive for Desktop | Arquivo sincroniza automaticamente — reabrir para ver atualização | App instalado nas máquinas |
| Download manual | Baixar o HTML do Drive a cada atualização | Sem instalação |

---

## 15. Histórico de versões

| Data | Sessão | O que mudou |
|---|---|---|
| 26/05/2026 | 1–4 | Build inicial: R1+R2+R3+R4, KPIs, pizza, drill-down, tabelas, filtro global, seções colapsáveis |
| 27/05/2026 | 5–7 | Nova regra de classificação (Aprovado/Reprovado por coluna Análise), R4 migrado para CSV, seções ocultas por alinhamento Débora/Ricardo, filtro de status removido do Detalhamento, área DOCUMENTOS → FORNECEDOR |
| 27/05/2026 | 8–9 | 2 pizzas sólidas lado a lado, card Total de Fornecedores, KPIs na seção R3, terminologia Conforme/Não Conforme (Ricardo), competência vazia → "A classificar", CNPJ composite key para razão social duplicada |
| 28/05/2026 | 10 | Documentação atualizada com de-paras completos |
| 01/06/2026 | — | Dados atualizados para jun/2026 (CSVs 03/06), card Total de Fornecedores alterado para contagem por CNPJ (55), card "Fornecedores com Execução" adicionado (38) |
| 03/06/2026 | 11 | R5 (cadastro XLS) adicionado como 5ª fonte; seção "Fornecedor sem interação com a plataforma" (21 fornecedores); enriquecimento do FORN_CNPJ_MAP com dados do cadastro; Top Service atualizado para 3 CNPJs |

---

*Script: `relatorio_fornecedores_zurich.py` | HTML: `relatorio_fornecedores_zurich.html` | Gerado com Claude Code — Efcaz CS*
