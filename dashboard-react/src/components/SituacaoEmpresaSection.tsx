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
  r4_irregular: number
  r4_alerta: number
  r4_pct_nc: number
  r4_pct_c: number
  r4_fornecedores: number
  geradoEm?: string
}

const STATUS_OPTIONS: { value: string; label: string; active: string; inactive: string }[] = [
  { value: 'Aprovado',    label: 'Aprovado',          active: 'bg-[#28A745] text-white',                  inactive: 'bg-white text-[#28A745] border border-[#28A745] hover:bg-[#eafaf1]' },
  { value: 'Reprovado',   label: 'Reprovado',         active: 'bg-[#DC3545] text-white',                  inactive: 'bg-white text-[#DC3545] border border-[#DC3545] hover:bg-[#fdf2f3]' },
  { value: 'Irregular',   label: 'Irregular (Débito)', active: 'bg-[#b05c00] text-white',                 inactive: 'bg-white text-[#b05c00] border border-[#b05c00] hover:bg-[#fff4e8]' },
  { value: 'Não Anexado', label: 'Não Anexado',       active: 'bg-[#FFC107] text-[#5a3e00]',              inactive: 'bg-white text-[#a07800] border border-[#FFC107] hover:bg-[#fffbea]' },
  { value: 'Em análise',  label: 'Em análise',        active: 'bg-[#0E8FA3] text-white',                  inactive: 'bg-white text-[#0E8FA3] border border-[#0E8FA3] hover:bg-[#e8f4f7]' },
  { value: 'Vencido',     label: 'Vencido',           active: 'bg-[#DC3545] text-white',                  inactive: 'bg-white text-[#DC3545] border border-[#DC3545] hover:bg-[#fdf2f3]' },
  { value: 'Alerta',      label: 'Alerta',            active: 'bg-[#d97706] text-white',                  inactive: 'bg-white text-[#d97706] border border-[#d97706] hover:bg-[#fef3c7]' },
]

