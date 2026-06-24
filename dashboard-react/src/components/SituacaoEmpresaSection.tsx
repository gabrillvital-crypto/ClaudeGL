import { useState, useMemo } from 'react'
import type { FornSitRow } from '../types'
import { exportCSV, exportXLSX, exportR4PDF } from '../utils/exportUtils'

interface Props {
  data: FornSitRow[]
  gfForn: string
  r4_total: number
  r4_aprovado: number
  r4_reprovado: number
  r4_nao_anex: number
  r4_em_analise: number
  r4_vencido: number
  r4_regular: number
  r4_nao_analisado: number
  r4_irregular: number
  r4_pct_nc: number
  r4_pct_c: number
  r4_fornecedores: number
  geradoEm?: string
}

function badge(s: string) {
  const m: Record<string, string> = {
    // Docs manuais (legado)
    'Aprovado':      'bg-[#d4edda] text-[#28A745]',
    'Reprovado':     'bg-[#ffeaea] text-[#DC3545]',
    'Não Anexado':   'bg-[#fff3cd] text-[#856404]',
    'Em análise':    'bg-[#e8f4f7] text-[#0E8FA3]',
    'Vencido':       'bg-[#ffeaea] text-[#DC3545]',
    // Busca automática (novos)
    'Regular':       'bg-[#d4f4e8] text-[#157347]',
    'Não Analisado': 'bg-[#e9ecef] text-[#6C757D]',
    'Irregular':     'bg-[#fff0d6] text-[#b05c00]',
  }
  return (
    <span className={`inline-block px-2 py-0.5 rounded-full text-[11px] font-bold ${m[s] ?? 'bg-gray-100 text-gray-600'}`}>
      {s}
    </span>
  )
}

function KPISmall({ value, label, color }: { value: string | number; label: string; color?: string }) {
  const c = color === 'green'  ? 'border-t-[#28A745] text-[#28A745]'
    : color === 'red'    ? 'border-t-[#DC3545] text-[#DC3545]'
    : color === 'yellow' ? 'border-t-[#FFC107] text-[#a07800]'
    : color === 'orange' ? 'border-t-[#F4793B] text-[#F4793B]'
    : 'border-t-[#0E8FA3] text-[#0E8FA3]'
  const [border, text] = c.split(' ')
  return (
    <div className={`bg-white rounded-xl p-3 shadow-sm border-t-4 text-center ${border}`}>
      <div className={`text-2xl font-bold leading-tight ${text}`}>{value}</div>
      <div className="text-[10px] text-[#666] mt-1 font-semibold uppercase tracking-wide leading-tight">{label}</div>
    </div>
  )
}

