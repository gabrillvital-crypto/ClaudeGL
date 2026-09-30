# Feature: Seção Evolução por Competência
**Status:** ⚠️ Dados ambíguos — validar com Débora antes de aplicar ao main
**Commits:** `c9c4e59` (versão gráfico) · `0425bd7` (versão tabela — versão final)

---

## O que faz

Adiciona uma seção abaixo dos 3 donuts de conformidade mostrando a evolução mensal
dos terceiros por competência, com base no **Relatório de Competências** exportado da plataforma.

### Visual

**4 KPI chips:**
| Chip | Dado |
|---|---|
| Competências com dados | Qtde de meses com terceiros registrados na série |
| Declaração de não atividade | Total de declarações (coluna H) na série — substituiu "Pico de terceiros" em 30/09 |
| Total acumulado | Soma de todos os terceiros na série |
| % Aprovados (série) | Percentual de submissões aprovadas; último mês no subtítulo |

**Tabela paginada (10 linhas/página):**
| Coluna | Descrição |
|---|---|
| Competência | Mês por extenso (ex: "Dezembro/2025") — ordenado cronologicamente |
| Qtd Fornecedores | Quantos CNPJs distintos têm registros naquele mês |
| Total Terceiros | Soma de Qtd Terceiros de todas as submissões do mês |
| Pendências 🟡 | Terceiros em submissões com status EM_ELABORACAO (antes "Em Elaboração") |
| Aprovados 🟢 | Terceiros em submissões com status APROVADO |
| % Aprovado | Barra de progresso colorida: 🔴 <40% · 🟡 40–70% · 🟢 >70% |

**Rodapé:** nota de fonte + aviso de exclusão de competências futuras e "A classificar"

---

## Ajuste 30/09/2026 — Filtro global de fornecedor

A seção agora respeita o filtro global de fornecedor do topo do dash.
- Casa por **CNPJ** (só dígitos), porque o nome no Relatório de Competências pode divergir do nome em R3/R4/contratos.
- Se o item selecionado não tiver CNPJ, cai para o **nome normalizado** (trim + maiúsculas).
- Ao trocar o filtro, a paginação volta para a página 1.
- Se o fornecedor selecionado não tiver competências, a seção mostra: "Fornecedor selecionado não possui competências neste relatório".
- Arquivos: `App.tsx` (passa `selectedFornSet`) e `CompetenciasSection.tsx`.

---

## Ajuste 30/09/2026 (2) — Pendências, não atividade e nova base

- Coluna "Em Elaboração" renomeada para **Pendências**. A regra de cálculo não mudou: soma os terceiros das solicitações que não estão como APROVADO.
- Card "Pico de terceiros" substituído por **Declaração de não atividade**, que lê a coluna H "Possui declaração de não atividade?". Mostra o total de declarações na série e em quantas competências aparecem.
- Linha de fornecedor com "Sim" na coluna H, ou com "-" em Qtd Terceiros, **não soma números**.
- Se todos os fornecedores de uma competência declararam não atividade, a linha mostra "-" nas colunas numéricas. Com declaração parcial, aparece "N s/ atividade" abaixo de Qtd Fornecedores.
- CNPJ normalizado para 14 dígitos nos dois lados do filtro.
- Base atualizada: relatório exportado em 30/09/2026, com 644 linhas e 46 CNPJs. Nenhuma declaração de não atividade nesta base.

---

## Ajuste 30/09/2026 (3) — Regulares × Pendências pelas colunas do relatório

A plataforma corrigiu a divisão entre Regulares e Com pendências. Na base de 30/09, Regulares + Com pendências = Qtd Terceiros em todas as linhas.
- **Pendências** agora soma a coluna "Com pendências".
- **Aprovados** virou **Regulares** e soma a coluna "Regulares".
- **% Aprovado** virou **% Regular** (regulares ÷ total). O card da série virou "% regulares (série)".
- O "Status da solicitação" (APROVADO / EM_ELABORACAO) deixou de ser usado nos números.
- Isso resolve boa parte do alerta abaixo, que fica como histórico.

---

## ⚠️ ALERTA — Interpretação dos dados

**Antes de aplicar ao main, validar com Débora as seguintes questões:**

### O que cada status realmente significa?

| Status no CSV | O que representa |
|---|---|
| `APROVADO` | A *solicitação mensal* do fornecedor foi aprovada pelo BPO — não garante que os documentos dos terceiros estão ok |
| `EM_ELABORACAO` | A solicitação está em aberto/rascunho — pode ter documentos enviados ou não, o CSV não diz |

### Evidência da ambiguidade
Em TODAS as linhas do CSV (inclusive as APROVADO):
- `Regulares = 0`
- `Com pendências = Qtd Terceiros`

Ou seja: mesmo submissões APROVADAS têm 100% de terceiros com pendências. Isso indica que "Aprovado" é status de **processo**, não de **conformidade documental**.

### Perguntas para a Débora

1. O que significa exatamente `EM_ELABORACAO`? É:
   - (a) O fornecedor não enviou nenhum documento ainda?
   - (b) O fornecedor enviou mas o BPO ainda não processou?
   - (c) O ciclo está aberto mas pode ter envios parciais?

2. Por que `Regulares = 0` mesmo nas competências APROVADAS?

3. Esse relatório é gerado por qual usuário/perfil no sistema?

### Relação com R3

A conformidade documental individual dos terceiros está no **R3** (já no dashboard):
- `Aprovado` → documento em dia
- `Reprovado` → enviado mas rejeitado
- `Aguardando Submissão` → notificado, não enviou
- `Não Anexado` → nunca enviou

O Relatório de Competências e o R3 são **complementares**, não substitutos.
Usar o CSV de competências para inferir conformidade documental é incorreto.

---

## Arquivo CSV necessário

**Nome:** `competencias_zurich.csv`
**Local:** `dashboard-react/public/data/`
**Origem:** Exportar no menu da plataforma Efcaz → Relatório de Competências

**Colunas esperadas:**
```
Fornecedor, Fornecedor CPF/CNPJ, Status da solicitação,
Competência, Qtd Terceiros, Regulares, Com pendências,
Possui declaração de não atividade?, Mensagem de declaração de não atividade
```

**Atualização:** manual — exportar nova base da plataforma e substituir o arquivo.

---

## Arquivos envolvidos

### Novo: `CompetenciasSection.tsx`
Componente autônomo — carrega e processa o próprio CSV via `fetch`.
Não depende do pipeline principal de dados (`useDashboardData`).

```tsx
// Uso no App.tsx:
import { CompetenciasSection } from './components/CompetenciasSection'

// No JSX, após <ConformidadeCharts>:
<Section title="Evolução de Terceiros por Competência">
  <CompetenciasSection />
</Section>
```

### Dados excluídos automaticamente pelo componente
- Competências com `Total Terceiros = 0` (meses futuros ou sem atividade)
- Competência `"A classificar"` (não tem data, não entra na série temporal)

### Novo: `public/data/competencias_zurich.csv`
Base de 30/09/2026. Atualizar a cada novo relatório exportado da plataforma.

---

## Checklist antes de aplicar ao main

- [ ] Validar com Débora o significado de EM_ELABORACAO e APROVADO
- [ ] Confirmar por que Regulares = 0 em todas as linhas (inclusive APROVADO)
- [ ] Definir label correto para as colunas (se não for "Aprovados", o que seria?)
- [ ] Avaliar se a seção deve ficar abaixo dos donuts ou em outro local do dash
- [ ] Atualizar o CSV com base mais recente antes de subir para produção
- [ ] Considerar se vale cruzar com R3 para enriquecer a leitura
