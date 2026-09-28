# Feature: Exportação Personalizada e Contextual
**Status:** ✅ Pronta para produção
**Commit:** `3e5fcc9`

---

## O que faz

Substitui os 3 botões separados (Excel / PDF / CSV) da barra de filtros por um único botão
**"📋 Exportar Relatório"** que abre uma modal com seleção personalizada de módulos e formato.

### Comportamento

1. Usuário clica em **Exportar Relatório** na barra de filtros (canto direito)
2. Modal abre herdando automaticamente o filtro ativo da tela
3. Usuário seleciona quais módulos incluir via checkbox:
   - 👥 Situação Documental — Terceiros (R3)
   - 🏢 Situação Documental — Empresa (R4)
   - 📋 Detalhamento de Pendências
4. Usuário escolhe o formato: **Excel (.xlsx)** ou **PDF**
5. Clica em **Gerar Relatório** → download automático

### Regras de comportamento

- **Filtro herdado:** se a tela está filtrada por fornecedor X, o relatório sai só com dados de X
- **Badge de contexto:** a modal mostra uma caixinha teal "🔍 Filtro ativo" com o resumo dos filtros
- **Sem filtro:** exibe aviso neutro "relatório incluirá todos os fornecedores"
- **Contagem por módulo:** cada checkbox mostra quantos registros serão exportados com o filtro atual
- **Botão desabilitado:** se nenhum módulo estiver marcado, o botão Gerar fica cinza/inativo
- **Fechar:** clica no X, no botão Cancelar ou fora da modal

### Formatos gerados

| Formato | Estrutura |
|---|---|
| Excel | Uma aba por módulo selecionado (R3 - Terceiros / R4 - Empresa / Pendências) |
| PDF | Documento único paginado com seções por módulo, cabeçalho Efcaz, rodapé com nº de página |

---

## Arquivos envolvidos

### Novo: `ExportModal.tsx`
Componente modal completo. Props:
```tsx
open: boolean
onClose: () => void
sitRows: SitTerceiroRow[]      // dados R3 já filtrados
fornSitRows: FornSitRow[]      // dados R4 já filtrados
pendRows: PendRow[]            // dados pendências já filtrados
geradoEm: string
filterSummary: string          // texto resumo dos filtros ativos
hasFilter: boolean
```

### Modificado: `exportUtils.ts`
Duas novas funções adicionadas:

```ts
exportPersonalizadoXLSX({
  sitRows, fornSitRows, pendRows,
  includeR3: boolean,
  includeR4: boolean,
  includePend: boolean,
  filename?: string
})

exportPersonalizadoPDF({
  sitRows, fornSitRows, pendRows,
  includeR3, includeR4, includePend,
  geradoEm: string,
  filename?: string
})
```

### Modificado: `GlobalFilter.tsx`
- **Removido:** props `onExportXLSX`, `onExportPDF`, `onExportCSV`
- **Adicionado:** prop `onOpenExport?: () => void`
- **Visual:** 3 botões → 1 botão branco com texto "📋 Exportar Relatório"

### Modificado: `App.tsx`
```tsx
// Estado da modal
const [showExportModal, setShowExportModal] = useState(false)

// Resumo legível dos filtros (passado para a modal)
const filterSummary = useMemo(() => { ... }, [...filtros])

// GlobalFilter: substituição das props
onOpenExport={() => setShowExportModal(true)}

// Modal no JSX (dentro do div#dashboard-root, após o conteúdo)
<ExportModal
  open={showExportModal}
  onClose={() => setShowExportModal(false)}
  sitRows={sitFiltered}
  fornSitRows={fornSitFiltered}
  pendRows={tabelaFiltered}
  geradoEm={data.geradoEm}
  filterSummary={filterSummary}
  hasFilter={hasFilter}
/>
```

---

## Checklist antes de aplicar ao main

- [ ] Testar exportação Excel com todos os 3 módulos selecionados
- [ ] Testar exportação Excel com apenas 1 módulo selecionado
- [ ] Testar exportação PDF com filtro de fornecedor ativo
- [ ] Testar exportação PDF sem filtro (todos os dados)
- [ ] Confirmar que o botão Gerar fica desabilitado sem módulo selecionado
- [ ] Confirmar que a modal fecha ao clicar fora
- [ ] Validar visual no mobile (responsividade)
