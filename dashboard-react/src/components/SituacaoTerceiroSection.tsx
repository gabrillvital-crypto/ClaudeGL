import { useState, useMemo } from 'react'
import type { SitTerceiroRow } from '../types'
import { exportCSV, exportXLSX, exportR3PDF } from '../utils/exportUtils'

interface Props { data: SitTerceiroRow[]; gfForn: string; geradoEm?: string }

function badge(s: string) {
  const m: Record<string, string> = {
    'Aprovado':              'bg-[#d4edda] text-[#28A745]',
    'Reprovado':             'bg-[#ffeaea] text-[#DC3545]',
    'Não anexado':           'bg-[#fff3cd] text-[#856404]',
    'Aguardando Submissão':  'bg-[#fff3cd] text-[#856404]',
    'Em Análise':            'bg-[#e8f4f7] text-[#0E8FA3]',
  }
  return <span className={`inline-block px-2 py-0.5 rounded-full text-[11px] font-bold ${m[s] ?? 'bg-gray-100 text-gray-600'}`}>{s}</span>
}

export function SituacaoTerceiroSection({ data, gfForn, geradoEm = '' }: Props) {
  const [filt, setFilt] = useState('')
  const [stat, setStat] = useState('')
  const [busca, setBusca] = useState('')
  const [pdfLoading, setPdfLoading] = useState(false)

  const filtered = useMemo(() => {
    let d = gfForn ? data.filter(r => r.Fornecedor === gfForn) : data
    if (filt) d = d.filter(r => r.Fornecedor === filt)
    if (stat) d = d.filter(r => r.Status === stat)
    if (busca) d = d.filter(r => r.Documento.toLowerCase().includes(busca.toLowerCase()))
    return d
  }, [data, gfForn, filt, stat, busca])

  const fornList = useMemo(() => [...new Set(data.map(r => r.Fornecedor))].sort(), [data])

  function clear() { setFilt(''); setStat(''); setBusca('') }

  const rows = filtered.map(r => ({
    Fornecedor: r.Fornecedor,
    Terceiro: r.Terceiro,
    Documento: r.Documento,
    Status: r.Status,
    Vencimento: r.Vencimento,
  }))

  const pdfRows = filtered.map(r => ({
    Fornecedor: r.Fornecedor,
    Terceiro: r.Terceiro,
    CNPJ_Terceiro: r.CNPJ_Terceiro,
    Documento: r.Documento,
    Competencia: r.Competencia ?? '',
    Status: r.Status,
    Vencimento: r.Vencimento,
  }))

  function handlePDF() {
    setPdfLoading(true)
    setTimeout(() => {
      exportR3PDF({ rows: pdfRows, geradoEm })
      setPdfLoading(false)
    }, 50)
  }

  return (
    <div id="section-r3">
      <div className="bg-white rounded-xl shadow-sm p-4 mb-3 flex flex-wrap gap-3 items-end">
        <div>
          <label className="block text-[12px] font-bold text-[#0E8FA3] uppercase mb-1">Fornecedor</label>
          <select value={filt} onChange={e => setFilt(e.target.value)} className="border border-[#cde] rounded px-2 py-1.5 text-[13px]">
            <option value="">Todos</option>
            {fornList.map(f => <option key={f} value={f}>{f}</option>)}
          </select>
        </div>
        <div>
          <label className="block text-[12px] font-bold text-[#0E8FA3] uppercase mb-1">Status</label>
          <select value={stat} onChange={e => setStat(e.target.value)} className="border border-[#cde] rounded px-2 py-1.5 text-[13px]">
            <option value="">Todos</option>
            <option value="Aprovado">Aprovado</option>
            <option value="Reprovado">Reprovado</option>
            <option value="Não anexado">Não anexado</option>
            <option value="Aguardando Submissão">Aguardando Submissão</option>
            <option value="Em Análise">Em Análise</option>
          </select>
        </div>
        <div>
          <label className="block text-[12px] font-bold text-[#0E8FA3] uppercase mb-1">Buscar documento</label>
          <input value={busca} onChange={e => setBusca(e.target.value)} placeholder="Ex: ASO, Ficha de EPI..." className="border border-[#cde] rounded px-2 py-1.5 text-[13px] w-52" />
        </div>
        <button onClick={clear} className="bg-[#0E8FA3] text-white rounded px-3 py-1.5 text-[13px] font-semibold hover:bg-[#0a7a8d]">Limpar</button>
        <div className="ml-auto flex items-center gap-1.5">
          <span className="text-[11px] text-[#999] font-semibold uppercase mr-1">Exportar:</span>
          <button onClick={() => exportXLSX(rows, 'situacao_terceiros')} className="bg-[#28A745] text-white rounded px-3 py-1.5 text-[13px] font-semibold hover:bg-[#1e7e34]">Excel</button>
          <button onClick={() => exportCSV(rows, 'situacao_terceiros')} className="bg-[#6C757D] text-white rounded px-3 py-1.5 text-[13px] font-semibold hover:bg-[#545b62]">CSV</button>
          <button onClick={handlePDF} disabled={pdfLoading} className="bg-[#DC3545] text-white rounded px-3 py-1.5 text-[13px] font-semibold hover:bg-[#b02a37] disabled:opacity-60 disabled:cursor-wait flex items-center gap-1">
            {pdfLoading ? '⏳' : '⬇'} PDF
          </button>
        </div>
      </div>
      <div className="bg-white rounded-xl shadow-sm p-4">
        <p className="text-[13px] text-[#6C757D] mb-2">{filtered.length} registro(s) de {data.length} no total</p>
        <div className="overflow-x-auto">
          <table className="w-full text-[13px] border-collapse">
            <thead>
              <tr className="bg-[#0E8FA3] text-white">
                {['Fornecedor','Terceiro','Documento','Status','Vencimento'].map(h => (
                  <th key={h} className="px-3 py-2.5 text-left font-bold">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {filtered.map((r, i) => (
                <tr key={i} className={`border-b border-[#e5eef1] hover:bg-[#d4eef3] ${i % 2 === 1 ? 'bg-[#f0f8fa]' : ''}`}>
                  <td className="px-3 py-2">{r.Fornecedor}</td>
                  <td className="px-3 py-2">{r.Terceiro}</td>
                  <td className="px-3 py-2">{r.Documento}</td>
                  <td className="px-3 py-2">{badge(r.Status)}</td>
                  <td className="px-3 py-2">{r.Vencimento || '—'}</td>
                </tr>
              ))}
              {filtered.length === 0 && (
                <tr><td colSpan={5} className="px-3 py-6 text-center text-[#999]">Nenhum registro encontrado</td></tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
