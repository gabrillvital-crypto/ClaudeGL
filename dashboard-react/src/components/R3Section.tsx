import { useState, useMemo, useRef } from 'react'
import type { SitTerceiroRow, DrillDoc } from '../types'
import { DrillDown } from './DrillDown'
import { GrupoEmpresaView } from './GrupoEmpresaView'
import { exportCSV, exportXLSX, exportR3PDF } from '../utils/exportUtils'

interface Props {
  data: SitTerceiroRow[]
  geradoEm?: string
}

type ViewMode = 'drill' | 'grupo'

const STATUS_OPTIONS: { value: string; label: string; active: string; inactive: string }[] = [
  { value: 'Aprovado',             label: 'Aprovado',          active: 'bg-[#28A745] text-white',                   inactive: 'bg-white text-[#28A745] border border-[#28A745] hover:bg-[#eafaf1]' },
  { value: 'Reprovado',            label: 'Reprovado',         active: 'bg-[#DC3545] text-white',                   inactive: 'bg-white text-[#DC3545] border border-[#DC3545] hover:bg-[#fdf2f3]' },
  { value: 'Não anexado',          label: 'Não Enviado',       active: 'bg-[#FFC107] text-[#5a3e00]',               inactive: 'bg-white text-[#a07800] border border-[#FFC107] hover:bg-[#fffbea]' },
  { value: 'Aguardando Submissão', label: 'Aguard. Submissão', active: 'bg-[#fd7e14] text-white',                   inactive: 'bg-white text-[#c05000] border border-[#fd7e14] hover:bg-[#fff4ec]' },
  { value: 'Em Análise',           label: 'Em Análise',        active: 'bg-[#F4793B] text-white',                   inactive: 'bg-white text-[#F4793B] border border-[#F4793B] hover:bg-[#fff1eb]' },
]

