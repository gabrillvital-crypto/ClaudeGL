# Especificação Técnica — Dashboard Conformidade Zurich Airport (Python)
> Engenharia reversa completa | Versão Python estática | Gerado em 10/06/2026

---

## Stack Tecnológica

| Camada | Tecnologia |
|--------|-----------|
| Processamento | Python 3 + pandas + numpy |
| Gráficos | Plotly (go.Bar / go.Pie / go.Figure) |
| Output | HTML estático gerado por f-string |
| Interatividade runtime | JavaScript puro + Plotly.js (CDN) |
| Export tabelas | SheetJS (XLSX) + jsPDF + jspdf-autotable (CDN) |
| Filtros de UI | CSS puro + JS vanilla |

---

## DOIS DASHBOARDS — Diferenças críticas

Existem **dois scripts Python** independentes. Não são versões do mesmo arquivo — têm lógicas diferentes:

| Aspecto | `dashboard_zurich.py` | `relatorio_fornecedores_zurich.py` |
|---------|----------------------|----------------------------------|
| **Output** | `dashboard_zurich_airport.html` | `relatorio_fornecedores_zurich.html` |
| **Lógica R3** | 3 status: Conforme / Vencido / Pendente | 5 status: Aprovado / Reprovado / Não anexado / Aguardando Submissão / Em Análise |
| **Filtro global** | `<select>` simples + filtro Competência | Multi-select custom JS (dropdown com checkbox) — igual ao React |
| **CNPJ no dropdown** | Não tem | Tem — label "Razão Social — CNPJ" |
| **Alerta de auditoria** | Visível, colapsável | Oculto (`display:none!important`) |
| **Total Fornecedores** | Usa `nunique()` de Fornecedor CPF/CNPJ do R3 | Usa `fornecedores_zurich.csv` + fallback R3∪R4 |
| **Sem Execução** | Não implementado | Implementado — tabela completa |

> **O `relatorio_fornecedores_zurich.py` é a versão canônica e mais recente.** Esta especificação documenta os dois, mas foca no novo.

---

## PILAR 1 — MAPEAMENTO DE DADOS E ORIGENS

### 1.1 Arquivos de entrada

Todos os CSVs ficam em `Dashboard/data/` — alimentados pelo N8N com nomes fixos.

| Variável Python | Arquivo CSV | Conteúdo |
|----------------|-------------|---------|
| `df_pend` | `pendencias_zurich.csv` | Pendências abertas por fornecedor |
| `df_terc` | `terceiros_zurich.csv` | Cadastro de trabalhadores terceirizados (Ativo/Inativo) |
| `df_sit` | `situacao_terceiro_zurich.csv` | Status documental R3: documentos dos terceiros |
| `df_sit_forn` | `situacao_fornecedor_zurich.csv` (CSV) ou `situacao_fornecedor_zurich.xlsx` (fallback) | Status documental R4: documentação corporativa |
| `df_forn_geral` | `fornecedores_zurich.csv` (opcional) | Cadastro-mestre de fornecedores |

### 1.2 Leitura tolerante a encoding

```python
def read_csv_safe(path):
    for enc in ["utf-8-sig", "latin-1", "utf-8"]:
        try:
            df = pd.read_csv(path, encoding=enc, on_bad_lines="skip")
            df.columns = df.columns.str.strip()  # remove espaços nos headers
            return df
        except Exception:
            continue
```

Tenta 3 encodings — garante leitura independente do encoding salvo pelo N8N ou Excel.

### 1.3 Estrutura de colunas por arquivo

#### `pendencias_zurich.csv`
```
Razão Social | CPF/CNPJ | Situação da solicitação | Área da pendência |
Documento | Marcas e representações | Pendência
```
- Detecção: teste direto `if "Razão Social" in df.columns else "Razao Social"`
- `Situação da solicitação` → `Status` da tabela (valores: `EM_ELABORACAO` = "Pendente", `APROVADO` = "Em Análise")
- `Área da pendência` → `Area` (valores: `TERCEIROS`, `DOCUMENTOS`)
- `Marcas e representações` → `Competencia` (mês/ano de referência)
- `Pendência` → `Detalhe` — texto descritivo completo

