import { useState } from 'react'
import type { SitTerceiroRow, FornSitRow, PendRow } from '../types'
import { exportPersonalizadoXLSX, exportPersonalizadoPDF } from '../utils/exportUtils'

interface Props {
  open: boolean
  onClose: () => void
  sitRows: SitTerceiroRow[]
  fornSitRows: FornSitRow[]
  pendRows: PendRow[]
  geradoEm: string
  filterSummary: string
  hasFilter: boolean
}

const MODULES = [
  {
    key: 'r3' as const,
    label: 'Situação Documental — Terceiros (R3)',
    desc: 'Status de documentação por terceiro credenciado, agrupado por fornecedor',
    icon: '👥',
  },
  {
    key: 'r4' as const,
    label: 'Situação Documental — Empresa (R4)',
    desc: 'Documentação corporativa dos fornecedores (FGTS, Certidões, etc.)',
    icon: '🏢',
  },
  {
    key: 'pendencias' as const,
    label: 'Detalhamento de Pendências',
    desc: 'Pendências agrupadas por competência, com situação e área',
    icon: '📋',
  },
]

type ModuleKey = typeof MODULES[number]['key']
type Format    = 'xlsx' | 'pdf'

export function ExportModal({
  open, onClose,
  sitRows, fornSitRows, pendRows,
  geradoEm, filterSummary, hasFilter,
}: Props) {
  const [selected,   setSelected]   = useState<Set<ModuleKey>>(new Set(['r3', 'r4', 'pendencias']))
  const [format,     setFormat]     = useState<Format>('xlsx')
  const [exporting,  setExporting]  = useState(false)

  if (!open) return null

  const toggle = (key: ModuleKey) =>
    setSelected(prev => {
      const next = new Set(prev)
      next.has(key) ? next.delete(key) : next.add(key)
      return next
    })

  const counts: Record<ModuleKey, number> = {
    r3:        sitRows.length,
    r4:        fornSitRows.length,
    pendencias: pendRows.length,
  }

  const noneSelected = selected.size === 0

  const handleExport = () => {
    if (noneSelected) return
    setExporting(true)
    try {
      const opts = {
        sitRows,
        fornSitRows,
        pendRows,
        includeR3:    selected.has('r3'),
        includeR4:    selected.has('r4'),
        includePend:  selected.has('pendencias'),
      }
      if (format === 'xlsx') {
        exportPersonalizadoXLSX(opts)
      } else {
        exportPersonalizadoPDF({ ...opts, geradoEm })
      }
      onClose()
    } finally {
      setExporting(false)
    }
  }

  // Fecha ao clicar no overlay
  const handleOverlay = (e: React.MouseEvent<HTMLDivElement>) => {
    if (e.target === e.currentTarget) onClose()
  }

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm"
      onClick={handleOverlay}
    >
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-lg mx-4 overflow-hidden animate-in">

        {/* ── Header ── */}
        <div className="bg-[#0A6A7A] px-6 py-4 flex items-center justify-between">
          <div>
            <h2 className="text-white font-bold text-lg leading-tight">Exportar Relatório</h2>
            <p className="text-white/65 text-[12px] mt-0.5">Selecione os módulos e o formato de saída</p>
          </div>
          <button
            onClick={onClose}
            className="text-white/60 hover:text-white transition-colors text-xl leading-none w-8 h-8 flex items-center justify-center rounded-lg hover:bg-white/15"
          >
            ✕
          </button>
        </div>

        <div className="p-6 space-y-5">

          {/* ── Contexto do filtro ── */}
          {hasFilter ? (
            <div className="bg-[#e8f6f8] border border-[#0E8FA3]/40 rounded-xl px-4 py-3">
              <p className="text-[11px] font-bold text-[#0A6A7A] uppercase tracking-wide mb-1">
                🔍 Filtro ativo — exportação com dados filtrados
              </p>
              <p className="text-[12px] text-[#1a4f5c] leading-relaxed">{filterSummary}</p>
            </div>
          ) : (
            <div className="bg-gray-50 border border-gray-200 rounded-xl px-4 py-3">
              <p className="text-[12px] text-gray-500">
                Nenhum filtro ativo — o relatório incluirá <span className="font-semibold text-gray-700">todos os fornecedores</span>
              </p>
            </div>
          )}

          {/* ── Seleção de módulos ── */}
          <div>
            <p className="text-[11px] font-bold text-gray-500 uppercase tracking-wide mb-2.5">
              Módulos a incluir
            </p>
            <div className="space-y-2">
              {MODULES.map(mod => {
                const isChecked = selected.has(mod.key)
                const count     = counts[mod.key]
                return (
                  <label
                    key={mod.key}
                    className={`flex items-start gap-3 p-3.5 rounded-xl border cursor-pointer transition-all select-none ${
                      isChecked
                        ? 'bg-[#e8f6f8] border-[#0E8FA3] shadow-sm'
                        : 'bg-gray-50 border-gray-200 hover:border-[#0E8FA3]/40 hover:bg-[#f0fafb]'
                    }`}
                  >
                    <input
                      type="checkbox"
                      checked={isChecked}
                      onChange={() => toggle(mod.key)}
                      className="mt-0.5 w-4 h-4 accent-[#0E8FA3] cursor-pointer shrink-0"
                    />
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center justify-between gap-2 flex-wrap">
                        <span className={`text-[13px] font-semibold ${isChecked ? 'text-[#0A6A7A]' : 'text-gray-700'}`}>
                          {mod.icon} {mod.label}
                        </span>
                        <span className={`text-[11px] font-bold px-2 py-0.5 rounded-full shrink-0 ${
                          count > 0
                            ? isChecked
                              ? 'bg-[#0E8FA3]/20 text-[#0A6A7A]'
                              : 'bg-gray-200 text-gray-500'
                            : 'bg-gray-100 text-gray-400'
                        }`}>
                          {count.toLocaleString('pt-BR')} reg.
                        </span>
                      </div>
                      <p className="text-[11px] text-gray-400 mt-0.5 leading-relaxed">{mod.desc}</p>
                    </div>
                  </label>
                )
              })}
            </div>
            {noneSelected && (
              <p className="text-[11px] text-red-500 mt-2 flex items-center gap-1">
                ⚠ Selecione ao menos um módulo para exportar
              </p>
            )}
          </div>

          {/* ── Formato ── */}
          <div>
            <p className="text-[11px] font-bold text-gray-500 uppercase tracking-wide mb-2.5">
              Formato de saída
            </p>
            <div className="flex gap-2">
              {([
                { key: 'xlsx' as const, label: '📊 Excel (.xlsx)', desc: 'Uma aba por módulo' },
                { key: 'pdf'  as const, label: '📄 PDF',           desc: 'Documento único paginado' },
              ]).map(f => (
                <button
                  key={f.key}
                  onClick={() => setFormat(f.key)}
                  className={`flex-1 py-3 px-4 rounded-xl text-left border transition-all ${
                    format === f.key
                      ? 'bg-[#0E8FA3] text-white border-[#0E8FA3] shadow-sm'
                      : 'bg-white text-gray-600 border-gray-300 hover:border-[#0E8FA3]/50 hover:bg-[#f0fafb]'
                  }`}
                >
                  <div className="text-[13px] font-bold">{f.label}</div>
                  <div className={`text-[10px] mt-0.5 ${format === f.key ? 'text-white/70' : 'text-gray-400'}`}>
                    {f.desc}
                  </div>
                </button>
              ))}
            </div>
          </div>

        </div>

        {/* ── Footer ── */}
        <div className="px-6 py-4 bg-gray-50 border-t border-gray-200 flex items-center justify-between gap-3">
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 text-[13px] font-medium transition-colors"
          >
            Cancelar
          </button>
          <button
            onClick={handleExport}
            disabled={noneSelected || exporting}
            className={`px-6 py-2.5 rounded-xl text-[13px] font-bold transition-all ${
              noneSelected || exporting
                ? 'bg-gray-200 text-gray-400 cursor-not-allowed'
                : 'bg-[#0E8FA3] text-white hover:bg-[#0A6A7A] shadow-sm cursor-pointer'
            }`}
          >
            {exporting
              ? 'Gerando...'
              : `Gerar Relatório${selected.size > 0 ? ` (${selected.size} módulo${selected.size !== 1 ? 's' : ''})` : ''}`
            }
          </button>
        </div>

      </div>
    </div>
  )
}
