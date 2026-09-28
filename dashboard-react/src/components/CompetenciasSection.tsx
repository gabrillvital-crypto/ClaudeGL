import { useState, useEffect, useMemo } from 'react'
import Papa from 'papaparse'

// ── Tipos ────────────────────────────────────────────────────────────────────

interface RawRow {
  Fornecedor: string
  'Fornecedor CPF/CNPJ': string
  'Status da solicitação': string
  Competência: string
  'Qtd Terceiros': string
  Regulares: string
  'Com pendências': string
}

interface CompRow {
  compKey: string      // "12/25" para ordenar
  label: string        // "Dezembro/2025"
  fornecedores: number // distintos
  total: number
  elaboracao: number
  aprovado: number
  pct: number          // % aprovado
}

// ── Helpers ──────────────────────────────────────────────────────────────────

const MONTH_FULL: Record<string, string> = {
  '01': 'Janeiro',   '02': 'Fevereiro', '03': 'Março',    '04': 'Abril',
  '05': 'Maio',      '06': 'Junho',     '07': 'Julho',    '08': 'Agosto',
  '09': 'Setembro',  '10': 'Outubro',   '11': 'Novembro', '12': 'Dezembro',
}

function parseKey(comp: string): string | null {
  const m = (comp ?? '').match(/^(\d{2})\/(\d{2})/)
  return m ? `${m[1]}/${m[2]}` : null
}

function keyToDate(key: string): Date {
  const [mm, yy] = key.split('/')
  return new Date(2000 + parseInt(yy, 10), parseInt(mm, 10) - 1, 1)
}

function keyToLabel(key: string): string {
  const [mm, yy] = key.split('/')
  return `${MONTH_FULL[mm] ?? mm}/${2000 + parseInt(yy, 10)}`
}

const PAGE_SIZE = 10

// ── Barra de progresso inline ────────────────────────────────────────────────

function ProgBar({ pct }: { pct: number }) {
  const color = pct >= 70 ? '#10B981' : pct >= 40 ? '#F59E0B' : '#EF4444'
  return (
    <div className="flex items-center gap-2 min-w-[120px]">
      <div className="flex-1 h-2 bg-gray-100 rounded-full overflow-hidden">
        <div
          className="h-full rounded-full transition-all"
          style={{ width: `${pct}%`, backgroundColor: color }}
        />
      </div>
      <span className="text-[12px] font-bold w-9 text-right" style={{ color }}>
        {pct}%
      </span>
    </div>
  )
}

// ── Badge de status ──────────────────────────────────────────────────────────

function StatusBadge({ value, type }: { value: number; type: 'elab' | 'aprov' }) {
  if (value === 0) return <span className="text-[#aaa]">—</span>
  const cls = type === 'aprov'
    ? 'bg-green-100 text-green-700'
    : 'bg-amber-100 text-amber-700'
  return (
    <span className={`inline-block px-2 py-0.5 rounded-full text-[11px] font-bold ${cls}`}>
      {value.toLocaleString('pt-BR')}
    </span>
  )
}

// ── Componente principal ─────────────────────────────────────────────────────