#### `situacao_terceiro_zurich.csv` — alimenta R3
```
Fornecedor Razão Social | Fornecedor CPF/CNPJ | Terceiro Razão Social | Terceiro CPF/CNPJ |
Documento | Status | Data de Vencimento | Situação Análise Documento | Situação última solicitação
```
- `col_analise_r3` detectado por: `"lise" in c.lower() and "doc" in c.lower()`
- `col_sit_solic_r3` detectado por: `"ltima" in c.lower() and "solic" in c.lower()`
- Ambas as colunas são **opcionais** — o código cai em fallback se não existirem

#### `situacao_fornecedor_zurich.csv` — alimenta R4
```
Razão Social (col 0) | CNPJ | Documento | Status | Data de Vencimento | Situação Análise Documento
```
- Primeira coluna é sempre a Razão Social: `col_r4_rs = df_sit_forn.columns[0]`
- `col_analise` detectado por: `"lise" in c.lower() and "doc" in c.lower()`

#### `terceiros_zurich.csv`
```
Razão Social | Status | (outras ignoradas)
```
- `Status`: `Ativo` ou `Inativo` — KPIs e fig6

#### `fornecedores_zurich.csv` (opcional)
```
Razão Social | CPF/CNPJ | (outras ignoradas)
```
- Usado para: `total_forn_geral` (nunique de CNPJs), `sem_execucao`, enriquecer `forn_cnpj_map`

### 1.4 Como cada status é determinado

#### R3 — `relatorio_fornecedores_zurich.py` (lógica nova — 5 status)

```python
def map_status_r3(row):
    # Prioridade 1 — Situação Análise Documento (mandatória)
    if col_analise_r3:
        analise = str(row.get(col_analise_r3, "")).strip().upper()
        if analise == "APROVADO":  return "Aprovado"
        if analise == "REPROVADO": return "Reprovado"

    # Prioridade 2 — Status do documento
    raw_status = row.get("Status", None)
    is_na = pd.isna(raw_status) or str(raw_status).upper() in ("N/A", "NA", "")
    if is_na: return "Aguardando análise"
    s = str(raw_status).strip().lower()
    if "anexado" in s: return "Não anexado"
    return "Aguardando análise"  # A vencer e Vencido entram aqui
```

**Depois do map_status_r3 — split de "Aguardando análise":**
```python
def _status_final_r3(row):
    if row["Status_Cat"] != "Aguardando análise": return row["Status_Cat"]
    if col_sit_solic_r3 and str(row.get(col_sit_solic_r3)).strip() == "EM_ELABORACAO":
        return "Aguardando Submissão"
    return "Em Análise"
df_sit_calc["Status_Final"] = df_sit_calc.apply(_status_final_r3, axis=1)
```

#### R3 — `dashboard_zurich.py` (lógica antiga — 3 status)
```python
STATUS_MAP = {"A vencer": "Conforme", "Vencido": "Vencido", "Não anexado": "Pendente"}
df_sit_calc = df_sit[df_sit["Status"].isin(STATUS_MAP.keys())].copy()
```
Apenas 3 valores são aceitos — N/A e outras strings são descartados.

#### R4 — ambos os scripts (`relatorio_fornecedores_zurich.py`)

```python
def map_status_r4(row):
    analise = str(row.get(col_analise, "")).strip().upper()
    if analise == "APROVADO":  return "Aprovado"
    if analise == "REPROVADO": return "Reprovado"
    status = str(row.get("Status", "")).strip().lower()
    if "vencer" in status:  return "Aprovado"   # A vencer = ainda válido
    if "anexado" in status: return "Não Anexado"
    if "vencido" in status: return "Vencido"
    return "Em análise"
```

---

## PILAR 2 — MATRIZ DE CONEXÕES E FLUXO

### 2.1 Arquitetura de geração — Python (estático)

O dashboard Python **não é uma SPA**. É um gerador que roda uma vez e produz um arquivo HTML autossuficiente. Toda a interatividade é JavaScript puro operando sobre dados embarcados no HTML.

