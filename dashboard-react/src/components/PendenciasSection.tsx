import { useState, useMemo } from 'react'
import type { PendRow } from '../types'
import { exportCSV, exportXLSX, exportPendPDF } from '../utils/exportUtils'

interface Props {
  data: PendRow[]
  gfForn: string
  competencias: string[]
  geradoEm?: string
}

function statusBadge(s: string) {
  const m: Record<string, string> = {
    EM_ELABORACAO: 'bg-[#fff3cd] text-[#856404]',
    APROVADO: 'bg-[#d4edda] text-[#28A745]',
  }
  const label: Record<string, string> = {
    EM_ELABORACAO: 'Pendente',
    APROVADO: 'Aprovado c/ Pend.',
  }
  return (
    <span className={`inline-block px-2 py-0.5 rounded-full text-[11px] font-bold ${m[s] ?? 'bg-gray-100 text-gray-600'}`}>
      {label[s] ?? s}
    </span>
  )
}

function areaBadge(a: string) {
  const m: Record<string, string> = {
    TERCEIROS: 'bg-[#e8f0fe] text-[#1a73e8]',
    DOCUMENTOS: 'bg-[#fce8d5] text-[#c05000]',
  }
  const label: Record<string, string> = { TERCEIROS: 'Terceiros', DOCUMENTOS: 'Fornecedor' }
  return (
    <span className={`inline-block px-2 py-0.5 rounded-full text-[11px] font-bold ${m[a] ?? 'bg-gray-100 text-gray-600'}`}>
      {label[a] ?? a}
    </span>
  )
}

function fmtCNPJ(d: string): string {
  const n = d.replace(/\D/g, '')
  if (n.length === 11) return n.replace(/(\d{3})(\d{3})(\d{3})(\d{2})/, '$1.$2.$3-$4')
  if (n.length === 14) return n.replace(/(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})/, '$1.$2.$3/$4-$5')
  return d
}

