# Especificação Técnica — Dashboard Conformidade Zurich Airport
> Engenharia reversa completa | Versão React (dashboard-react/) | Gerado em 10/06/2026 | Atualizado em 11/06/2026

---

## Stack Tecnológica

| Camada | Tecnologia |
|--------|-----------|
| Build | Vite 5 + TypeScript |
| UI | React 18 + Tailwind CSS 3 |
| Gráficos | Recharts (PieChart / Donut) |
| Parsing CSV | PapaParse |
| Export XLSX | SheetJS (xlsx) |
| Export PDF | jsPDF + jspdf-autotable |
| Dev server | `iniciar.bat` → http://localhost:5173 |

---

## PILAR 1 — MAPEAMENTO DE DADOS E ORIGENS

### 1.1 Arquivos de origem

Todos os CSVs ficam em `dashboard-react/data/` e são servidos pelo Vite em `/data/*.csv`.

| Variável interna | Arquivo CSV | Conteúdo |
|----------------|-------------|---------|
| `rawPend` | `pendencias_zurich.csv` | Pendências abertas por fornecedor |
| `rawTerc` | `terceiros_zurich.csv` | Cadastro de trabalhadores terceirizados (Ativo/Inativo) |
| `rawSit` | `situacao_terceiro_zurich.csv` | Status documental R3: documentos dos terceiros |
| `rawFornSit` | `situacao_fornecedor_zurich.csv` | Status documental R4: documentos corporativos do fornecedor |
| `rawFornCad` | `fornecedores_zurich.csv` | Cadastro-mestre de fornecedores (fallback tolerante — não quebra o sistema se ausente) |

### 1.2 Estrutura de colunas por arquivo

#### `pendencias_zurich.csv` — `rawPend`
```
Razão Social | CPF/CNPJ | Situação da solicitação | Área da pendência | Documento | Marcas e representações | Pendência
```
- Detecção de coluna via `findCol()` — busca por substring nas chaves
- `Situação da solicitação` → campo `Status` da `PendRow` (valores: `EM_ELABORACAO`, `APROVADO`)
- `Área da pendência` → campo `Area` (valores: `TERCEIROS`, `DOCUMENTOS`)
- `Marcas e representações` → campo `Competencia` (mês/ano de referência)
- `Pendência` → campo `Detalhe` — texto descritivo completo da pendência
  - **CRÍTICO:** esta coluna vem DEPOIS de `Área da pendência` no CSV. A detecção usa regex exato `/^pend[eê]ncia$/i` para evitar capturar `Área da pendência` (que também contém "pend")

#### `situacao_terceiro_zurich.csv` — `rawSit` → alimenta R3
```
Fornecedor Razão Social | Fornecedor CPF/CNPJ | Terceiro Razão Social | Terceiro CPF/CNPJ |
Documento | Status | Data de Vencimento | Situação Análise Documento | Situação última solicitação
```
- Todas as colunas são detectadas dinamicamente por substring — nunca por posição fixa
- `Situação Análise Documento` → prioridade máxima na classificação de status R3
- `Situação última solicitação` → tiebreaker para "Aguardando Submissão" vs "Em Análise"

#### `situacao_fornecedor_zurich.csv` — `rawFornSit` → alimenta R4
```
Razão Social | CPF/CNPJ | Documento | Status | Data de Vencimento | Situação Análise Documento
```
- Primeira coluna (`fornSitCols[0]`) é sempre a Razão Social do fornecedor
- `Situação Análise Documento` é opcional (coluna detectada por "lise" + "doc")

#### `terceiros_zurich.csv` — `rawTerc`
```
Razão Social | Status | (outras colunas ignoradas)
```
- `Status`: `Ativo` ou `Inativo` — alimenta KPIs de trabalhadores e gráfico `trab_emp_data`

#### `fornecedores_zurich.csv` — `rawFornCad` (cadastro-mestre)
```
Razão Social | CPF/CNPJ | (outras colunas ignoradas)
```
- Usado exclusivamente para: calcular `total_forn_geral`, identificar `sem_execucao` e popular `fornCNPJMap`
- CNPJs vêm no formato pandas float (ex: `20845454000170.0`) — normalizados via `normCNPJ()`

### 1.3 Como cada status é determinado

#### Status R3 — `situacao_terceiro_zurich.csv`