```
CSVs em Dashboard/data/
       │
       ▼ pandas.read_csv (3 encodings)
df_pend / df_terc / df_sit / df_sit_forn / df_forn_geral
       │
       ▼ Processamento Python
abbrev() → normalização de nomes
map_status_r3() / map_status_r4() → classificação de status
groupby / aggregações → DataFrames para gráficos
tabela / sit_tabela / forn_sit_tabela → DataFrames para tabelas
       │
       ▼ Serialização
.to_dict("records") → listas de dicts Python
json.dumps() → strings JSON
fig.to_html(full_html=False) → divs Plotly embutidos
       │
       ▼ f-string HTML gigante
html = f"""..."""
f.write(html) → dashboard_zurich_airport.html OU relatorio_fornecedores_zurich.html
       │
       ▼ Navegador abre o HTML
const DADOS    = [...];   // tabela pendências
const SIT      = [...];   // situação R3
const FORN_SIT = [...];   // situação R4
const TERC_KPI = [...];   // terceiros cadastro
       │
       ▼ JS vanilla (sem framework)
filtrarTabela() / filtrarSit() / filtrarFornSit()
applyGlobalFilter() / updateKPICards()
renderDrillSuppliers() / showWorkers() / showDocs()
       │
       ▼ innerHTML direto
tbody.innerHTML = linhas.map(r => `<tr>...</tr>`).join("")
```

### 2.2 Caminho de um dado: "Aprovado" aparece no donut geral

```
situacao_terceiro_zurich.csv
  → df_sit[n]['Situação Análise Documento'] = "APROVADO"
  → map_status_r3() retorna "Aprovado"
  → df_sit_calc[n]['Status_Cat'] = "Aprovado"
  → total_conformes = (df_sit_calc["Status_Cat"] == "Aprovado").sum()
  → pct_conformidade = total_conformes / total_docs_sit * 100
  → const SIT = [{..., "Status": "Aprovado"}, ...];  ← embutido no HTML
  → JavaScript renderPizzaGeral(SIT, FORN_SIT)
  → conf = SIT.filter(r => r.Status === "Aprovado").length + FORN_SIT.filter(...)
  → Plotly.react("fig-pizza-geral", [{values:[conf,naoConf], type:"pie", hole:0.5}])
  → Plotly renderiza o donut verde
```

### 2.3 Variáveis Python que viram constantes JavaScript

| Python | JavaScript | Alimenta |
|--------|-----------|---------|
| `tabela.to_dict("records")` | `const DADOS = [...]` | Tabela pendências + KPIs dinâmicos |
| `sit_tabela.to_dict("records")` | `const SIT = [...]` | Tabela R3 + donuts + drill-down |
| `forn_sit_tabela.to_dict("records")` | `const FORN_SIT = [...]` | Tabela R4 + KPIs R4 dinâmicos |
| `terc_kpi.to_dict("records")` | `const TERC_KPI = [...]` | KPI terceiros ativos |
| `forn_cnpj_json` | `const FORN_CNPJ_MAP = {...}` | Dropdown com CNPJ |
| `sem_exec_json` | `const SEM_EXEC = [...]` | Tabela sem execução |
| `fig1.to_html(...)` | `<div id="fig1">...</div>` | Gráfico Plotly pré-renderizado |

### 2.4 Responsabilidade dividida Python × JavaScript

| O que Python faz | O que JavaScript faz |
|-----------------|---------------------|
| Classificar status de cada linha (R3/R4) | Filtrar linhas por fornecedor/status/busca |
| Calcular KPIs totais (valores iniciais) | Recalcular KPIs quando filtro muda |
| Gerar gráficos Plotly (fig1–fig8) | Renderizar donuts de conformidade via Plotly.react() |
| Serializar dados para JSON | Poplar selects, renderizar tabelas via innerHTML |
| Gerar HTML/CSS/JS completo | Drill-down interativo (3 níveis) |
| Detectar colunas dinamicamente | Multi-select de fornecedor com busca |

---

## PILAR 3 — ARQUITETURA E LÓGICA DOS FILTROS

### 3.1 Filtro Global — `relatorio_fornecedores_zurich.py`

O script novo usa um **multi-select custom** — componente JavaScript completamente manual, sem biblioteca:

