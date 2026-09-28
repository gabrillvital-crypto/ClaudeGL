import { useState, useEffect, useMemo } from 'react'
import Papa from 'papaparse'
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip,
  Legend, ResponsiveContainer,
} from 'recharts'

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

interface ChartPoint {
  mes: string        // label curto: "Dez/25"
  compKey: string    // "12/25" para ordenação
  elaboracao: number
  aprovado: number
  total: number
}

// ── Helpers ──────────────────────────────────────────────────────────────────

const MONTH_ABBR: Record<string, string> = {
  '01': 'Jan', '02': 'Fev', '03': 'Mar', '04': 'Abr',
  '05': 'Mai', '06': 'Jun', '07': 'Jul', '08': 'Ago',
  '09': 'Set', '10': 'Out', '11': 'Nov', '12': 'Dez',
}

function parseCompKey(comp: string): string | null {
  // "12/25 - Dezembro 2025" → "12/25"
  const m = comp?.match(/^(\d{2})\/(\d{2})/)
  return m ? `${m[1]}/${m[2]}` : null
}

function keyToDate(key: string): Date {
  const [mm, yy] = key.split('/')
  return new Date(2000 + parseInt(yy, 10), parseInt(mm, 10) - 1, 1)
}

function keyToLabel(key: string): string {
  const [mm, yy] = key.split('/')
  return `${MONTH_ABBR[mm] ?? mm}/${yy}`
}

// ── Tooltip personalizado ────────────────────────────────────────────────────

function CustomTooltip({ active, payload, label }: any) {
  if (!active || !payload?.length) return null
  const elab  = payload.find((p: any) => p.dataKey === 'elaboracao')?.value ?? 0
  const aprov = payload.find((p: any) => p.dataKey === 'aprovado')?.value ?? 0
  const total = elab + aprov
  const pct   = total > 0 ? Math.round(aprov / total * 100) : 0
  return (
    <div className="bg-white rounded-xl shadow-lg border border-[#e5eef1] p-3 text-[12px] min-w-[180px]">
      <p className="font-bold text-[#0A6A7A] mb-2">{label}</p>
      <div className="space-y-1">
        <div className="flex justify-between gap-4">
          <span className="flex items-center gap-1.5 text-amber-600">
            <span className="w-2.5 h-2.5 rounded-full bg-amber-400 inline-block" />
            Em elaboração
          </span>
          <span className="font-bold text-amber-700">{elab.toLocaleString('pt-BR')}</span>
        </div>
        <div className="flex justify-between gap-4">
          <span className="flex items-center gap-1.5 text-green-600">
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-500 inline-block" />
            Aprovado
          </span>
          <span className="font-bold text-green-700">{aprov.toLocaleString('pt-BR')}</span>
        </div>
        <div className="border-t border-gray-100 pt-1 flex justify-between gap-4">
          <span className="text-gray-500">Total</span>
          <span className="font-bold text-gray-700">{total.toLocaleString('pt-BR')}</span>
        </div>
        <div className="flex justify-between gap-4">
          <span className="text-gray-500">% aprovado</span>
          <span className={`font-bold ${pct >= 50 ? 'text-green-600' : 'text-amber-600'}`}>{pct}%</span>
        </div>
      </div>
    </div>
  )
}

// ── Componente principal ─────────────────────────────────────────────────────