```
mapStatusR3(row, colAnalise, colSitSolic):

1. Se coluna "Situação Análise Documento" existe:
   - valor == "APROVADO"  → StatusR3 = "Aprovado"
   - valor == "REPROVADO" → StatusR3 = "Reprovado"

2. Fallback pelo campo "Status" do documento:
   - contém "anexado" → "Não anexado"
   - demais (vencendo, vencido, N/A, em branco) → Aguardando análise →
     - Situação última solicitação == "EM_ELABORACAO" → "Aguardando Submissão"
     - else → "Em Análise"
```

#### Status R4 — `situacao_fornecedor_zurich.csv`

```
mapStatusR4(row, colAnalise):

COM coluna "Situação Análise Documento":
  - "APROVADO"  → "Aprovado"
  - "REPROVADO" → "Reprovado"
  - NOT_ANALYZED + Status contém "vencer"   → "Aprovado"  (a vencer = ainda válido)
  - NOT_ANALYZED + Status contém "anexado"  → "Não Anexado"
  - NOT_ANALYZED + Status contém "vencido"  → "Vencido"
  - else → "Em análise"

SEM a coluna (modo legacy):
  - "aprovado" (sem "ressalva") → "Aprovado"
  - "reprovado" → "Reprovado"
  - "vencer"   → "Aprovado"
  - "vencido"  → "Vencido"
  - "anexado"  → "Não Anexado"
```

---

## PILAR 2 — MATRIZ DE CONEXÕES E FLUXO

### 2.1 Diagrama de fluxo completo

```
ARQUIVOS CSV (dashboard-react/data/)
       │
       ▼ fetch paralelo (Promise.all)
csvLoader.ts → loadAllCSVs()
  PapaParse.parse() com header:true, skipEmptyLines, trimHeaders
       │
       ▼ { rawPend, rawTerc, rawSit, rawFornSit, rawFornCad }
useDashboardData.ts → useEffect()
  → processAllData(rawPend, rawTerc, rawSit, rawFornSit, rawFornCad)
       │
       ▼ dataProcessing.ts
  1. Descoberta de colunas (findCol por substring)
  2. mapStatusR3 / mapStatusR4 → classificação por linha
  3. Agregações: contagens, sets de CNPJ, arrays
  4. Retorna DashboardData (contrato tipado)
       │
       ▼ setData(processed) → state: 'success'
App.tsx
  useDashboardData() → data: DashboardData
  useGlobalFilter()  → selectedFornSet: Set<string>
       │
       ├─ useMemo: fornOptions (lista com CNPJ formatado para o dropdown)
       ├─ useMemo: sitFiltered   (data.sit_tabela  filtrado por matchesForn)
       ├─ useMemo: fornSitFiltered (data.forn_sit  filtrado por matchesForn)
       ├─ useMemo: tabelaFiltered (data.tabela     filtrado por matchesForn)
       ├─ useMemo: kpis          (contagens reativas ao filtro)
       └─ useMemo: r4Kpis        (sub-KPIs R4 reativos ao filtro)
       │
       ▼ render
┌──────────────────────────────────────────────────────┐
│ Header (título + data de geração)                    │
├──────────────────────────────────────────────────────┤
│ GlobalFilter (MultiSelectDropdown + botão limpar)    │
├──────────────────────────────────────────────────────┤
│ KPIGrid                                              │
│   [2 globais visíveis somente se !hasFilter]         │
│   [6 ativos sempre visíveis]                         │
├──────────────────────────────────────────────────────┤
│ ConformidadeCharts                                   │
│   [3 donuts recebem sitFiltered + fornSitFiltered]   │
├──────────────────────────────────────────────────────┤
│ Section "R3" → R3Section(sitFiltered)                │
│ Section "R4" → SituacaoEmpresaSection(fornSitFiltered│
│ Section "Pendências" → PendenciasSection(tabFiltered)│
│ Section "Sem Execução" → data.sem_execucao (fixo)    │
└──────────────────────────────────────────────────────┘
```

### 2.2 Caminho de um dado específico: exemplo — "Aprovado" aparece no donut

