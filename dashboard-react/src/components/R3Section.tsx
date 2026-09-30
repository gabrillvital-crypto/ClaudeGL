import { useState, useMemo, useRef, useEffect } from 'react'
import type { SitTerceiroRow } from '../types'
import { exportCSV, exportXLSX, exportR3PDF } from '../utils/exportUtils'

// Situação Documental por Terceiro — mesmo layout do relatório Python:
// 8 KPIs · Modo Agrupado + Exportar · tabela paginada (150/pág) ou cartões por terceiro

interface Props {
  data: SitTerceiroRow[]
  totalGeral: number
  geradoEm?: string
}

const PAGE_SIZE = 150

const STATUS_CLS: Record<string, string> = {
  'Aprovado':             'bg-[#d4edda] text-[#28A745]',
  'Reprovado':            'bg-[#ffeaea] text-[#DC3545]',
  'Não anexado':          'bg-[#fff3cd] text-[#856404]',
  'Aguardando Submissão': 'bg-[#fff3cd] text-[#856404]',
  'Em Análise':           'bg-[#e8f4f7] text-[#0E8FA3]',
}

function badge(s: string) {
  return (
    <span className={`inline-block px-2 py-0.5 rounded-full text-[11px] font-bold whitespace-nowrap ${STATUS_CLS[s] ?? 'bg-gray-100 text-gray-600'}`}>
      {s}
    </span>
  )
}

function badgeComp(c: string) {
  if (!c) return <span className="text-[#aaa]">—</span>
  // Mesmo badge para todas as competências, inclusive "A classificar" (igual ao relatório Python)
  return <span className="inline-block px-2 py-0.5 rounded-lg text-[11px] bg-[#e8f4f8] text-[#0E8FA3]">{c}</span>
}

function KPI({ value, label, color }: { value: string | number; label: string; color?: 'red' | 'green' | 'yellow' | 'orange' }) {
  const [border, text] = (
    color === 'green'  ? 'border-t-[#28A745] text-[#28A745]'
    : color === 'red'    ? 'border-t-[#DC3545] text-[#DC3545]'
    : color === 'yellow' ? 'border-t-[#FFC107] text-[#b38600]'
    : color === 'orange' ? 'border-t-[#F4793B] text-[#F4793B]'
    : 'border-t-[#0E8FA3] text-[#0E8FA3]'
  ).split(' ')
  return (
    <div className={`bg-white rounded-xl px-3.5 py-4 shadow-sm border-t-4 text-center ${border}`}>
      <div className={`text-[28px] font-bold leading-tight ${text}`}>{value}</div>
      <div
        className="text-[11px] text-[#666] mt-1.5 font-semibold uppercase tracking-wide leading-tight"
        dangerouslySetInnerHTML={{ __html: label }}
      />
    </div>
  )
}