export function CompetenciasSection() {
  const [rows,    setRows]    = useState<RawRow[]>([])
  const [loading, setLoading] = useState(true)
  const [error,   setError]   = useState<string | null>(null)
  const [page,    setPage]    = useState(0)

  useEffect(() => {
    fetch('/data/competencias_zurich.csv')
      .then(r => { if (!r.ok) throw new Error(`HTTP ${r.status}`); return r.text() })
      .then(text => {
        const result = Papa.parse<RawRow>(text, {
          header: true, skipEmptyLines: true,
          delimiter: '', transformHeader: (h: string) => h.trim(),
        })
        setRows(result.data)
        setLoading(false)
      })
      .catch(e => { setError(String(e)); setLoading(false) })
  }, [])

  // ── Agregação por competência ─────────────────────────────────────────────
  const tableData = useMemo((): CompRow[] => {
    if (!rows.length) return []

    const map = new Map<string, {
      elaboracao: number; aprovado: number; fornSet: Set<string>
    }>()

    for (const r of rows) {
      const raw = (r as unknown as Record<string, string>)
      const comp = raw['Competência'] ?? raw['Competencia'] ?? ''
      const key  = parseKey(comp)
      if (!key) continue  // "A classificar" → fora da série temporal

      const qtd  = parseInt(raw['Qtd Terceiros'] || '0', 10) || 0
      const cnpj = raw['Fornecedor CPF/CNPJ'] ?? ''
      if (!map.has(key)) map.set(key, { elaboracao: 0, aprovado: 0, fornSet: new Set() })
      const e = map.get(key)!

      const status = (raw['Status da solicitação'] ?? '').trim()
      if (status === 'APROVADO') e.aprovado   += qtd
      else                        e.elaboracao += qtd
      if (cnpj) e.fornSet.add(cnpj)
    }

    return [...map.entries()]
      .map(([key, v]) => {
        const total = v.elaboracao + v.aprovado
        return {
          compKey:     key,
          label:       keyToLabel(key),
          fornecedores: v.fornSet.size,
          total,
          elaboracao:  v.elaboracao,
          aprovado:    v.aprovado,
          pct:         total > 0 ? Math.round(v.aprovado / total * 100) : 0,
        }
      })
      .filter(p => p.total > 0)
      .sort((a, b) => keyToDate(a.compKey).getTime() - keyToDate(b.compKey).getTime())
  }, [rows])

  // ── KPIs ─────────────────────────────────────────────────────────────────
  const totalMeses = tableData.length
  const peak       = tableData.reduce((mx, r) => r.total > mx.total ? r : mx,
    { label: '—', total: 0 } as CompRow)
  const totalAll   = tableData.reduce((s, r) => s + r.total, 0)
  const totalAprov = tableData.reduce((s, r) => s + r.aprovado, 0)
  const pctGeral   = totalAll > 0 ? Math.round(totalAprov / totalAll * 100) : 0
  const lastRow    = tableData[tableData.length - 1]

  // ── Paginação ─────────────────────────────────────────────────────────────
  const totalPages = Math.ceil(tableData.length / PAGE_SIZE)
  const pageData   = tableData.slice(page * PAGE_SIZE, (page + 1) * PAGE_SIZE)

  // ── Loading / erro ────────────────────────────────────────────────────────
  if (loading) return (
    <div className="flex items-center justify-center py-10 text-[#0E8FA3]">
      <div className="w-7 h-7 border-4 border-[#0E8FA3] border-t-transparent rounded-full animate-spin mr-3" />
      <span className="text-[13px] font-medium">Carregando competências...</span>
    </div>
  )

  if (error || !tableData.length) return (
    <div className="text-center py-8 text-gray-400 text-sm">
      {error
        ? <><span className="text-red-400">⚠ Erro:</span> {error}</>
        : 'Nenhum dado — adicione competencias_zurich.csv em public/data/'
      }
    </div>
  )

  return (
    <div>

      {/* ── KPI chips ──────────────────────────────────────────────────────── */}
      <div className="flex flex-wrap gap-3 mb-5">
        <div className="flex-1 min-w-[130px] bg-[#e8f6f8] border border-[#0E8FA3]/30 rounded-xl px-4 py-3">
          <p className="text-[11px] font-bold text-[#0E8FA3] uppercase tracking-wide">Competências com dados</p>
          <p className="text-[22px] font-bold text-[#0A6A7A] mt-0.5">{totalMeses}</p>
          <p className="text-[11px] text-gray-400">meses na série</p>
        </div>

        <div className="flex-1 min-w-[130px] bg-gray-50 border border-gray-200 rounded-xl px-4 py-3">
          <p className="text-[11px] font-bold text-gray-500 uppercase tracking-wide">Pico de terceiros</p>
          <p className="text-[17px] font-bold text-gray-700 mt-0.5 leading-tight">{peak.label}</p>
          <p className="text-[11px] text-gray-400">{peak.total.toLocaleString('pt-BR')} terceiros</p>
        </div>

        <div className="flex-1 min-w-[130px] bg-gray-50 border border-gray-200 rounded-xl px-4 py-3">
          <p className="text-[11px] font-bold text-gray-500 uppercase tracking-wide">Total acumulado</p>
          <p className="text-[22px] font-bold text-gray-700 mt-0.5">{totalAll.toLocaleString('pt-BR')}</p>
          <p className="text-[11px] text-gray-400">terceiros na série</p>
        </div>

        <div className={`flex-1 min-w-[130px] rounded-xl px-4 py-3 border ${
          pctGeral >= 50 ? 'bg-green-50 border-green-200' : 'bg-amber-50 border-amber-200'
        }`}>
          <p className={`text-[11px] font-bold uppercase tracking-wide ${pctGeral >= 50 ? 'text-green-600' : 'text-amber-600'}`}>
            % aprovados (série)
          </p>
          <p className={`text-[22px] font-bold mt-0.5 ${pctGeral >= 50 ? 'text-green-700' : 'text-amber-700'}`}>
            {pctGeral}%
          </p>
          <p className="text-[11px] text-gray-400">
            {lastRow ? `Últ. mês: ${lastRow.label.split('/')[0]} ${lastRow.pct}%` : ''}
          </p>
        </div>
      </div>

      {/* ── Tabela ─────────────────────────────────────────────────────────── */}
      <div className="bg-white rounded-xl shadow-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-[13px] border-collapse">
            <thead>
              <tr className="bg-[#0E8FA3] text-white">
                <th className="px-4 py-3 text-left font-bold">Competência</th>
                <th className="px-4 py-3 text-center font-bold">Qtd Fornecedores</th>
                <th className="px-4 py-3 text-center font-bold">Total Terceiros</th>
                <th className="px-4 py-3 text-center font-bold">Em Elaboração</th>
                <th className="px-4 py-3 text-center font-bold">Aprovados</th>
                <th className="px-4 py-3 text-left font-bold min-w-[160px]">% Aprovado</th>
              </tr>
            </thead>
            <tbody>
              {pageData.map((row, i) => (
                <tr
                  key={row.compKey}
                  className={`border-b border-[#e5eef1] hover:bg-[#d4eef3] transition-colors ${
                    i % 2 === 1 ? 'bg-[#f0f8fa]' : 'bg-white'
                  }`}
                >
                  <td className="px-4 py-3 font-semibold text-[#0A6A7A] uppercase tracking-wide">
                    {row.label}
                  </td>
                  <td className="px-4 py-3 text-center text-gray-600">
                    {row.fornecedores}
                  </td>
                  <td className="px-4 py-3 text-center font-bold text-gray-700">
                    {row.total.toLocaleString('pt-BR')}
                  </td>
                  <td className="px-4 py-3 text-center">
                    <StatusBadge value={row.elaboracao} type="elab" />
                  </td>
                  <td className="px-4 py-3 text-center">
                    <StatusBadge value={row.aprovado} type="aprov" />
                  </td>
                  <td className="px-4 py-3">
                    <ProgBar pct={row.pct} />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* ── Paginação ──────────────────────────────────────────────────── */}
        {totalPages > 1 && (
          <div className="flex items-center justify-between px-4 py-3 border-t border-[#e5eef1] bg-gray-50">
            <p className="text-[12px] text-gray-400">
              {page * PAGE_SIZE + 1}–{Math.min((page + 1) * PAGE_SIZE, tableData.length)} de {tableData.length} competências
            </p>
            <div className="flex gap-1">
              <button
                onClick={() => setPage(0)} disabled={page === 0}
                className="px-2 py-1 rounded text-[12px] font-bold disabled:opacity-30 hover:bg-[#e8f6f8] text-[#0A6A7A] transition-colors"
              >⟪</button>
              <button
                onClick={() => setPage(p => Math.max(0, p - 1))} disabled={page === 0}
                className="px-2 py-1 rounded text-[12px] font-bold disabled:opacity-30 hover:bg-[#e8f6f8] text-[#0A6A7A] transition-colors"
              >‹</button>
              {Array.from({ length: totalPages }, (_, i) => (
                <button key={i} onClick={() => setPage(i)}
                  className={`px-2.5 py-1 rounded text-[12px] font-bold transition-colors ${
                    i === page
                      ? 'bg-[#0E8FA3] text-white'
                      : 'hover:bg-[#e8f6f8] text-[#0A6A7A]'
                  }`}>
                  {i + 1}
                </button>
              ))}
              <button
                onClick={() => setPage(p => Math.min(totalPages - 1, p + 1))} disabled={page === totalPages - 1}
                className="px-2 py-1 rounded text-[12px] font-bold disabled:opacity-30 hover:bg-[#e8f6f8] text-[#0A6A7A] transition-colors"
              >›</button>
              <button
                onClick={() => setPage(totalPages - 1)} disabled={page === totalPages - 1}
                className="px-2 py-1 rounded text-[12px] font-bold disabled:opacity-30 hover:bg-[#e8f6f8] text-[#0A6A7A] transition-colors"
              >⟫</button>
            </div>
          </div>
        )}
      </div>

      <p className="text-[11px] text-gray-400 mt-2 text-center">
        Fonte: Relatório de Competências — plataforma Efcaz &nbsp;·&nbsp;
        Competências futuras (zero terceiros) e "A classificar" excluídas da série
      </p>

    </div>
  )
}