```
situacao_terceiro_zurich.csv
  → rawSit[n]['Situação Análise Documento'] = "APROVADO"
  → mapStatusR3() retorna 'Aprovado'
  → sitCalc[n].Status = 'Aprovado'
  → aprovR3 = sitCalc.filter(r => r.Status === 'Aprovado').length
  → docs_aprovados = aprovR3 + r4_aprovado    (DashboardData)
  → App.tsx: sitFiltered = sitCalc.filter(matchesForn)
  → ConformidadeCharts recebe sitFiltered
  → aprovR3 = sitData.filter(r => r.Status === 'Aprovado').length
  → PizzaCard "Conformidade Terceiros" → conforme = aprovR3 → pct = aprovR3/total
  → Recharts PieChart: Cell[0] fill='#10B981' (verde conforme)
```

### 2.3 Rastreabilidade das variáveis de estado

| Variável de estado | Onde vive | O que controla |
|-------------------|-----------|---------------|
| `data` | `useDashboardData` → `useState` | Todo o conjunto de dados processados |
| `state` ('idle'/'loading'/'success'/'error') | `useDashboardData` | Loading screen vs dashboard |
| `selectedFornSet` | `useGlobalFilter` → `useState<Set<string>>` | Quais fornecedores estão ativos no filtro global |
| `hasFilter` | `App.tsx` derivado | `selectedFornSet.size > 0` — controla visibilidade dos KPIs globais |
| `sitFiltered` | `App.tsx` useMemo | Linhas R3 após filtro global |
| `fornSitFiltered` | `App.tsx` useMemo | Linhas R4 após filtro global |
| `tabelaFiltered` | `App.tsx` useMemo | Linhas pendências após filtro global |
| `kpis` | `App.tsx` useMemo | KPI cards (recalculados on-the-fly quando filtrado) |
| `r4Kpis` | `App.tsx` useMemo | Sub-KPIs da seção R4 |
| `filt/stat/area/comp/busca` | Cada Section (useState local) | Filtros internos de cada tabela |

---

## PILAR 3 — ARQUITETURA E LÓGICA DOS FILTROS

### 3.1 Estrutura do filtro global

O filtro global é baseado em um `Set<string>` de chaves. Cada chave é o **nome abreviado do fornecedor** (saída de `abbrev()`). O mesmo nome abreviado é usado como chave em todas as tabelas — isso garante que um único toggle afete R3, R4 e Pendências simultaneamente.

```
hooks/useGlobalFilter.ts
  selectedFornSet: Set<string>    ← chaves são os nomes abreviados
  toggleForn(key: string)         ← adiciona ou remove do Set
  clearAll()                      ← esvazia o Set
  matchesForn(nome, cnpj?)        ← função de teste usada nos useMemo
```

### 3.2 Razão Social idêntica com CNPJs distintos (filiais)

O problema: dois fornecedores podem ter a mesma Razão Social mas CNPJs diferentes (ex: Karuana Matriz e Karuana Filial). Se a chave fosse só o nome, selecionar um selecionaria os dois.

**Solução implementada — chave composta com separador `|||`:**

```typescript
// Formato da chave quando há CNPJ: "Nome do Fornecedor|||12345678000195"
// Sem CNPJ: "Nome do Fornecedor"

// Criação da chave — App.tsx:
const fornOptions = [...names].sort().map(name => ({
  key: name,                          // chave SEMPRE = nome abreviado (sem CNPJ)
  label: fornCNPJMap[name]
    ? `${name} — ${fmtCNPJ(fornCNPJMap[name])}`   // label exibe CNPJ formatado
    : name,
}))
```

> **Nota importante:** Na implementação atual, a chave de filtro é só o nome abreviado (sem `|||`). O separador `|||` e o `parseFornVal()` existem no código (em `useGlobalFilter.ts` e `MultiSelectDropdown.tsx`) para suporte futuro a filtragem por CNPJ específico, mas ainda não são utilizados para montar as chaves em `fornOptions`.

**Função de correspondência:**
```typescript
matchesForn(rowNome, rowCNPJ?) {
  if (selectedFornSet.size === 0) return true   // sem filtro = tudo passa
  for (const raw of selectedFornSet) {
    const { nome, cnpj } = parseFornVal(raw)    // extrai nome e CNPJ da chave
    if (rowNome === nome && (!cnpj || !rowCNPJ || rowCNPJ === cnpj)) return true
  }
  return false
}
```

### 3.3 Lógica IN/includes para múltiplos fornecedores

Quando o usuário seleciona 3 fornecedores, `selectedFornSet = Set{'Forn A', 'Forn B', 'Forn C'}`.