function badge(s: string) {
  const m: Record<string, string> = {
    'Aprovado':    'bg-[#d4edda] text-[#28A745]',
    'Reprovado':   'bg-[#ffeaea] text-[#DC3545]',
    'Não Anexado': 'bg-[#fff3cd] text-[#856404]',
    'Em análise':  'bg-[#e8f4f7] text-[#0E8FA3]',
    'Vencido':     'bg-[#ffeaea] text-[#DC3545]',
    'Irregular':   'bg-[#fff0d6] text-[#b05c00]',
    'Alerta':      'bg-[#fef3c7] text-[#d97706]',
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
    : color === 'amber'  ? 'border-t-[#d97706] text-[#d97706]'
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
  r4_irregular, r4_alerta,
  r4_pct_nc, r4_pct_c, r4_fornecedores,
  geradoEm = '',
}: Props) {
  const [pdfLoading, setPdfLoading] = useState(false)
  const [filt, setFilt] = useState('')
  const [compFilt, setCompFilt] = useState('')
  const [statFilters, setStatFilters] = useState<Set<string>>(new Set())
  const [busca, setBusca] = useState('')

  function toggleStat(v: string) {
    setStatFilters(prev => {
      const next = new Set(prev)
      next.has(v) ? next.delete(v) : next.add(v)
      return next
    })
  }

  const fornList = useMemo(() => [...new Set(data.map(r => r.Fornecedor))].sort(), [data])
  const compList = useMemo(() => [...new Set(data.map(r => r.Competencia).filter(Boolean))].sort(), [data])

  const filtered = useMemo(() => {
    let d = gfForn ? data.filter(r => r.Fornecedor === gfForn) : data
    if (filt) d = d.filter(r => r.Fornecedor === filt)
    if (compFilt) d = d.filter(r => r.Competencia === compFilt)
    if (statFilters.size > 0) d = d.filter(r => statFilters.has(r.Status))
    if (busca) d = d.filter(r => r.Documento.toLowerCase().includes(busca.toLowerCase()))
    return d
  }, [data, gfForn, filt, compFilt, statFilters, busca])

  const subKPI = useMemo(() => {
    const active = gfForn || filt || compFilt || statFilters.size > 0 || busca
    if (!active) {
      return {
        total: r4_total, aprovado: r4_aprovado, reprovado: r4_reprovado,
        nao_anex: r4_nao_anex, em_analise: r4_em_analise, vencido: r4_vencido,
        irregular: r4_irregular, alerta: r4_alerta,
        pct_nc: r4_pct_nc, pct_c: r4_pct_c, forn: r4_fornecedores,
      }
    }
    const total      = filtered.length
    const aprovado   = filtered.filter(r => r.Status === 'Aprovado').length
    const reprovado  = filtered.filter(r => r.Status === 'Reprovado').length
    const nao_anex   = filtered.filter(r => r.Status === 'Não Anexado').length
    const em_analise = filtered.filter(r => r.Status === 'Em análise').length
    const vencido    = filtered.filter(r => r.Status === 'Vencido').length
    const irregular  = filtered.filter(r => r.Status === 'Irregular').length
    const alerta     = filtered.filter(r => r.Status === 'Alerta').length
    const nao_conf   = reprovado + nao_anex + em_analise + vencido + irregular + alerta
    return {
      total, aprovado, reprovado, nao_anex, em_analise, vencido, irregular, alerta,
      pct_nc: total > 0 ? Math.round(nao_conf / total * 1000) / 10 : 0,
      pct_c:  total > 0 ? Math.round(aprovado / total * 1000) / 10 : 0,
      forn: new Set(filtered.map(r => r.Fornecedor)).size,
    }
  }, [filtered, gfForn, filt, compFilt, statFilters, busca,
      r4_total, r4_aprovado, r4_reprovado, r4_nao_anex, r4_em_analise, r4_vencido,
      r4_irregular, r4_alerta, r4_pct_nc, r4_pct_c, r4_fornecedores])

  function clear() { setFilt(''); setCompFilt(''); setStatFilters(new Set()); setBusca('') }

  const rows = filtered.map(r => ({ Fornecedor: r.Fornecedor, Documento: r.Documento, Competencia: r.Competencia, Status: r.Status, Vencimento: r.Vencimento }))

  function handlePDF() {
    setPdfLoading(true)
    setTimeout(() => {
      exportR4PDF({ rows, kpis: subKPI, geradoEm })
      setPdfLoading(false)
    }, 50)
  }

  const activeLabel = statFilters.size > 0
    ? `${filtered.length} de ${data.length} registro(s)`
    : `${filtered.length} registro(s) de ${data.length} no total`

  return (
    <div id="section-r4">
      {/* Sub-KPIs */}
      <div className="grid gap-3 mb-4" style={{ gridTemplateColumns: 'repeat(auto-fit, minmax(120px, 1fr))' }}>
        <KPISmall value={`${subKPI.pct_nc}%`}  label="% Não Conf. Empresa"  color="red" />
        <KPISmall value={`${subKPI.pct_c}%`}   label="% Conf. Empresa"      color="green" />
        <KPISmall value={subKPI.aprovado}       label="Aprovados"            color="green" />
        <KPISmall value={subKPI.reprovado}      label="Reprovados"           color="red" />
        <KPISmall value={subKPI.irregular}      label="Irregular (Débito)"   color="orange" />
        <KPISmall value={subKPI.alerta}         label="Alerta (verificar)"   color="amber" />
        <KPISmall value={subKPI.nao_anex}       label="Não Anexados"         color="yellow" />
        <KPISmall value={subKPI.em_analise}     label="Aguardando Análise"   color="orange" />
        <KPISmall value={subKPI.vencido}        label="Vencidos"             color="red" />
        <KPISmall value={subKPI.total}          label="Total Documentos" />
        <KPISmall value={subKPI.forn}           label="Fornecedores c/ Docs" />
      </div>

      {/* Filtro de status — pills multi-select */}
      <div className="flex flex-wrap items-center gap-2 mb-3 bg-white border border-[#e5eef1] rounded-lg px-3 py-2 shadow-sm">
        <span className="text-[11px] font-bold text-[#0E8FA3] uppercase tracking-wide mr-1">
          Filtrar por status:
        </span>
        {STATUS_OPTIONS.map(opt => (
          <button
            key={opt.value}
            onClick={() => toggleStat(opt.value)}
            className={`px-3 py-1 rounded-full text-[11px] font-bold transition-all ${
              statFilters.has(opt.value) ? opt.active : opt.inactive
            }`}
          >
            {opt.label}
          </button>
        ))}
        {statFilters.size > 0 && (
          <button
            onClick={() => setStatFilters(new Set())}
            className="ml-2 text-[11px] text-[#999] hover:text-[#DC3545] underline font-semibold"
          >
            Limpar filtro
          </button>
        )}
      </div>

      {/* Filtros Fornecedor + Busca */}
      <div className="bg-white rounded-xl shadow-sm p-4 mb-3 flex flex-wrap gap-3 items-end">
        <div>
          <label className="block text-[12px] font-bold text-[#0E8FA3] uppercase mb-1">Fornecedor</label>
          <select value={filt} onChange={e => setFilt(e.target.value)} className="border border-[#cde] rounded px-2 py-1.5 text-[13px]">
            <option value="">Todos</option>
            {fornList.map(f => <option key={f} value={f}>{f}</option>)}
          </select>
        </div>
        <div>
          <label className="block text-[12px] font-bold text-[#0E8FA3] uppercase mb-1">Competência</label>
          <select value={compFilt} onChange={e => setCompFilt(e.target.value)} className="border border-[#cde] rounded px-2 py-1.5 text-[13px]">
            <option value="">Todas</option>
            {compList.map(c => <option key={c} value={c}>{c}</option>)}
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
        <p className="text-[13px] text-[#6C757D] mb-2">{activeLabel}</p>
        <div className="overflow-x-auto">
          <table className="w-full text-[13px] border-collapse">
            <thead>
              <tr className="bg-[#0E8FA3] text-white">
                {['Fornecedor', 'Documento', 'Competência', 'Status', 'Vencimento'].map(h => (
                  <th key={h} className="px-3 py-2.5 text-left font-bold">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {filtered.map((r, i) => (
                <tr key={i} className={`border-b border-[#e5eef1] hover:bg-[#d4eef3] ${i % 2 === 1 ? 'bg-[#f0f8fa]' : ''}`}>
                  <td className="px-3 py-2">{r.Fornecedor}</td>
                  <td className="px-3 py-2">{r.Documento}</td>
                  <td className="px-3 py-2">
                    {r.Competencia
                      ? <span className="inline-block px-2 py-0.5 rounded-full text-[11px] font-bold bg-[#e8f4f7] text-[#0E8FA3]">{r.Competencia}</span>
                      : <span className="text-[#aaa]">—</span>}
                  </td>
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
