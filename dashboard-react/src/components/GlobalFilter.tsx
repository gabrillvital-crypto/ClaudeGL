import { MultiSelectDropdown } from './MultiSelectDropdown'

interface Option {
  key: string
  label: string
}

const AEROPORTOS = ['CAIF', 'VIX', 'MEA', 'CAIN']
const STATUS_TERC_OPTIONS: { key: 'all' | 'Ativo' | 'Inativo'; label: string }[] = [
  { key: 'all',     label: 'Todos' },
  { key: 'Ativo',   label: 'Ativos' },
  { key: 'Inativo', label: 'Inativos' },
]

interface Props {
  fornOptions: Option[]
  selectedFornSet: Set<string>
  onFornToggle: (key: string) => void
  onFornClear: () => void
  compOptions: Option[]
  selectedCompSet: Set<string>
  onCompToggle: (key: string) => void
  onCompClear: () => void
  statusOptions: Option[]
  selectedStatusSet: Set<string>
  onStatusToggle: (key: string) => void
  onStatusClear: () => void
  selectedAeroportoSet: Set<string>
  onAeroportoToggle: (key: string) => void
  selectedStatusTerc: 'all' | 'Ativo' | 'Inativo'
  onStatusTercChange: (v: 'all' | 'Ativo' | 'Inativo') => void
  filtroSit: 'nao_resolvidas' | 'ativas' | 'todas'
  onFiltroSitChange: (v: 'nao_resolvidas' | 'ativas' | 'todas') => void
  totalNaoResolvidas: number
  totalAtivas: number
  totalTodas: number
  onClear: () => void
  onExportXLSX?: () => void
  onExportPDF?: () => void
  onExportCSV?: () => void
}

export function GlobalFilter({
  fornOptions, selectedFornSet, onFornToggle, onFornClear,
  compOptions, selectedCompSet, onCompToggle, onCompClear,
  statusOptions, selectedStatusSet, onStatusToggle, onStatusClear,
  selectedAeroportoSet, onAeroportoToggle,
  selectedStatusTerc, onStatusTercChange,
  filtroSit, onFiltroSitChange, totalNaoResolvidas, totalAtivas, totalTodas,
  onClear, onExportXLSX, onExportPDF, onExportCSV,
}: Props) {
  const active = selectedFornSet.size > 0 || selectedCompSet.size > 0 || selectedStatusSet.size > 0 || selectedAeroportoSet.size > 0 || selectedStatusTerc !== 'all' || filtroSit !== 'nao_resolvidas'

  const activeLabel = [
    selectedFornSet.size > 0 ? `${selectedFornSet.size} fornecedor(es)` : '',
    selectedCompSet.size > 0 ? `${selectedCompSet.size} competência(s)` : '',
    selectedStatusSet.size > 0 ? `${selectedStatusSet.size} status` : '',
    selectedAeroportoSet.size > 0 ? `aeroporto: ${[...selectedAeroportoSet].join('+')}` : '',
    selectedStatusTerc !== 'all' ? `terceiros: ${selectedStatusTerc === 'Ativo' ? 'Ativos' : 'Inativos'}` : '',
    filtroSit === 'ativas' ? 'pendências: só ativas' : filtroSit === 'todas' ? 'pendências: todas' : '',
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

      <div>
        <label className="block text-[11px] font-bold text-white/85 uppercase tracking-wide mb-1">Status</label>
        <MultiSelectDropdown
          options={statusOptions}
          selected={selectedStatusSet}
          onToggle={onStatusToggle}
          onClear={onStatusClear}
          placeholder="Todos os status"
          minWidth="260px"
        />
      </div>

      <div>
        <label className="block text-[11px] font-bold text-white/85 uppercase tracking-wide mb-1">Aeroporto</label>
        <div className="flex gap-1.5 h-[34px] items-center">
          {AEROPORTOS.map(a => (
            <button key={a} onClick={() => onAeroportoToggle(a)}
              className={`text-[12px] font-bold px-3 py-1 rounded-full border transition-colors cursor-pointer ${
                selectedAeroportoSet.has(a)
                  ? 'bg-white text-[#0A6A7A] border-white'
                  : 'bg-white/15 text-white border-white/50 hover:bg-white/30'
              }`}>
              {a}
            </button>
          ))}
        </div>
      </div>

      <div>
        <label className="block text-[11px] font-bold text-white/85 uppercase tracking-wide mb-1">Terceiros</label>
        <div className="flex gap-1.5 h-[34px] items-center">
          {STATUS_TERC_OPTIONS.map(opt => (
            <button key={opt.key} onClick={() => onStatusTercChange(opt.key)}
              className={`text-[12px] font-bold px-3 py-1 rounded-full border transition-colors cursor-pointer ${
                selectedStatusTerc === opt.key
                  ? 'bg-white text-[#0A6A7A] border-white'
                  : 'bg-white/15 text-white border-white/50 hover:bg-white/30'
              }`}>
              {opt.label}
            </button>
          ))}
        </div>
      </div>

      <div>
        <label className="block text-[11px] font-bold text-white/85 uppercase tracking-wide mb-1">Pendências</label>
        <div className="flex gap-1.5 h-[34px] items-center">
          {([
          ['nao_resolvidas', `Não resolvidas (${totalNaoResolvidas})`],
          ['ativas', `Só ativas (${totalAtivas})`],
          ['todas', `Todas (${totalTodas})`],
        ] as const).map(([val, lbl]) => (
            <button key={val} onClick={() => onFiltroSitChange(val)}
              className={`text-[12px] font-bold px-3 py-1 rounded-full border transition-colors cursor-pointer ${
                filtroSit === val
                  ? 'bg-white text-[#0A6A7A] border-white'
                  : 'bg-white/15 text-white border-white/50 hover:bg-white/30'
              }`}>
              {lbl}
            </button>
          ))}
        </div>
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