`matchesForn('Forn B')` percorre o Set com `for...of` e retorna `true` na primeira correspondência — comportamento equivalente a SQL `WHERE nome IN ('Forn A', 'Forn B', 'Forn C')`.

Os filtros derivados em `App.tsx` usam `Array.filter(r => matchesForn(r.Fornecedor))`, que itera cada linha da tabela e aplica essa lógica. Os três `useMemo` — `sitFiltered`, `fornSitFiltered`, `tabelaFiltered` — são recalculados automaticamente pelo React quando `selectedFornSet` muda (dependência via `matchesForn` que é um `useCallback` com `selectedFornSet` como dep).

Os KPIs também são recalculados no mesmo ciclo:
```typescript
// App.tsx — useMemo kpis
docs_aprovados = sitFiltered.filter(r => r.Status === 'Aprovado').length
               + fornSitFiltered.filter(r => r.Status === 'Aprovado').length
```

Ou seja: **cada mudança no Set dispara um único ciclo de re-render que atualiza KPIs, donuts, R3, R4 e Pendências em sincronia**.

### 3.4 Regra de visibilidade condicional dos KPIs globais

```typescript
// App.tsx
const hasFilter = selectedFornSet.size > 0

// KPIGrid.tsx
const visibleKpis = props.hideGlobal ? activeKpis : [...globalKpis, ...activeKpis]
const cols = visibleKpis.length === 6 ? 'repeat(3, 1fr)' : 'repeat(4, 1fr)'
```

| Estado do filtro | `hasFilter` | Cards renderizados | Grid |
|-----------------|-------------|-------------------|------|
| Vazio (todos) | `false` | 10 cards (2 globais + 8 ativos) | 5 colunas × 2 linhas |
| ≥1 selecionado | `true` | 8 cards (só ativos) | 4 colunas × 2 linhas |

Os 8 cards ativos são: Docs Esperados Fornecedor, Docs Esperados Terceiros, Aprovados, Não Aprovados, Não Enviados, Aguardando Submissão, Em Análise, Vencidos.

Os 2 cards globais (`Total de Fornecedores` e `Fornecedores com Execução`) não fazem sentido quando filtrado — mostrariam o total geral, não o do fornecedor selecionado, o que seria enganoso. Por isso são removidos da DOM ao invés de ficarem com valor incorreto.

### 3.5 Filtros locais dentro de cada seção

Cada seção tem seus próprios filtros locais independentes do filtro global:

```
GlobalFilter (nível App)
  → passa dado já filtrado para cada seção como prop `data`

Seção (nível interno)
  → filtra novamente localmente
  → o dado exportado (Excel/CSV/PDF) usa os registros após aplicar AMBOS os filtros
```

Isso cria um sistema de filtragem em cascata: o filtro global reduz o universo, o filtro local afina dentro desse subconjunto.

#### R3Section — filtros locais (atualizado 11/06/2026)

`R3Section.tsx` tem filtro de status local via pills multi-select:
- Estado: `statusFilters: Set<string>`
- Opções: `'Aprovado'` / `'Reprovado'` / `'Não anexado'` / `'Aguardando Submissão'` / `'Em Análise'`
- `filteredData = data.filter(r => statusFilters.has(r.Status))` (sem seleção = mostra tudo)
- `drillData`, `exportRows` e `pdfRows` dependem de `filteredData` — exports sincronizados
- Escopo isolado: zero impacto em KPIs globais, donuts ou outras seções

#### SituacaoEmpresaSection (R4)

Filtros locais: Fornecedor, Status, Documento (busca texto)

#### PendenciasSection (atualizado 11/06/2026)

Filtros locais: Fornecedor, Área, Competência, Busca texto

- **Filtro "Status" removido** — não faz sentido semântico numa seção de pendências (todas têm status de pendência por definição)
- Coluna "Status" também removida da tabela e do PDF exportado

---

## PILAR 4 — MAPEAMENTO DE UX E COMPORTAMENTO PROATIVO

### 4.1 Tooltips dos KPI Cards

Implementados via CSS puro com `group`/`group-hover` do Tailwind. Sem JavaScript de estado — o hover é tratado inteiramente por CSS transitions.

**Estrutura do HTML do tooltip:**
```html
<div class="... opacity-0 group-hover:opacity-100 transition-opacity duration-200 ...">
  {tooltip text}
  <div class="... border-t-[#1a2a35]" />  ← triângulo CSS (seta apontando para baixo)
</div>
```

