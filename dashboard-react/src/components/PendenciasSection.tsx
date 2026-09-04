import { useState, useMemo } from 'react'
import type { PendRow } from '../types'
import { exportCSV, exportXLSX, exportPendPDF } from '../utils/exportUtils'

interface Props {
  data: PendRow[]
  aClassificar?: PendRow[]
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

export function PendenciasSection({ data, aClassificar = [], geradoEm = '' }: Props) {
  const [pdfLoading, setPdfLoading] = useState(false)

  const rows = useMemo(() => data.map(r => ({
    Fornecedor: r.Fornecedor,
    CNPJ: fmtCNPJ(r.CNPJ_Forn),
    Area: r.Area,
    Documento: r.Documento,
    Competencia: r.Competencia,
    Detalhe: r.Detalhe,
  })), [data])

  function handlePDF() {
    setPdfLoading(true)
    setTimeout(() => {
      exportPendPDF({ rows, geradoEm })
      setPdfLoading(false)
    }, 50)
  }

  // suppress unused warning — statusBadge kept for future use
  void statusBadge

  return (
    <div id="section-pendencias">

      {/* Alerta: registros classificados como "A classificar" */}
      {aClassificar.length > 0 && (
        <div className="bg-[#fff8e1] border border-[#f59e0b] rounded-xl p-4 mb-4 flex items-start gap-3">
          <span className="text-[#f59e0b] text-xl mt-0.5">⚠️</span>
          <div className="w-full">
            <p className="text-[13px] font-bold text-[#92400e] mb-1">
              {aClassificar.length} pendência(s) classificadas como "A classificar"
            </p>
            <p className="text-[12px] text-[#78350f] mb-2">
              Estes registros exigem competência mas não possuem data válida no campo estruturado
              <strong> "Marcas e representações"</strong>. Motivo: campo vazio <em>ou</em> data
              anterior ao início do contrato Zurich (novembro/2025). Verifique e preencha
              o campo na plataforma para que a competência seja registrada corretamente.
            </p>
            <div className="overflow-x-auto">
              <table className="text-[12px] border-collapse w-full">
                <thead>
                  <tr className="bg-[#fef3c7]">
                    {['Fornecedor', 'Documento', 'Área', 'Status Real'].map(h => (
                      <th key={h} className="px-3 py-1.5 text-left font-semibold text-[#92400e] border border-[#fde68a]">{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {aClassificar.map((r, i) => (
                    <tr key={i} className="border-b border-[#fde68a]">
                      <td className="px-3 py-1.5 text-[#78350f]">{r.Fornecedor}</td>
                      <td className="px-3 py-1.5 font-semibold text-[#78350f]">{r.Documento}</td>
                      <td className="px-3 py-1.5">{r.Area === 'TERCEIROS' ? 'Terceiros' : 'Fornecedor'}</td>
                      <td className="px-3 py-1.5">
                        {r.StatusReal === 'Ativa' && <span className="inline-block px-2 py-0.5 rounded-full text-[10px] font-bold bg-[#fff3cd] text-[#856404]">Ativa</span>}
                        {r.StatusReal === 'Não resolvida' && <span className="inline-block px-2 py-0.5 rounded-full text-[10px] font-bold bg-[#fde8e8] text-[#b91c1c]">Não resolvida</span>}
                        {r.StatusReal === 'Resolvida' && <span className="inline-block px-2 py-0.5 rounded-full text-[10px] font-bold bg-[#d4edda] text-[#155724]">Resolvida</span>}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* Export bar */}
      <div className="bg-white rounded-xl shadow-sm p-4 mb-3 flex flex-wrap gap-3 items-center justify-end">
        <span className="text-[11px] text-[#999] font-semibold uppercase mr-1">Exportar:</span>
        <button onClick={() => exportXLSX(rows, 'pendencias_zurich')} className="bg-[#28A745] text-white rounded px-3 py-1.5 text-[13px] font-semibold hover:bg-[#1e7e34]">Excel</button>
        <button onClick={() => exportCSV(rows, 'pendencias_zurich')} className="bg-[#6C757D] text-white rounded px-3 py-1.5 text-[13px] font-semibold hover:bg-[#545b62]">CSV</button>
        <button onClick={handlePDF} disabled={pdfLoading} className="bg-[#DC3545] text-white rounded px-3 py-1.5 text-[13px] font-semibold hover:bg-[#b02a37] disabled:opacity-60 disabled:cursor-wait flex items-center gap-1">
          {pdfLoading ? '⏳' : '⬇'} PDF
        </button>
      </div>

      {/* Table */}
      <div className="bg-white rounded-xl shadow-sm p-4">
        <p className="text-[13px] text-[#6C757D] mb-2">{data.length} pendência(s)</p>
        <div className="overflow-x-auto">
          <table className="w-full text-[13px] border-collapse">
            <thead>
              <tr className="bg-[#0E8FA3] text-white">
                {['Situação Real', 'Fornecedor', 'Área', 'Documento', 'Competência', 'Detalhe'].map(h => (
                  <th key={h} className="px-3 py-2.5 text-left font-bold">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {data.map((r, i) => (
                <tr key={i} className={`border-b border-[#e5eef1] hover:bg-[#d4eef3] ${i % 2 === 1 ? 'bg-[#f0f8fa]' : ''}`}>
                  <td className="px-3 py-2 whitespace-nowrap">
                    {r.StatusReal === 'Ativa' && <span className="inline-block px-2 py-0.5 rounded-full text-[11px] font-bold bg-[#fff3cd] text-[#856404]">Ativa</span>}
                    {r.StatusReal === 'Não resolvida' && <span className="inline-block px-2 py-0.5 rounded-full text-[11px] font-bold bg-[#fde8e8] text-[#b91c1c]">Não resolvida</span>}
                    {r.StatusReal === 'Resolvida' && <span className="inline-block px-2 py-0.5 rounded-full text-[11px] font-bold bg-[#d4edda] text-[#155724]">Resolvida</span>}
                  </td>
                  <td className="px-3 py-2">
                    <div className="font-medium">{r.Fornecedor}</div>
                    {r.CNPJ_Forn && <div className="text-[11px] text-[#999] font-mono mt-0.5">{fmtCNPJ(r.CNPJ_Forn)}</div>}
                  </td>
                  <td className="px-3 py-2">{areaBadge(r.Area)}</td>
                  <td className="px-3 py-2 font-semibold">{r.Documento}</td>
                  <td className="px-3 py-2">
                    {r.Competencia === 'Não possui competência'
                      ? <span className="bg-[#f0f0f0] text-[#999] text-[11px] px-2 py-0.5 rounded italic">{r.Competencia}</span>
                      : r.Competencia === 'A classificar'
                        ? <span className="bg-[#fff3cd] text-[#856404] text-[11px] px-2 py-0.5 rounded italic" title="Campo estruturado vazio ou data anterior ao contrato (nov/2025)">A classificar</span>
                        : r.Competencia
                          ? <span className="bg-[#e8f7fa] text-[#0E8FA3] text-[11px] px-2 py-0.5 rounded">{r.Competencia}</span>
                          : <span className="text-[#ccc]">—</span>}
                  </td>
                  <td className="px-3 py-2 text-[12px] text-[#666] break-words" style={{ minWidth: '240px', maxWidth: '420px' }}>{r.Detalhe}</td>
                </tr>
              ))}
              {data.length === 0 && (
                <tr><td colSpan={6} className="px-3 py-6 text-center text-[#999]">Nenhuma pendência encontrada</td></tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