export function R3Section({ data, geradoEm = '' }: Props) {
  const [mode, setMode] = useState<ViewMode>('drill')
  const [pdfLoading, setPdfLoading] = useState(false)
  const [statusFilters, setStatusFilters] = useState<Set<string>>(new Set())
  const [compFilters, setCompFilters] = useState<Set<string>>(new Set())

  function toggleStatus(v: string) {
    setStatusFilters(prev => {
      const next = new Set(prev)
      next.has(v) ? next.delete(v) : next.add(v)
      return next
    })
  }

  function toggleComp(v: string) {
    setCompFilters(prev => {
      const next = new Set(prev)
      next.has(v) ? next.delete(v) : next.add(v)
      return next
    })
  }

  const competencias = useMemo(() => {
    const s = new Set(data.map(r => r.Competencia).filter(Boolean))
    return [...s].sort()
  }, [data])

  // Filtragem local por status + competência — age após o filtro global de fornecedores (já aplicado em data)
  const filteredData = useMemo(() => {
    let d = data
    if (statusFilters.size > 0) d = d.filter(r => statusFilters.has(r.Status))
    if (compFilters.size > 0) d = d.filter(r => compFilters.has(r.Competencia))
    return d
  }, [data, statusFilters, compFilters])

  const drillData = useMemo(() => {
    const d: Record<string, Record<string, DrillDoc[]>> = {}
    filteredData.forEach(r => {
      if (!d[r.Fornecedor]) d[r.Fornecedor] = {}
      if (!d[r.Fornecedor][r.Terceiro]) d[r.Fornecedor][r.Terceiro] = []
      d[r.Fornecedor][r.Terceiro].push({
        doc: r.Documento,
        status: r.Status,
        venc: r.Vencimento,
      })
    })
    return d
  }, [filteredData])

  const exportRows = useMemo(
    () =>
      filteredData.map(r => ({
        Fornecedor: r.Fornecedor,
        Terceiro: r.Terceiro,
        Documento: r.Documento,
        Competencia: r.Competencia,
        Status: r.Status,
        Vencimento: r.Vencimento,
      })),
    [filteredData]
  )

  const pdfRows = useMemo(
    () =>
      filteredData.map(r => ({
        Fornecedor: r.Fornecedor,
        Terceiro: r.Terceiro,
        CNPJ_Terceiro: r.CNPJ_Terceiro,
        Documento: r.Documento,
        Competencia: r.Competencia,
        Status: r.Status,
        Vencimento: r.Vencimento,
      })),
    [filteredData]
  )

  // Ref sempre sincronizado inline — garante que o setTimeout captura o valor mais atual
  const pdfRowsRef = useRef(pdfRows)
  pdfRowsRef.current = pdfRows

  function handlePDF() {
    const snapshot = pdfRowsRef.current
    setPdfLoading(true)
    setTimeout(() => {
      exportR3PDF({ rows: snapshot, geradoEm })
      setPdfLoading(false)
    }, 50)
  }

  const activeLabel = (statusFilters.size > 0 || compFilters.size > 0)
    ? `${filteredData.length} de ${data.length} registro(s)`
    : `${data.length} registro(s)`

  return (
    <div id="section-r3">
      {/* Linha 1: toggle de modo + contagem + exportação */}
      <div className="flex flex-wrap items-center gap-3 mb-2">
        <div className="flex bg-white border border-[#cde] rounded-lg overflow-hidden shadow-sm">
          <button
            onClick={() => setMode('drill')}
            className={`px-4 py-2 text-[13px] font-bold transition-colors ${
              mode === 'drill' ? 'bg-[#0E8FA3] text-white' : 'text-[#0E8FA3] hover:bg-[#e8f7fa]'
            }`}
          >
            🔍 Drill-Down
          </button>
          <button
            onClick={() => setMode('grupo')}
            className={`px-4 py-2 text-[13px] font-bold transition-colors border-l border-[#cde] ${
              mode === 'grupo' ? 'bg-[#0E8FA3] text-white' : 'text-[#0E8FA3] hover:bg-[#e8f7fa]'
            }`}
          >
            🏢 Agrupado por Empresa
          </button>
        </div>

        <span className="text-[12px] text-[#888]">
          {activeLabel} ·{' '}
          {new Set(filteredData.map(r => r.Fornecedor)).size} empresa(s) ·{' '}
          {new Set(filteredData.map(r => r.Terceiro)).size} terceiro(s)
        </span>

        <div className="ml-auto flex items-center gap-1.5">
          <span className="text-[11px] text-[#999] font-semibold uppercase mr-1">Exportar:</span>
          <button
            onClick={() => exportXLSX(exportRows, 'situacao_terceiros')}
            className="bg-[#28A745] text-white rounded px-3 py-1.5 text-[13px] font-semibold hover:bg-[#1e7e34]"
          >
            Excel
          </button>
          <button
            onClick={() => exportCSV(exportRows, 'situacao_terceiros')}
            className="bg-[#6C757D] text-white rounded px-3 py-1.5 text-[13px] font-semibold hover:bg-[#545b62]"
          >
            CSV
          </button>
          <button
            onClick={handlePDF}
            disabled={pdfLoading}
            className="bg-[#DC3545] text-white rounded px-3 py-1.5 text-[13px] font-semibold hover:bg-[#b02a37] disabled:opacity-60 disabled:cursor-wait flex items-center gap-1"
          >
            {pdfLoading ? '⏳' : '⬇'} PDF
          </button>
        </div>
      </div>

      {/* Linha 2: filtro de status local */}
      <div className="flex flex-wrap items-center gap-2 mb-2 bg-white border border-[#e5eef1] rounded-lg px-3 py-2 shadow-sm">
        <span className="text-[11px] font-bold text-[#0E8FA3] uppercase tracking-wide mr-1">
          Status:
        </span>
        {STATUS_OPTIONS.map(opt => (
          <button
            key={opt.value}
            onClick={() => toggleStatus(opt.value)}
            className={`px-3 py-1 rounded-full text-[11px] font-bold transition-all ${
              statusFilters.has(opt.value) ? opt.active : opt.inactive
            }`}
          >
            {opt.label}
          </button>
        ))}
        {statusFilters.size > 0 && (
          <button
            onClick={() => setStatusFilters(new Set())}
            className="ml-2 text-[11px] text-[#999] hover:text-[#DC3545] underline font-semibold"
          >
            Limpar
          </button>
        )}
      </div>

      {/* Linha 3: filtro de competência */}
      {competencias.length > 0 && (
        <div className="flex flex-wrap items-center gap-2 mb-4 bg-white border border-[#e5eef1] rounded-lg px-3 py-2 shadow-sm">
          <span className="text-[11px] font-bold text-[#0E8FA3] uppercase tracking-wide mr-1">
            Competência:
          </span>
          {competencias.map(comp => (
            <button
              key={comp}
              onClick={() => toggleComp(comp)}
              className={`px-3 py-1 rounded-full text-[11px] font-bold transition-all ${
                compFilters.has(comp)
                  ? 'bg-[#0E8FA3] text-white'
                  : 'bg-white text-[#0E8FA3] border border-[#0E8FA3] hover:bg-[#e8f7fa]'
              }`}
            >
              {comp}
            </button>
          ))}
          {compFilters.size > 0 && (
            <button
              onClick={() => setCompFilters(new Set())}
              className="ml-2 text-[11px] text-[#999] hover:text-[#DC3545] underline font-semibold"
            >
              Limpar
            </button>
          )}
        </div>
      )}


      {/* Conteúdo: Drill-Down ou Modo Agrupado */}
      {mode === 'drill' && <DrillDown drillData={drillData} />}
      {mode === 'grupo' && <GrupoEmpresaView data={filteredData} />}
    </div>
  )
}