O card pai tem `relative group` — o hover no pai ativa `group-hover:opacity-100` no filho.

**Mapeamento completo de tooltips:**

| Card | Cor da borda | Tooltip |
|------|-------------|---------|
| Total de Fornecedores | `#0E8FA3` (teal) | "Número total de empresas fornecedoras cadastradas na base da plataforma." |
| Fornecedores com Execução | `#0E8FA3` (teal) | "Fornecedores que possuem documentação ativa em R3 (terceiros) ou R4 (corporativo) — estão operando na plataforma." |
| Docs Esperados Fornecedor | `#0E8FA3` (teal) | "Total de documentos corporativos que o fornecedor precisa enviar (R4). Inclui todos os status." |
| Docs Esperados Terceiros | `#0E8FA3` (teal) | "Total de documentos exigidos dos funcionários ou prestadores vinculados ao fornecedor (R3). Inclui todos os status." |
| Documentos Aprovados | `#28A745` (verde) | "Documentos que foram analisados e validados pela equipe de conformidade. Estão em dia." |
| Documentos Não Aprovados | `#DC3545` (vermelho) | "Documentos que passaram por análise e foram recusados por inconformidade, dados incorretos ou prazo vencido." |
| Documentos Não Enviados | `#FFC107` (amarelo) | "Documentos obrigatórios ainda pendentes de envio pelo fornecedor ou terceiro. Exigem ação imediata." |
| Documentos Em Análise | `#F4793B` (laranja) | "Documentos já submetidos e na fila de validação pela equipe. Em breve serão aprovados ou devolvidos para ajuste." |

### 4.2 Paleta de cores e semântica

#### Cores dos KPI Cards (borda superior + valor)

| Token de cor | Hex | Semântica |
|-------------|-----|----------|
| `default` | `#0E8FA3` | Neutro / informativo |
| `green` | `#28A745` | Conforme / aprovado / positivo |
| `red` | `#DC3545` | Crítico / reprovado / negativo |
| `yellow` | `#FFC107` (borda) / `#a07800` (valor) | Atenção / pendente |
| `orange` | `#F4793B` | Em processo / aguardando |
| `gray` | `#6C757D` | Inativo / sem relevância |

#### Cores do Triple-View (donuts de conformidade)

```typescript
const COR_CONF     = '#10B981'  // Verde esmeralda — Conforme
const COR_NAO_CONF = '#EF4444'  // Vermelho — Não Conforme
```

O percentual mostrado no centro do donut é **sempre o percentual conforme**:
```typescript
const pct = total > 0 ? (conforme / total * 100).toFixed(1) : '0.0'
// "Não Conforme" = (100 - parseFloat(pct)).toFixed(1)
```

#### Cores de status nas tabelas e PDF

| Status | Cor (hex) | Aplicado em |
|--------|----------|------------|
| Aprovado | `#28A745` (verde) | Badge, PDF coluna status |
| Reprovado | `#DC3545` (vermelho) | Badge, PDF |
| Não Anexado / Não anexado | `#a07800` (amarelo escuro) | Badge, PDF |
| Em Análise / Em análise | `#0E8FA3` (teal) | Badge, PDF |
| Vencido | `#DC3545` (vermelho) | Badge, PDF |
| Aguardando Submissão | `#F4793B` (laranja) | Badge, PDF |
| TERCEIROS (área) | `#1a73e8` (azul) | Badge na tabela pendências |
| DOCUMENTOS (área) | `#c05000` (laranja escuro) | Badge "Fornecedor" |

### 4.3 Comportamento do Triple-View (3 donuts)

O `ConformidadeCharts` recebe `sitData` (R3 filtrado) e `fornData` (R4 filtrado) e computa:

```
Donut 1 — Conformidade Geral
  conforme    = aprovR3 + aprovR4
  naoConforme = (total R3 - aprovR3) + (total R4 - aprovR4)

Donut 2 — Conformidade Fornecedores
  conforme    = fornData.filter(Aprovado).length
  naoConforme = fornData.length - conforme

Donut 3 — Conformidade Terceiros
  conforme    = sitData.filter(Aprovado).length
  naoConforme = sitData.length - conforme
```

Todos os três reagem ao filtro global porque recebem arrays já filtrados do `App.tsx`.

### 4.4 Comportamento do dropdown MultiSelect