export function CompetenciasSection() {
  const [rows,    setRows]    = useState<RawRow[]>([])
  const [loading, setLoading] = useState(true)
  const [error,   setError]   = useState<string | null>(null)

  useEffect(() => {
    fetch('/data/competencias_zurich.csv')
      .then(r => {
        if (!r.ok) throw new Error(`HTTP ${r.status}`)
        return r.text()
      })
      .then(text => {
        const result = Papa.parse<RawRow>(text, {
          header: true,
          skipEmptyLines: true,
          delimiter: '',        // auto-detect
          transformHeader: (h: string) => h.trim(),
        })
        setRows(result.data)
        setLoading(false)
      })
      .catch(e => { setError(String(e)); setLoading(false) })
  }, [])

  // ── Agregação ──────────────────────────────────────────────────────────────
  const chartData = useMemo((): ChartPoint[] => {
    if (!rows.length) return []

    const map = new Map<string, { elaboracao: number; aprovado: number }>()

    for (const r of rows) {
      const rawComp = (r as unknown as Record<string, string>)['Competência']
        ?? (r as unknown as Record<string, string>)['Competencia']
        ?? ''
      const key = parseCompKey(rawComp)
      if (!key) continue   // "A classificar" → ignora na série temporal

      const qtd = parseInt(r['Qtd Terceiros'] || '0', 10) || 0
      if (!map.has(key)) map.set(key, { elaboracao: 0, aprovado: 0 })
      const entry = map.get(key)!

      if ((r['Status da solicitação'] ?? '').trim() === 'APROVADO') {
        entry.aprovado += qtd
      } else {
        entry.elaboracao += qtd
      }
    }

    return [...map.entries()]
      .map(([key, v]) => ({
        mes: keyToLabel(key),
        compKey: key,
        elaboracao: v.elaboracao,
        aprovado:   v.aprovado,
        total:      v.elaboracao + v.aprovado,
      }))
      .filter(p => p.total > 0)                                // descarta meses sem terceiros
      .sort((a, b) => keyToDate(a.compKey).getTime() - keyToDate(b.compKey).getTime())
  }, [rows])

  // ── KPIs ───────────────────────────────────────────────────────────────────
  const totalMeses  = chartData.length
  const peakPoint   = chartData.reduce(
    (mx, p) => p.total > mx.total ? p : mx,
    { mes: '—', total: 0, elaboracao: 0, aprovado: 0, compKey: '' },
  )
  const totalAprov  = chartData.reduce((s, p) => s + p.aprovado, 0)
  const totalAll    = chartData.reduce((s, p) => s + p.total, 0)
  const pctAprov    = totalAll > 0 ? Math.round(totalAprov / totalAll * 100) : 0
  const lastPoint   = chartData[chartData.length - 1]
  const lastPct     = lastPoint && lastPoint.total > 0
    ? Math.round(lastPoint.aprovado / lastPoint.total * 100) : 0

  // ── Loading / erro ─────────────────────────────────────────────────────────
  if (loading) {
    return (
      <div className="flex items-center justify-center py-10 text-[#0E8FA3]">
        <div className="w-7 h-7 border-4 border-[#0E8FA3] border-t-transparent rounded-full animate-spin mr-3" />
        <span className="text-[13px] font-medium">Carregando dados de competência...</span>
      </div>
    )
  }

  if (error || !chartData.length) {
    return (
      <div className="text-center py-8 text-gray-400 text-sm">
        {error
          ? <><span className="text-red-400">⚠ Erro:</span> {error}</>
          : 'Nenhum dado de competência disponível — adicione competencias_zurich.csv à pasta data/'
        }
      </div>
    )
  }

  return (
    <div>
      {/* ── KPI chips ────────────────────────────────────────────────────── */}
      <div className="flex flex-wrap gap-3 mb-5">

        <div className="flex-1 min-w-[140px] bg-[#e8f6f8] border border-[#0E8FA3]/30 rounded-xl px-4 py-3">
          <p className="text-[11px] font-bold text-[#0E8FA3] uppercase tracking-wide">Competências c/ dados</p>
          <p className="text-[22px] font-bold text-[#0A6A7A] mt-0.5">{totalMeses}</p>
          <p className="text-[11px] text-gray-400">meses na série</p>
        </div>

        <div className="flex-1 min-w-[140px] bg-gray-50 border border-gray-200 rounded-xl px-4 py-3">
          <p className="text-[11px] font-bold text-gray-500 uppercase tracking-wide">Pico de terceiros</p>
          <p className="text-[18px] font-bold text-gray-700 mt-0.5">{peakPoint.mes}</p>
          <p className="text-[11px] text-gray-400">{peakPoint.total.toLocaleString('pt-BR')} terceiros</p>
        </div>

        <div className="flex-1 min-w-[140px] bg-gray-50 border border-gray-200 rounded-xl px-4 py-3">
          <p className="text-[11px] font-bold text-gray-500 uppercase tracking-wide">Total acumulado</p>
          <p className="text-[22px] font-bold text-gray-700 mt-0.5">{totalAll.toLocaleString('pt-BR')}</p>
          <p className="text-[11px] text-gray-400">terceiros na série</p>
        </div>

        <div className={`flex-1 min-w-[140px] rounded-xl px-4 py-3 border ${
          pctAprov >= 50
            ? 'bg-green-50 border-green-200'
            : 'bg-amber-50 border-amber-200'
        }`}>
          <p className={`text-[11px] font-bold uppercase tracking-wide ${pctAprov >= 50 ? 'text-green-600' : 'text-amber-600'}`}>
            % envios aprovados (série)
          </p>
          <p className={`text-[22px] font-bold mt-0.5 ${pctAprov >= 50 ? 'text-green-700' : 'text-amber-700'}`}>
            {pctAprov}%
          </p>
          <p className="text-[11px] text-gray-400">
            {lastPoint ? `${lastPoint.mes}: ${lastPct}% aprovado` : ''}
          </p>
        </div>

      </div>

      {/* ── Gráfico de barras empilhadas ──────────────────────────────────── */}
      <ResponsiveContainer width="100%" height={300}>
        <BarChart
          data={chartData}
          margin={{ top: 5, right: 20, left: 0, bottom: 5 }}
          barSize={28}
        >
          <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e5eef1" />
          <XAxis
            dataKey="mes"
            tick={{ fontSize: 11, fill: '#777' }}
            tickLine={false}
            axisLine={false}
          />
          <YAxis
            tick={{ fontSize: 11, fill: '#aaa' }}
            tickLine={false}
            axisLine={false}
            tickFormatter={v => v >= 1000 ? `${(v / 1000).toFixed(1)}k` : String(v)}
          />
          <Tooltip content={<CustomTooltip />} cursor={{ fill: 'rgba(14,143,163,0.06)' }} />
          <Legend
            formatter={v => (
              <span style={{ fontSize: 12, color: '#555' }}>
                {v === 'elaboracao' ? 'Em elaboração' : 'Aprovado'}
              </span>
            )}
            wrapperStyle={{ paddingTop: 10 }}
          />
          <Bar
            dataKey="elaboracao"
            stackId="a"
            fill="#F59E0B"
            name="elaboracao"
            radius={[0, 0, 0, 0]}
          />
          <Bar
            dataKey="aprovado"
            stackId="a"
            fill="#10B981"
            name="aprovado"
            radius={[4, 4, 0, 0]}
          />
        </BarChart>
      </ResponsiveContainer>

      <p className="text-[11px] text-gray-400 mt-1 text-center">
        Fonte: Relatório de Competências — plataforma Efcaz &nbsp;·&nbsp;
        Competências futuras (zero terceiros) e "A classificar" excluídas da série
      </p>
    </div>
  )
}