```html
<div id="gf-multi-wrap">
  <div id="gf-multi-btn">                  ← botão trigger
    <span id="gf-selected-label">Todos</span>
  </div>
  <div id="gf-multi-panel">                ← dropdown (display:none por padrão)
    <input id="gf-multi-search">           ← busca por texto
    <div id="gf-multi-list">               ← itens com checkbox
      <!-- preenchido dinamicamente pelo JS -->
    </div>
    <div id="gf-multi-footer">Limpar</div>
  </div>
</div>
```

**Construção do dropdown com CNPJ** (`relatorio_fornecedores_zurich.py`):

Python gera `forn_cnpj_map` — dicionário de `nome_abrev → [cnpj1, cnpj2, ...]` mas **só para fornecedores com CNPJs distintos** (filiais):

```python
_grp = df_sit_calc.groupby("Empresa")["Fornecedor CPF/CNPJ"].apply(
    lambda x: sorted(set(...))
)
forn_cnpj_map = {k: v for k, v in _grp.items() if len(v) > 1}
# Enriquece com cadastro (fornecedores_zurich.csv) se disponível
```

JavaScript lê o mapa e constrói labels diferenciados:
```javascript
// Para fornecedores com 1 CNPJ → label = nome
// Para fornecedores com 2+ CNPJs → label = "nome — CNPJ1" e "nome — CNPJ2" (entradas separadas)
const map = FORN_CNPJ_MAP;
const label = map[nome] && map[nome].length > 1
  ? `${nome} — ${fmtCNPJ(cnpj)}`
  : nome;
```

### 3.2 Estado do filtro global — `gfSelectedForn`

```javascript
let gfSelectedForn = new Set();  // chaves selecionadas (nome ou "nome|||cnpj")

function applyGlobalFilter() {
  const sel = [...gfSelectedForn];
  updateKPICards(sel);          // recalcula KPIs
  renderPizzaGeral(sel);        // atualiza donuts
  filtrarSit();                 // re-renderiza tabela R3
  filtrarFornSit();             // re-renderiza tabela R4
  filtrarTabela();              // re-renderiza pendências
  renderDrillSuppliers();       // atualiza drill-down
  toggleGlobalKpis(sel.length > 0);  // esconde/mostra 2 KPIs globais
}
```

### 3.3 Validação de Razão Social idêntica com CNPJs distintos

Python detecta duplicatas e cria entradas separadas no dropdown:

```python
# forn_cnpj_map = {"KARUANA SERVICOS": ["12345678000190", "98765432000110"]}
# → JavaScript cria dois itens no dropdown:
#   "KARUANA SERVICOS — 12.345.678/0001-90"
#   "KARUANA SERVICOS — 98.765.432/0001-10"
```

Cada item tem chave composta `"nome|||cnpj"`. A função de match:
```javascript
function matchForn(rowForn, rowCNPJ) {
  if (gfSelectedForn.size === 0) return true;
  for (const key of gfSelectedForn) {
    const [nome, cnpj] = key.includes("|||") ? key.split("|||") : [key, ""];
    if (rowForn === nome && (!cnpj || !rowCNPJ || rowCNPJ === cnpj)) return true;
  }
  return false;
}
```

### 3.4 Lógica IN/includes para múltipla seleção

`gfSelectedForn` é um `Set` — o `for...of` itera todos os selecionados e retorna `true` na primeira correspondência. Equivalente SQL a `WHERE nome IN ('A','B','C')`.

Todos os `filtrar*()` chamam `matchForn(r.Fornecedor, r.CNPJ_Forn)` para cada linha do array de dados.

### 3.5 Regra de visibilidade dos KPIs globais

```javascript
function toggleGlobalKpis(hasFilter) {
  const card1 = document.getElementById("kpi-card-total-forn");
  const card2 = document.getElementById("kpi-card-exec-plat");
  card1.style.display = hasFilter ? "none" : "";
  card2.style.display = hasFilter ? "none" : "";
  // Grid ajusta automaticamente com auto-fit/minmax
}
```

CSS da grade KPI:
```css
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);  /* fixo em 4 colunas no relatório novo */
}
```

Com filtro: os 2 primeiros cards somem do DOM via `display:none`. Sem filtro: 10 cards (4+4+2). Com filtro: 8 cards. O `repeat(4,1fr)` mantém 4 colunas em ambos os casos.