export function SituacaoEmpresaSection({
  data, gfForn,
  r4_total, r4_aprovado, r4_reprovado, r4_nao_anex, r4_em_analise, r4_vencido,
  r4_regular, r4_nao_analisado, r4_irregular,
  r4_pct_nc, r4_pct_c, r4_fornecedores,
  geradoEm = '',
}: Props) {
  const [pdfLoading, setPdfLoading] = useState(false)
  const [filt, setFilt] = useState('')
  const [stat, setStat] = useState('')
  const [busca, setBusca] = useState('')

  const fornList = useMemo(() => [...new Set(data.map(r => r.Fornecedor))].sort(), [data])

  const filtered = useMemo(() => {
    let d = gfForn ? data.filter(r => r.Fornecedor === gfForn) : data
    if (filt) d = d.filter(r => r.Fornecedor === filt)
    if (stat) d = d.filter(r => r.Status === stat)
    if (busca) d = d.filter(r => r.Documento.toLowerCase().includes(busca.toLowerCase()))
    return d
  }, [data, gfForn, filt, stat, busca])

  const subKPI = useMemo(() => {
    const active = gfForn || filt || stat || busca
    if (!active) {
      return {
        total: r4_total, aprovado: r4_aprovado, reprovado: r4_reprovado,
        nao_anex: r4_nao_anex, em_analise: r4_em_analise, vencido: r4_vencido,
        regular: r4_regular, nao_analisado: r4_nao_analisado, irregular: r4_irregular,
        pct_nc: r4_pct_nc, pct_c: r4_pct_c, forn: r4_fornecedores,
      }
    }
    const total         = filtered.length
    const aprovado      = filtered.filter(r => r.Status === 'Aprovado').length
    const reprovado     = filtered.filter(r => r.Status === 'Reprovado').length
    const nao_anex      = filtered.filter(r => r.Status === 'Não Anexado').length
    const em_analise    = filtered.filter(r => r.Status === 'Em análise').length
    const vencido       = filtered.filter(r => r.Status === 'Vencido').length
    const regular       = filtered.filter(r => r.Status === 'Regular').length
    const nao_analisado = filtered.filter(r => r.Status === 'Não Analisado').length
    const irregular     = filtered.filter(r => r.Status === 'Irregular').length
    const nao_conf      = reprovado + nao_anex + em_analise + vencido + nao_analisado + irregular
    return {
      total, aprovado, reprovado, nao_anex, em_analise, vencido,
      regular, nao_analisado, irregular,
      pct_nc: total > 0 ? Math.round(nao_conf / total * 1000) / 10 : 0,
      pct_c:  total > 0 ? Math.round((aprovado + regular) / total * 1000) / 10 : 0,
      forn: new Set(filtered.map(r => r.Fornecedor)).size,
    }
  }, [filtered, gfForn, filt, stat, busca,
      r4_total, r4_aprovado, r4_reprovado, r4_nao_anex, r4_em_analise, r4_vencido,
      r4_regular, r4_nao_analisado, r4_irregular, r4_pct_nc, r4_pct_c, r4_fornecedores])

  function clear() { setFilt(''); setStat(''); setBusca('') }

  const rows = filtered.map(r => ({ Fornecedor: r.Fornecedor, Documento: r.Documento, Status: r.Status, Vencimento: r.Vencimento }))

  function handlePDF() {
    setPdfLoading(true)
    setTimeout(() => {
      exportR4PDF({ rows, kpis: subKPI, geradoEm })
      setPdfLoading(false)
    }, 50)
  }

  return (
    <div id="section-r4">
      {/* Sub-KPIs */}
      <div className="grid gap-3 mb-4" style={{ gridTemplateColumns: 'repeat(auto-fit, minmax(120px, 1fr))' }}>
        <KPISmall value={`${subKPI.pct_nc}%`}      label="% Não Conf. Empresa"  color="red" />
        <KPISmall value={`${subKPI.pct_c}%`}       label="% Conf. Empresa"      color="green" />
        <KPISmall value={subKPI.regular}            label="Regular (Robô OK)"    color="green" />
        <KPISmall value={subKPI.aprovado}           label="Aprovados (BPO)"      color="green" />
        <KPISmall value={subKPI.reprovado}          label="Reprovados"           color="red" />
        <KPISmall value={subKPI.irregular}          label="Irregular (Débito)"   color="orange" />
        <KPISmall value={subKPI.nao_analisado}      label="Não Analisados"       color="yellow" />
        <KPISmall value={subKPI.nao_anex}           label="Não Anexados"         color="yellow" />
        <KPISmall value={subKPI.em_analise}         label="Em Análise (Manual)"  color="orange" />
        <KPISmall value={subKPI.vencido}            label="Vencidos"             color="red" />
        <KPISmall value={subKPI.total}              label="Total Documentos" />
        <KPISmall value={subKPI.forn}               label="Fornecedores c/ Docs" />
      </div>

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
          <label className="block text-[12px] font-bold text-[#0E8FA3] uppercase mb-1">Status</label>
          <select value={stat} onChange={e => setStat(e.target.value)} className="border border-[#cde] rounded px-2 py-1.5 text-[13px]">
            <option value="">Todos</option>
            <optgroup label="Busca Automática">
              <option value="Regular">Regular (Robô OK)</option>
              <option value="Irregular">Irregular (Débito)</option>
              <option value="Não Analisado">Não Analisado</option>
            </optgroup>
            <optgroup label="Análise BPO / Manual">
              <option value="Aprovado">Aprovado</option>
              <option value="Reprovado">Reprovado</option>
              <option value="Vencido">Vencido</option>
              <option value="Não Anexado">Não Anexado</option>
              <option value="Em análise">Em análise</option>
            </optgroup>
          </select>
        </div>
        <div>
          <label className="block text-[12px] font-bold text-[#0E8FA3] uppercase mb-1">Buscar documento</label>
          <input value={busca} onChange={e => setBusca(e.target.value)} placeholder="Ex: FGTS, CND, TRF3..." className="border border-[#cde] rounded px-2 py-1.5 text-[13px] w-52" />
        </div>
        <button onClick={clear} className="bg-[#0E8FA3] text-white rounded px-3 py-1.5 text-[13px] font-semibold hover:bg-[#0a7a8d]">Limpar</button>
        <div className="ml-auto flex items-center gap-1.5">
          <span className="text-[11px] text-[#999] font-semibold uppercase mr-1">Exportar:</span>
          <button onClick={() => exportXLSX(rows as any, 'situacao_empresa')} className="bg-[#28A745] text-white rounded px-3 py-1.5 text-[13px] font-semibold hover:bg-[#1e7e34]">Excel</button>
          <button onClick={() => exportCSV(rows as any, 'situacao_empresa')} className="bg-[#6C757D] text-white rounded px-3 py-1.5 text-[13px] font-semibold hover:bg-[#545b62]">CSV</button>
          <button onClick={handlePDF} disabled={pdfLoading} className="bg-[#DC3545] text-white rounded px-3 py-1.5 text-[13px] font-semibold hover:bg-[#b02a37] disabled:opacity-60 disabled:cursor-wait flex items-center gap-1">
            {pdfLoading ? '⏳' : '⬇'} PDF
          </button>
        </div>
      </div>

      {/* Table */}
      <div className="bg-white rounded-xl shadow-sm p-4">
        <p className="text-[13px] text-[#6C757D] mb-2">{filtered.length} registro(s) de {data.length} no total</p>
        <div className="overflow-x-auto">
          <table className="w-full text-[13px] border-collapse">
            <thead>
              <tr className="bg-[#0E8FA3] text-white">
                {['Fornecedor', 'Documento', 'Status', 'Vencimento'].map(h => (
                  <th key={h} className="px-3 py-2.5 text-left font-bold">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {filtered.map((r, i) => (
                <tr key={i} className={`border-b border-[#e5eef1] hover:bg-[#d4eef3] ${i % 2 === 1 ? 'bg-[#f0f8fa]' : ''}`}>
                  <td className="px-3 py-2">{r.Fornecedor}</td>
                  <td className="px-3 py-2">{r.Documento}</td>
                  <td className="px-3 py-2">{badge(r.Status)}</td>
                  <td className="px-3 py-2">{r.Vencimento || '—'}</td>
                </tr>
              ))}
              {filtered.length === 0 && (
                <tr><td colSpan={4} className="px-3 py-6 text-center text-[#999]">Nenhum registro encontrado</td></tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