export function R3Section({ data, totalGeral, geradoEm = '' }: Props) {
  const [agrupado, setAgrupado] = useState(false)
  const [page, setPage] = useState(0)
  const [pdfLoading, setPdfLoading] = useState(false)

  // Filtro mudou → volta para a primeira página
  useEffect(() => { setPage(0) }, [data])

  // ── KPIs (mesma conta do Python) ──
  const kpis = useMemo(() => {
    const n = (s: string) => data.filter(r => r.Status === s).length
    const aprov = n('Aprovado'), reprov = n('Reprovado'), naoAnex = n('Não anexado')
    const aguardSub = n('Aguardando Submissão'), emAnal = n('Em Análise')
    const tot = aprov + reprov + naoAnex + aguardSub + emAnal
    return {
      pctNC: tot > 0 ? ((tot - aprov) / tot * 100).toFixed(1) : '0.0',
      pctC:  tot > 0 ? (aprov / tot * 100).toFixed(1) : '0.0',
      aprov, reprov, naoAnex, aguardSub, emAnal,
      terc: new Set(data.map(r => r.Terceiro)).size,
    }
  }, [data])

  // ── Modo agrupado: um cartão por fornecedor + terceiro ──
  const grupos = useMemo(() => {
    if (!agrupado) return []
    const m = new Map<string, { fornecedor: string; terceiro: string; docs: SitTerceiroRow[]; temNC: boolean }>()
    data.forEach(r => {
      const k = `${r.Fornecedor}|||${r.Terceiro}`
      if (!m.has(k)) m.set(k, { fornecedor: r.Fornecedor, terceiro: r.Terceiro, docs: [], temNC: false })
      const g = m.get(k)!
      g.docs.push(r)
      if (r.Status !== 'Aprovado') g.temNC = true
    })
    return [...m.values()]
  }, [data, agrupado])

  // ── Exportação ──
  const exportRows = useMemo(() => data.map(r => ({
    Fornecedor: r.Fornecedor,
    CNPJ_Forn: r.CNPJ_Forn,
    Aeroporto: r.Aeroporto ?? '',
    Terceiro: r.Terceiro,
    CNPJ_Terceiro: r.CNPJ_Terceiro,
    Documento: r.Documento,
    Competencia: r.Competencia,
    Status: r.Status,
    Vencimento: r.Vencimento,
  })), [data])

  const pdfRowsRef = useRef(exportRows)
  pdfRowsRef.current = exportRows

  function handlePDF() {
    const snapshot = pdfRowsRef.current.map(({ CNPJ_Forn: _c, ...r }) => r)
    setPdfLoading(true)
    setTimeout(() => {
      exportR3PDF({ rows: snapshot, geradoEm })
      setPdfLoading(false)
    }, 50)
  }

  const pages = Math.ceil(data.length / PAGE_SIZE)
  const pageRows = data.slice(page * PAGE_SIZE, (page + 1) * PAGE_SIZE)
  const btn = 'text-white rounded px-3.5 py-1.5 text-[13px] font-semibold transition-colors'

  return (
    <div id="section-r3">
      {/* KPIs */}
      <div className="grid gap-3.5 mb-4" style={{ gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))' }}>
        <KPI value={`${kpis.pctNC}%`} label="% Não Conf.<br>Geral" color="red" />
        <KPI value={`${kpis.pctC}%`}  label="% Conf.<br>Geral"     color="green" />
        <KPI value={kpis.aprov}       label="Docs<br>Aprovados"    color="green" />
        <KPI value={kpis.reprov}      label="Docs<br>Reprovados"   color="red" />
        <KPI value={kpis.naoAnex}     label="Não<br>Anexado"       color="yellow" />
        <KPI value={kpis.aguardSub}   label="Ag.<br>Submissão"     color="yellow" />
        <KPI value={kpis.emAnal}      label="Em<br>Análise"        color="orange" />
        <KPI value={kpis.terc}        label="Terceiros<br>com Docs" />
      </div>

      {/* Ações */}
      <div className="flex flex-wrap items-center justify-end gap-2 mb-3">
        <button onClick={() => setAgrupado(a => !a)} className={`${btn} bg-[#6f42c1] hover:bg-[#5a32a3]`}>
          {agrupado ? 'Modo Linha' : 'Modo Agrupado'}
        </button>
        <span className="text-[11px] text-[#999] font-semibold uppercase ml-1">Exportar:</span>
        <button onClick={() => exportXLSX(exportRows, 'situacao_terceiros')} className={`${btn} bg-[#28A745] hover:bg-[#1e7e34]`}>
          Excel
        </button>
        <button onClick={handlePDF} disabled={pdfLoading} className={`${btn} bg-[#c0392b] hover:bg-[#96281b] disabled:opacity-60 disabled:cursor-wait`}>
          {pdfLoading ? '⏳ PDF' : 'PDF'}
        </button>
        <button onClick={() => exportCSV(exportRows, 'situacao_terceiros')} className={`${btn} bg-[#6C757D] hover:bg-[#545b62]`}>
          CSV
        </button>
      </div>

      <div className="bg-white rounded-xl shadow-sm p-5">
        <p className="text-[13px] text-[#6C757D] mb-2.5">
          {data.length} registro(s) exibido(s) de {totalGeral} no total
        </p>

        {!agrupado && (
          <>
            <div className="overflow-x-auto">
              <table className="w-full text-[13px] border-collapse">
                <thead>
                  <tr className="bg-[#0E8FA3] text-white">
                    {['Fornecedor', 'Aeroporto', 'Terceiro', 'Documento', 'Competência', 'Status', 'Vencimento'].map(h => (
                      <th key={h} className="px-3 py-2.5 text-left font-bold">{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {pageRows.map((r, i) => (
                    <tr key={i} className={`border-b border-[#e5eef1] hover:bg-[#d4eef3] ${i % 2 === 1 ? 'bg-[#f0f8fa]' : ''}`}>
                      <td className="px-3 py-2">{r.Fornecedor}</td>
                      <td className="px-3 py-2 text-[12px] font-semibold text-[#0E8FA3]">{r.Aeroporto || '—'}</td>
                      <td className="px-3 py-2">{r.Terceiro}</td>
                      <td className="px-3 py-2">{r.Documento}</td>
                      <td className="px-3 py-2">{badgeComp(r.Competencia)}</td>
                      <td className="px-3 py-2">{badge(r.Status)}</td>
                      <td className="px-3 py-2">{r.Vencimento || '—'}</td>
                    </tr>
                  ))}
                  {data.length === 0 && (
                    <tr><td colSpan={7} className="px-3 py-6 text-center text-[#999]">Nenhum registro encontrado</td></tr>
                  )}
                </tbody>
              </table>
            </div>

            {pages > 1 && (
              <div className="flex items-center gap-2.5 mt-2.5 text-[13px] text-[#6C757D]">
                <button
                  onClick={() => setPage(p => Math.max(0, p - 1))} disabled={page === 0}
                  className="px-3 py-1 border border-[#ccc] rounded bg-white disabled:opacity-40 disabled:cursor-default"
                >‹ Anterior</button>
                <span>Página {page + 1} de {pages} &nbsp;({data.length} registros)</span>
                <button
                  onClick={() => setPage(p => Math.min(pages - 1, p + 1))} disabled={page === pages - 1}
                  className="px-3 py-1 border border-[#ccc] rounded bg-white disabled:opacity-40 disabled:cursor-default"
                >Próximo ›</button>
              </div>
            )}
          </>
        )}

        {agrupado && (
          grupos.length === 0
            ? <p className="text-center text-[#aaa] py-6">Nenhum resultado</p>
            : grupos.map(g => (
              <div
                key={`${g.fornecedor}|||${g.terceiro}`}
                className={`bg-[#f8f9fa] rounded-lg px-4 py-3 mb-2.5 border-l-4 ${g.temNC ? 'border-l-[#DC3545]' : 'border-l-[#0E8FA3]'}`}
              >
                <div className="flex items-center gap-2.5 mb-2">
                  <div className="flex-1">
                    <div className="text-[11px] text-[#0E8FA3] font-bold uppercase">{g.fornecedor}</div>
                    <div className="text-[14px] font-bold text-[#222]">{g.terceiro}</div>
                  </div>
                  <div className="text-[11px] text-[#999]">{g.docs.length} doc(s)</div>
                </div>
                <div className="flex flex-wrap gap-1.5">
                  {g.docs.map((d, i) => (
                    <span
                      key={i}
                      title={d.Status}
                      className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-xl text-[12px] font-semibold ${STATUS_CLS[d.Status] ?? 'bg-[#eee] text-[#333]'}`}
                    >
                      {d.Documento}
                      {d.Vencimento && <span className="text-[10px] opacity-80">({d.Vencimento})</span>}
                    </span>
                  ))}
                </div>
              </div>
            ))
        )}
      </div>
    </div>
  )
}