### 3.6 Filtros locais por seção

Cada seção tem filtros independentes (Fornecedor multi-select, Status, Busca) que operam sobre as constantes JavaScript (não sobre os dados já filtrados pelo global). A cascata é aplicada dentro de cada função:

```javascript
function filtrarSit() {
  const empSel = sitEmpSet;        // Set local da seção R3
  const stat   = document.getElementById("sit-status").value;
  const busca  = document.getElementById("sit-busca").value.toLowerCase();

  sitFiltrado = SIT.filter(r => {
    if (empSel.size > 0 && !empSel.has(r.Fornecedor)) return false;  // filtro local
    if (!matchForn(r.Fornecedor, r.CNPJ_Forn)) return false;         // filtro global
    if (stat && r.Status !== stat) return false;
    if (busca && !r.Documento.toLowerCase().includes(busca)) return false;
    return true;
  });
  // renderiza tbody
}
```

### 3.7 Filtro Global — `dashboard_zurich.py` (versão antiga)

O script antigo usa `<select>` simples — sem multi-select:
```html
<select id="gf-fornecedor" onchange="applyGlobalFilter()">
  <option value="">Todos os fornecedores</option>
</select>
<select id="gf-competencia" onchange="applyGlobalFilter()">
  <option value="">Todas as competencias</option>
</select>
```

Sem suporte a múltiplos fornecedores simultâneos. Sem CNPJ no label.

---

## PILAR 4 — MAPEAMENTO DE UX E COMPORTAMENTO PROATIVO

### 4.1 Tooltips dos KPI Cards — Python via CSS

O Python usa `data-tooltip` attribute com `::after`/`::before` CSS puro — sem JavaScript de estado. Técnica diferente do React (que usa Tailwind `group-hover`), mas visualmente idêntica.

```css
.kpi-card[data-tooltip]::after {
  content: attr(data-tooltip);        /* lê o atributo data-tooltip */
  position: absolute;
  bottom: calc(100% + 8px);
  /* ... posicionamento e estilo do balão */
  opacity: 0; visibility: hidden;
  transition: opacity .18s ease, visibility .18s ease;
}
.kpi-card[data-tooltip]:hover::after { opacity: 1; visibility: visible; }
.kpi-card[data-tooltip]::before { /* triângulo CSS apontando para baixo */ }
```

**Mapeamento completo de tooltips** (`relatorio_fornecedores_zurich.py`):

| ID do Card | Cor | Tooltip |
|-----------|-----|---------|
| `kpi-total-forn` | teal | "Número total de empresas fornecedoras cadastradas na base." |
| `kpi-exec-plat` | teal | "Quantidade de fornecedores que possuem contratos ativos e movimentações na plataforma." |
| `kpi-docs-esp-forn` | teal | "Quantidade total de documentos que a empresa contratada precisa enviar para a plataforma." |
| `kpi-docs-esp-terc` | teal | "Quantidade total de documentos exigidos dos funcionários ou prestadores vinculados ao fornecedor." |
| `kpi-docs-aprov` | green | "Documentos que já foram analisados e validados com sucesso pela nossa equipe de conformidade." |
| `kpi-docs-nao-aprov` | red | "Documentos que passaram por análise, mas foram recusados por inconformidade ou erro." |
| `kpi-docs-nao-env` | yellow | "Documentos obrigatórios que ainda estão pendentes de anexo por parte do fornecedor ou terceiro." |
| `kpi-docs-aguard-sub` | yellow | "Documentos inseridos na plataforma pelo fornecedor, mas ainda não submetidos para análise. O fornecedor precisa concluir o envio clicando em submeter." |
| `kpi-docs-em-anal` | orange | "Documentos já submetidos pelos fornecedores aguardando validação da equipe de conformidade." |
| `kpi-docs-vencido` | red | "Documentos de fornecedores com prazo vencido — exigem renovação ou substituição imediata." |

### 4.2 Paleta de cores e semântica — Python

