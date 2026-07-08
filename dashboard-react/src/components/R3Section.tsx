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

export function R3Section({ data, geradoEm = '' }: Props) {
  const [mode, setMode] = useState<ViewMode>('drill')
  const [pdfLoading, setPdfLoading] = useState(false)

  const drillData = useMemo(() => {
    const d: Record<string, Record<string, DrillDoc[]>> = {}
    data.forEach(r => {
      if (!d[r.Fornecedor]) d[r.Fornecedor] = {}
      if (!d[r.Fornecedor][r.Terceiro]) d[r.Fornecedor][r.Terceiro] = []
      d[r.Fornecedor][r.Terceiro].push({
        doc: r.Documento,
        status: r.Status,
        venc: r.Vencimento,
        comp: r.Competencia,
      })
    })
    return d
  }, [data])

  const exportRows = useMemo(
    () =>
      data.map(r => ({
        Fornecedor: r.Fornecedor,
        CNPJ_Forn: r.CNPJ_Forn,
        Terceiro: r.Terceiro,
        CNPJ_Terceiro: r.CNPJ_Terceiro,
        Documento: r.Documento,
        Competencia: r.Competencia,
        Status: r.Status,
        Vencimento: r.Vencimento,
      })),
    [data]
  )

  const pdfRows = useMemo(
    () =>
      data.map(r => ({
        Fornecedor: r.Fornecedor,
        Terceiro: r.Terceiro,
        CNPJ_Terceiro: r.CNPJ_Terceiro,
        Documento: r.Documento,
        Competencia: r.Competencia,
        Status: r.Status,
        Vencimento: r.Vencimento,
      })),
    [data]
  )

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

  return (
    <div id="section-r3">
      <div className="flex flex-wrap items-center gap-3 mb-4">
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
          {data.length} registro(s) ·{' '}
          {new Set(data.map(r => r.Fornecedor)).size} empresa(s) ·{' '}
          {new Set(data.map(r => r.Terceiro)).size} terceiro(s)
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

      {mode === 'drill' && <DrillDown drillData={drillData} />}
      {mode === 'grupo' && <GrupoEmpresaView data={data} />}
    </div>
  )
}