export function PendenciasSection({ data, gfForn, competencias, geradoEm = '' }: Props) {
  const [filt, setFilt] = useState('')
  const [area, setArea] = useState('')
  const [comp, setComp] = useState('')
  const [busca, setBusca] = useState('')
  const [pdfLoading, setPdfLoading] = useState(false)

  const fornList = useMemo(() => [...new Set(data.map(r => r.Fornecedor))].sort(), [data])

  const filtered = useMemo(() => {
    let d = gfForn ? data.filter(r => r.Fornecedor === gfForn) : data
    if (filt) d = d.filter(r => r.Fornecedor === filt)
    if (area) d = d.filter(r => r.Area === area)
    if (comp) d = d.filter(r => r.Competencia === comp)
    if (busca) {
      const b = busca.toLowerCase()
      d = d.filter(r => r.Documento.toLowerCase().includes(b) || r.Detalhe.toLowerCase().includes(b))
    }
    return d
  }, [data, gfForn, filt, area, comp, busca])

  function clear() { setFilt(''); setArea(''); setComp(''); setBusca('') }

  function handlePDF() {
    setPdfLoading(true)
    setTimeout(() => {
      exportPendPDF({ rows, geradoEm })
      setPdfLoading(false)
    }, 50)
  }

  const rows = filtered.map(r => ({
    Fornecedor: r.Fornecedor,
    CNPJ: fmtCNPJ(r.CNPJ_Forn),
    Area: r.Area,
    Documento: r.Documento,
    Competencia: r.Competencia,
    Detalhe: r.Detalhe,
  }))

  return (
    <div id="section-pendencias">
      {/* Filters */}
      <div className="bg-white rounded-xl shadow-sm p-4 mb-3 flex flex-wrap gap-3 items-end">
        <div>
          <label className="block text-[12px] font-bold text-[#0E8FA3] uppercase mb-1">Fornecedor</label>
          <select value={filt} onChange={e => setFilt(e.target.value)} className="border border-[#cde] rounded px-2 py-1.5 text-[13px]">
            <option value="">Todos</option>
            {fornList.map(f => <option key={f} value={f}>{f}</option>)}
          </select>
        </div>
        <div>
          <label className="block text-[12px] font-bold text-[#0E8FA3] uppercase mb-1">Área</label>
          <select value={area} onChange={e => setArea(e.target.value)} className="border border-[#cde] rounded px-2 py-1.5 text-[13px]">
            <option value="">Todas</option>
            <option value="TERCEIROS">Terceiros</option>
            <option value="DOCUMENTOS">Documental</option>
          </select>
        </div>
        {competencias.length > 0 && (
          <div>
            <label className="block text-[12px] font-bold text-[#0E8FA3] uppercase mb-1">Competência</label>
            <select value={comp} onChange={e => setComp(e.target.value)} className="border border-[#cde] rounded px-2 py-1.5 text-[13px]">
              <option value="">Todas</option>
              {competencias.map(c => <option key={c} value={c}>{c}</option>)}
            </select>
          </div>
        )}
        <div>
          <label className="block text-[12px] font-bold text-[#0E8FA3] uppercase mb-1">Buscar</label>
          <input value={busca} onChange={e => setBusca(e.target.value)} placeholder="Documento ou pendência..." className="border border-[#cde] rounded px-2 py-1.5 text-[13px] w-48" />
        </div>
        <button onClick={clear} className="bg-[#0E8FA3] text-white rounded px-3 py-1.5 text-[13px] font-semibold hover:bg-[#0a7a8d]">Limpar</button>
        <div className="ml-auto flex items-center gap-1.5">
          <span className="text-[11px] text-[#999] font-semibold uppercase mr-1">Exportar:</span>
          <button onClick={() => exportXLSX(rows, 'pendencias_zurich')} className="bg-[#28A745] text-white rounded px-3 py-1.5 text-[13px] font-semibold hover:bg-[#1e7e34]">Excel</button>
          <button onClick={() => exportCSV(rows, 'pendencias_zurich')} className="bg-[#6C757D] text-white rounded px-3 py-1.5 text-[13px] font-semibold hover:bg-[#545b62]">CSV</button>
          <button onClick={handlePDF} disabled={pdfLoading} className="bg-[#DC3545] text-white rounded px-3 py-1.5 text-[13px] font-semibold hover:bg-[#b02a37] disabled:opacity-60 disabled:cursor-wait flex items-center gap-1">
            {pdfLoading ? '⏳' : '⬇'} PDF
          </button>
        </div>
      </div>

      {/* Table */}
      <div className="bg-white rounded-xl shadow-sm p-4">
        <p className="text-[13px] text-[#6C757D] mb-2">{filtered.length} pendência(s) de {data.length} no total</p>
        <div className="overflow-x-auto">
          <table className="w-full text-[13px] border-collapse">
            <thead>
              <tr className="bg-[#0E8FA3] text-white">
                {['Fornecedor', 'Área', 'Documento', 'Competência', 'Detalhe'].map(h => (
                  <th key={h} className="px-3 py-2.5 text-left font-bold">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {filtered.map((r, i) => (
                <tr key={i} className={`border-b border-[#e5eef1] hover:bg-[#d4eef3] ${i % 2 === 1 ? 'bg-[#f0f8fa]' : ''}`}>
                  <td className="px-3 py-2">
                    <div className="font-medium">{r.Fornecedor}</div>
                    {r.CNPJ_Forn && <div className="text-[11px] text-[#999] font-mono mt-0.5">{fmtCNPJ(r.CNPJ_Forn)}</div>}
                  </td>
                  <td className="px-3 py-2">{areaBadge(r.Area)}</td>
                  <td className="px-3 py-2 font-semibold">{r.Documento}</td>
                  <td className="px-3 py-2">
                    {r.Competencia
                      ? <span className="bg-[#e8f7fa] text-[#0E8FA3] text-[11px] px-2 py-0.5 rounded">{r.Competencia}</span>
                      : <span className="text-[#ccc]">—</span>}
                  </td>
                  <td className="px-3 py-2 text-[12px] text-[#666] break-words" style={{ minWidth: '240px', maxWidth: '420px' }}>{r.Detalhe}</td>
                </tr>
              ))}
              {filtered.length === 0 && (
                <tr><td colSpan={5} className="px-3 py-6 text-center text-[#999]">Nenhuma pendência encontrada</td></tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