```python
COR_TEAL        = "#0E8FA3"   # padrão / neutro
COR_TEAL_LIGHT  = "#5BBFCC"   # variação clara
COR_TEAL_ESCURO = "#0A6A7A"   # fundo da barra de filtro global
COR_LARANJA     = "#F4793B"   # em processo / aguardando análise
COR_CINZA       = "#6C757D"   # inativo / neutro
COR_VERDE       = "#28A745"   # conforme / aprovado
COR_AMARELO     = "#FFC107"   # atenção / não enviado
COR_VERMELHO    = "#DC3545"   # reprovado / vencido / não conforme
COR_BG          = "#F8F9FA"   # fundo da página
COR_CARD        = "#FFFFFF"   # fundo dos cards
```

#### Cores dos gráficos de conformidade (donuts)

O Python usa JavaScript + Plotly — **não usa `#10B981` / `#EF4444` como o React**. Usa as cores Python definidas no CSS:

```javascript
// Cores dos donuts — geradas por renderPizzaDonut()
const COR_CONF    = "#28A745";   // verde
const COR_NAO     = "#DC3545";   // vermelho
```

Os 3 donuts são renderizados por `Plotly.react()` no navegador, não por `go.Pie()` no Python. O Python gera fig1–fig8 (barras), mas os **donuts de conformidade são JavaScript puros**.

#### Cores dinâmicas do gráfico fig7 (% não conformidade)

```python
cores_conf = [
    COR_VERDE   if p <= 30 else
    COR_AMARELO if p <= 60 else
    COR_VERMELHO
    for p in conf_emp["Pct_Nao_Conf"]
]
```

Verde ≤30% → situação controlada | Amarelo 31–60% → atenção | Vermelho >60% → risco alto.

### 4.3 Comportamento do Triple-View (3 donuts)

Os 3 donuts são **renderizados inteiramente em JavaScript** via `Plotly.react()`, não pelo Python. Isso permite que atualizem em tempo real quando o filtro global muda.

```javascript
function renderPizzaDonut(divId, conforme, naoConf) {
  const total = conforme + naoConf;
  const pct = total > 0 ? (conforme/total*100).toFixed(1) : "0.0";
  Plotly.react(divId, [{
    type: "pie", hole: 0.5,
    values: [conforme, naoConf],
    labels: [`Conforme ${pct}%`, `Não Conforme ${(100-parseFloat(pct)).toFixed(1)}%`],
    marker: { colors: ["#28A745", "#DC3545"] },
    textinfo: "none",
  }], { height: 240, margin: {t:0,b:0,l:0,r:0}, showlegend: true });
  // Texto central inserido via overlay div absoluto
}

function renderPizzaGeral(fornSel) {
  const sit  = applyGfFilter(SIT, fornSel);
  const forn = applyGfFilter(FORN_SIT, fornSel);
  const aprovR3 = sit.filter(r => r.Status === "Aprovado").length;
  const aprovR4 = forn.filter(r => r.Status === "Aprovado").length;
  renderPizzaDonut("fig-pizza-geral", aprovR3 + aprovR4, sit.length + forn.length - aprovR3 - aprovR4);
  renderPizzaDonut("fig-pizza-forn",  aprovR4, forn.length - aprovR4);
  renderPizzaDonut("fig-pizza",       aprovR3, sit.length - aprovR3);
}
```

### 4.4 Drill-down interativo — 3 níveis

Único no Python. Não existe na versão React atual. Hierarquia: Fornecedor → Terceiro → Documentos.

**Nível 1 — Cards de fornecedor:**
```javascript
function renderDrillSuppliers() {
  const filt = gfSelectedForn.size > 0 ? [...gfSelectedForn] : null;
  const forns = [...new Set(SIT.filter(r => !filt || matchForn(r.Fornecedor)).map(r => r.Fornecedor))];
  // Calcula pct não conforme por fornecedor
  // Renderiza cards com mini-barra horizontal e cor semântica
}
```

**Nível 2 — Lista de terceiros:**
- Click no card → `showWorkers(fornecedor)`
- Lista todos os terceiros daquele fornecedor com badges por status

**Nível 3 — Documentos do terceiro:**
- Click no terceiro → `showDocs(fornecedor, terceiro)`
- Lista documentos com status e vencimento

### 4.5 Modo agrupado (seção R3)

Exclusivo do Python — botão "Modo Agrupado" renderiza os resultados agrupados por fornecedor em vez de tabela linha a linha:

