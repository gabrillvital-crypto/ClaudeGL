import { MultiSelectDropdown } from './MultiSelectDropdown'

interface Option {
  key: string
  label: string
}

interface Props {
  fornOptions: Option[]
  selectedFornSet: Set<string>
  onFornToggle: (key: string) => void
  onFornClear: () => void
  compOptions: Option[]
  selectedCompSet: Set<string>
  onCompToggle: (key: string) => void
  onCompClear: () => void
  onClear: () => void
  onExportXLSX?: () => void
  onExportPDF?: () => void
  onExportCSV?: () => void
}

export function GlobalFilter({
  fornOptions, selectedFornSet, onFornToggle, onFornClear,
  compOptions, selectedCompSet, onCompToggle, onCompClear,
  onClear, onExportXLSX, onExportPDF, onExportCSV,
}: Props) {
  const active = selectedFornSet.size > 0 || selectedCompSet.size > 0

  const activeLabel = [
    selectedFornSet.size > 0 ? `${selectedFornSet.size} fornecedor(es)` : '',
    selectedCompSet.size > 0 ? `${selectedCompSet.size} competência(s)` : '',
  ].filter(Boolean).join(' · ') + ' selecionado(s) — KPIs atualizados'

  return (
    <div className="bg-[#0A6A7A] px-8 py-3.5 flex flex-wrap gap-5 items-end shadow-md">
      <div>
        <label className="block text-[11px] font-bold text-white/85 uppercase tracking-wide mb-1">Fornecedor</label>
        <MultiSelectDropdown
          options={fornOptions}
          selected={selectedFornSet}
          onToggle={onFornToggle}
          onClear={onFornClear}
          placeholder="Todos os fornecedores"
          minWidth="320px"
        />
      </div>

      <div>
        <label className="block text-[11px] font-bold text-white/85 uppercase tracking-wide mb-1">Competência</label>
        <MultiSelectDropdown
          options={compOptions}
          selected={selectedCompSet}
          onToggle={onCompToggle}
          onClear={onCompClear}
          placeholder="Todas as competências"
          minWidth="220px"
        />
      </div>

      <button
        onClick={onClear}
        className="bg-white/20 border border-white/50 text-white rounded px-4 py-1.5 text-[13px] font-bold hover:bg-white/35 transition-colors"
      >
        ✕ Limpar filtros
      </button>

      {(onExportXLSX || onExportPDF || onExportCSV) && (
        <div className="ml-auto">
          <label className="block text-[11px] font-bold text-white/85 uppercase tracking-wide mb-1">Exportar relatório</label>
          <div className="flex gap-1.5">
            {onExportXLSX && (
              <button onClick={onExportXLSX} title="Excel com 3 abas (R3, R4, Pendências)"
                className="bg-white/15 border border-white/40 text-white rounded px-3 py-1.5 text-[12px] font-semibold hover:bg-white/30 transition-colors">
                Excel
              </button>
            )}
            {onExportPDF && (
              <button onClick={onExportPDF} title="PDF combinado (R3, R4, Pendências)"
                className="bg-white/15 border border-white/40 text-white rounded px-3 py-1.5 text-[12px] font-semibold hover:bg-white/30 transition-colors">
                PDF
              </button>
            )}
            {onExportCSV && (
              <button onClick={onExportCSV} title="CSV único com coluna Seção"
                className="bg-white/15 border border-white/40 text-white rounded px-3 py-1.5 text-[12px] font-semibold hover:bg-white/30 transition-colors">
                CSV
              </button>
            )}
          </div>
        </div>
      )}

      {active && (
        <span className="text-white/75 text-[12px] italic self-center">
          {activeLabel}
        </span>
      )}
    </div>
  )
}