```
Estado vazio (sem seleção)    → label = "Todos os fornecedores"
1 fornecedor selecionado      → label = chave do fornecedor (nome)
≥2 fornecedores selecionados  → label = "N selecionados"
```

A busca interna do dropdown filtra por `o.label.toLowerCase().includes(search)` — busca no label formatado (que inclui o CNPJ), então o usuário pode digitar o número do CNPJ para encontrar a filial correta.

Quando ≥1 está selecionado, aparece na barra de filtro global: `"N fornecedor(es) selecionado(s) — KPIs atualizados"`.

---

## Funções utilitárias críticas

### `abbrev(name, n=40)` — normalização de nomes
Remove sufixos jurídicos (LTDA, S/A, EIRELI, ME, EPP) e trunca em 40 chars.
Aplicado em TODAS as tabelas — garante que "Karuana LTDA" e "Karuana" sejam tratados como a mesma entidade.

### `normCNPJ(v)` — normalização de CNPJs
1. Remove `.0` do formato pandas float (`"20845454000170.0"` → `"20845454000170"`)
2. Remove pontuação (`.`, `-`, `/`)
3. Faz `padStart(14, '0')` se numérico e < 14 dígitos

### `findCol(cols, ...terms)` — detecção dinâmica de colunas
```typescript
cols.find(c => terms.every(t => c.toLowerCase().includes(t.toLowerCase())))
```
Busca a PRIMEIRA coluna que contém TODOS os termos fornecidos. A ordem das colunas no CSV importa — a coluna mais específica deve ser buscada com mais termos ou com regex.

### `fmtDate(v)` — formatação de datas
Converte qualquer formato para `dd/mm/yyyy` via `Date.toLocaleDateString('pt-BR')`. Se não for uma data válida, retorna a string original.

### `extractDoc(row)` — extração do nome do documento
1. Tenta campo `Documento` diretamente
2. Faz regex na coluna `Pendência`: extrai após ` - ` ou antes da primeira `,`
3. Fallback: `'OUTROS'`

---

## Export PDF — Arquitetura

Cada seção tem seu botão "⬇ PDF" que chama uma função específica de `exportUtils.ts`. O PDF é gerado **direto dos dados** — sem screenshot de DOM.

| Função | Seção | Arquivo |
|--------|-------|---------|
| `exportR4PDF()` | Situação Empresa | `situacao_empresa.pdf` |
| `exportR3PDF()` | Situação Terceiros | `situacao_terceiros.pdf` |
| `exportPendPDF()` | Pendências | `pendencias.pdf` |

**Estrutura de cada PDF (A4 landscape):**
1. Barra de header dark teal (`#0A6A7A`) — título, "EFCAZ", data
2. Linha de mini-KPI cards com cores semânticas
3. Tabela `autoTable` com: header teal repetido por página, zebra striping, coluna Status colorida via `didParseCell`

O PDF exporta exatamente os registros visíveis no momento (após filtro global + filtros locais da seção).

---

## Glossário de termos técnicos

| Termo | Significado |
|-------|------------|
| **R3** | Situação documental de terceiros (funcionários/prestadores do fornecedor) — arquivo `situacao_terceiro_zurich.csv` |
| **R4** | Situação documental da empresa (documentação corporativa do fornecedor) — arquivo `situacao_fornecedor_zurich.csv` |
| **sitCalc** | Array R3 processado e classificado (`SitTerceiroRow[]`) — nome interno em `dataProcessing.ts` |
| **forn_sit** | Array R4 processado e classificado (`FornSitRow[]`) |
| **hasFilter** | `boolean` derivado de `selectedFornSet.size > 0` — controla visibilidade dos KPIs globais |
| **matchesForn** | Função de teste para filtro global — retorna `true` se a linha pertence ao(s) fornecedor(es) selecionado(s) |
| **fornCNPJMap** | `Record<string, string>` — mapa nome abreviado → CNPJ — usado para montar labels do dropdown |
| **abbrev** | Função que normaliza nomes de empresa removendo sufixos jurídicos e truncando |
| **colAnalise** | Coluna "Situação Análise Documento" — quando presente, tem prioridade máxima na classificação de status |

---

*Este documento descreve a versão do dashboard em `dashboard-react/` (React/TypeScript).
O dashboard Python original em `Dashboard/` não deve ser modificado — são sistemas independentes.*
