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
}

export function GlobalFilter({
  fornOptions, selectedFornSet, onFornToggle, onFornClear,
  compOptions, selectedCompSet, onCompToggle, onCompClear,
  onClear,
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

      {active && (
        <span className="text-white/75 text-[12px] italic ml-auto self-center">
          {activeLabel}
        </span>
      )}
    </div>
  )
}