```javascript
function renderSitAgrupado(rows) {
  const grupos = {};
  rows.forEach(r => {
    if (!grupos[r.Fornecedor]) grupos[r.Fornecedor] = { items: [], nc: 0 };
    grupos[r.Fornecedor].items.push(r);
    if (r.Status !== "Aprovado") grupos[r.Fornecedor].nc++;
  });
  // Renderiza .grupo-card com .grupo-doc-badge por documento
}
```

---

## PILAR 5 — DIFERENÇAS ENTRE PYTHON E REACT

| Aspecto | Python (relatorio_fornecedores) | React (dashboard-react/) |
|---------|--------------------------------|--------------------------|
| **Renderização** | Estática — HTML gerado uma vez | SPA — renderização em tempo real |
| **Gráficos** | Plotly (fig1–fig8 = Python, donuts = JS) | Recharts (PieChart) |
| **Gráficos de barra** | 8 gráficos: pendências, tipos, status, área, trabalhadores, conformidade | Apenas 3 donuts |
| **Donuts de conformidade** | `Plotly.react()` — JavaScript | `Recharts PieChart` — React |
| **Drill-down** | 3 níveis interativos | Removido |
| **Alerta de Auditoria** | Seção completa (oculta na versão relatório) | Removido |
| **Modo agrupado** | Sim — seção R3 | Não |
| **Filtro Competência** | Apenas no `dashboard_zurich.py` | Removido |
| **Status R3** | 5 labels (Aprovado/Reprovado/Não Anexado/Ag.Submissão/Em Análise) | Igual |
| **Status R4** | Aprovado/Reprovado/Não Anexado/Em análise/Vencido | Igual |
| **CNPJ no dropdown** | Só para duplicatas (forn_cnpj_map com len>1) | Para todos os fornecedores |
| **Export PDF** | jsPDF autoTable (CDN) | jsPDF autoTable (npm) |
| **KPIs com tooltip** | data-tooltip CSS (::after/::before) | Tailwind group-hover |
| **Sem Execução** | Tabela completa | Tabela completa |
| **Simulação BD** | Bloco de dados simulados com numpy (demo) | Removido |

---

## Funções Python críticas

### `abbrev(name, n=40)`
```python
def abbrev(name, n=40):
    s = str(name).strip()
    short = re.sub(r'\s+(LTDA|LTDA\.|S/A|SA|EIRELI|ME|EPP).*', '', s, flags=re.I)
    return short[:n] + "..." if len(short) > n else short
```
Remove sufixos jurídicos e trunca. **Aplicada em todas as colunas de Razão Social** — garante que "Karuana LTDA" e "Karuana" sejam a mesma entidade no filtro.

### `extrair_doc(row)`
```python
def extrair_doc(row):
    doc = str(row.get("Documento", "")).strip()
    if doc and doc != "nan": return doc.upper()
    pend = str(row.get("Pendencia", row.get("Pendência", "")))
    m = re.match(r"[A-Z\s]+ - ([^,]+)", pend)
    if m: return m.group(1).strip().upper()
    m2 = re.match(r"^([^,]+),", pend)
    if m2: return m2.group(1).strip().upper()
    return "OUTROS"
```

### `_norm_cnpj(v)`
```python
def _norm_cnpj(v):
    s = str(v).strip()
    if s in ("", "nan", "0", "None"): return ""
    if s.replace(".", "").replace("-", "").replace("/", "").isdigit():
        try: return str(int(float(s.replace(".", "").replace("-", "").replace("/", ""))))
        except: pass
    return s
```
O `int(float(s))` remove o sufixo `.0` que o pandas gera ao ler CNPJs numéricos como float.

---

## Como rodar

```bash
# Versão nova (relatório de fornecedores)
cd Dashboard
python relatorio_fornecedores_zurich.py
# → gera relatorio_fornecedores_zurich.html

# Versão antiga (dashboard de terceiros)
python dashboard_zurich.py
# → gera dashboard_zurich_airport.html
```

Abrir o HTML diretamente no navegador — não precisa de servidor.

---

*Documentação da pasta `Dashboard/` (Python estático). A versão React paralela está em `dashboard-react/` com especificação em `dashboard-react/ARQUITETURA_TECNICA.md`.*
