import { useEffect, useState, useMemo } from 'react'
import { ClienteScore, StatusHS } from './types'
import { loadClientes } from './utils/csvLoader'
import { calcScore } from './utils/scoreCalculator'
import { ClienteCard } from './components/ClienteCard'

type Filtro = 'todos' | StatusHS | 'A' | 'B+' | 'B' | 'C'

function fmt(n: number) {
  return n.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })
}

export function App() {
  const [clientes, setClientes] = useState<ClienteScore[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [filtro, setFiltro] = useState<Filtro>('todos')
  const [busca, setBusca] = useState('')

  useEffect(() => {
    loadClientes()
      .then(inputs => setClientes(inputs.map(calcScore)))
      .catch(e => setError(String(e)))
      .finally(() => setLoading(false))
  }, [])

  const sorted = useMemo(
    () => [...clientes].sort((a, b) => b.score - a.score),
    [clientes]
  )

  const filtered = useMemo(() => {
    return sorted.filter(cs => {
      const matchesBusca = cs.input.cliente.toLowerCase().includes(busca.toLowerCase())
      const matchesFiltro =
        filtro === 'todos' ||
        filtro === cs.status ||
        filtro === cs.input.tier
      return matchesBusca && matchesFiltro
    })
  }, [sorted, filtro, busca])

  const verdes    = clientes.filter(c => c.status === 'verde').length
  const amarelos  = clientes.filter(c => c.status === 'amarelo').length
  const vermelhos = clientes.filter(c => c.status === 'vermelho').length
  const mediaScore = clientes.length > 0
    ? Math.round(clientes.reduce((s, c) => s + c.score, 0) / clientes.length)
    : 0
  const mrrTotal    = clientes.reduce((s, c) => s + c.input.mrr, 0)
  const totalAlertas = clientes.reduce((s, c) => s + c.alertas.length, 0)

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center text-slate-500 bg-slate-950">
        <div className="flex flex-col items-center gap-3">
          <div className="w-6 h-6 border-2 border-slate-700 border-t-slate-400 rounded-full animate-spin" />
          <span className="text-sm">Carregando dados...</span>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-950">
        <div className="bg-red-500/10 border border-red-500/30 rounded-xl px-6 py-4 text-red-400 text-sm">
          Erro ao carregar dados: {error}
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-slate-950">

      {/* ── Header ───────────────────────────────────────────────────── */}
      <header className="bg-slate-900 border-b border-slate-800/60 px-6 py-5">
        <div className="max-w-5xl mx-auto flex items-center justify-between">
          <div>
            <div className="flex items-center gap-2.5">
              <span className="w-2 h-2 rounded-full bg-efcaz inline-block" />
              <h1 className="text-base font-semibold text-white tracking-tight">
                Health Score — Carteira Efcaz
              </h1>
            </div>
            <p className="text-slate-500 text-xs mt-0.5 pl-4">Monitoramento interno · Gabriel Vital</p>
          </div>
          <time className="text-slate-500 text-xs tabular-nums">
            {new Date().toLocaleDateString('pt-BR', { day: '2-digit', month: 'long', year: 'numeric' })}
          </time>
        </div>
      </header>

      <main className="max-w-5xl mx-auto px-4 py-8">

        {/* ── KPIs ─────────────────────────────────────────────────────── */}
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-4 mb-4">
          <KPI label="Total"      value={clientes.length} sub="clientes" />
          <KPI label="Saudáveis"  value={verdes}    sub="verde"    dot="emerald" />
          <KPI label="Em atenção" value={amarelos}  sub="amarelo"  dot="amber"   />
          <KPI label="Em risco"   value={vermelhos} sub="vermelho" dot="red"     />
          <KPI label="Média HS"   value={mediaScore} sub="pontos"  />
          <KPI label="Alertas"    value={totalAlertas} sub="ativos"
            urgent={totalAlertas > 0}
          />
        </div>

        {/* ── MRR strip ────────────────────────────────────────────────── */}
        <div className="bg-slate-900 rounded-xl border border-slate-800/50 px-6 py-3.5 mb-8 flex items-center justify-between">
          <span className="text-slate-500 text-xs uppercase tracking-widest font-medium">MRR monitorado</span>
          <span className="font-bold text-white text-lg tabular-nums">{fmt(mrrTotal)}</span>
        </div>

        {/* ── Filtros ──────────────────────────────────────────────────── */}
        <div className="flex flex-wrap gap-2 mb-6 items-center">
          <div className="relative">
            <svg className="absolute left-2.5 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-slate-500 pointer-events-none" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="m21 21-4.35-4.35M17 11A6 6 0 1 1 5 11a6 6 0 0 1 12 0z" />
            </svg>
            <input
              type="text"
              placeholder="Buscar cliente..."
              value={busca}
              onChange={e => setBusca(e.target.value)}
              className="bg-slate-900 border border-slate-700/60 text-slate-200 placeholder-slate-600 rounded-lg pl-8 pr-3 py-1.5 text-sm focus:outline-none focus:ring-1 focus:ring-slate-500 w-48 transition-colors"
            />
          </div>

          {(['todos', 'verde', 'amarelo', 'vermelho', 'A', 'B+', 'B', 'C'] as Filtro[]).map(f => (
            <FilterChip key={f} value={f} active={filtro === f} onClick={() => setFiltro(f)} />
          ))}
        </div>

        {/* ── Cards ────────────────────────────────────────────────────── */}
        <div className="space-y-3">
          {filtered.length === 0
            ? <p className="text-center text-slate-600 py-16 text-sm">Nenhum cliente encontrado.</p>
            : filtered.map(cs => <ClienteCard key={cs.input.cliente} cs={cs} />)
          }
        </div>

        {/* ── Footer legenda ───────────────────────────────────────────── */}
        <div className="mt-12 text-xs text-slate-600 border-t border-slate-800 pt-5 space-y-1">
          <p className="text-slate-500 font-medium mb-1">Como atualizar os dados</p>
          <p>Edite <code className="bg-slate-800 text-slate-400 px-1.5 py-0.5 rounded text-[11px]">public/data/clientes.csv</code> e recarregue a página.</p>
          <p className="leading-relaxed">
            <strong className="text-slate-500">buscas_status / certidoes_status:</strong> 0=nunca | 1=configurado sem execução | 2=executando ·{' '}
            <strong className="text-slate-500">engagement_renovacao:</strong> 0=sem resposta | 1=contato feito | 2=reunião agendada/realizada ·{' '}
            <strong className="text-slate-500">rfi_trimestre:</strong> vazio = módulo não contratado ·{' '}
            <strong className="text-slate-500">nps / config_sistema_pct / dias_ultimo_login:</strong> vazio = N/D
          </p>
        </div>
      </main>
    </div>
  )
}

// ── Subcomponentes ────────────────────────────────────────────────────────────

const DOT_COLOR: Record<string, string> = {
  emerald: 'bg-emerald-400',
  amber:   'bg-amber-400',
  red:     'bg-red-400',
}

function KPI({
  label, value, sub, dot, urgent,
}: {
  label: string
  value: number
  sub: string
  dot?: 'emerald' | 'amber' | 'red'
  urgent?: boolean
}) {
  return (
    <div className="bg-slate-900 rounded-xl border border-slate-800/50 px-4 py-5 text-center flex flex-col items-center gap-1">
      <div className={`text-3xl font-bold tabular-nums ${urgent ? 'text-red-400' : 'text-white'}`}>
        {value}
      </div>
      <div className="flex items-center gap-1.5">
        {dot && <span className={`w-1.5 h-1.5 rounded-full ${DOT_COLOR[dot]} shrink-0`} />}
        <span className="text-xs text-slate-400">{label}</span>
      </div>
      {!dot && <span className="text-[10px] text-slate-600">{sub}</span>}
    </div>
  )
}

const FILTER_LABEL: Record<string, string> = {
  todos:    'Todos',
  verde:    'Saudáveis',
  amarelo:  'Atenção',
  vermelho: 'Risco',
  A: 'Tier A',
  'B+': 'Tier B+',
  B: 'Tier B',
  C: 'Tier C',
}

const FILTER_DOT: Record<string, string> = {
  verde:    'bg-emerald-400',
  amarelo:  'bg-amber-400',
  vermelho: 'bg-red-400',
}

function FilterChip({ value, active, onClick }: { value: string; active: boolean; onClick: () => void }) {
  const dot = FILTER_DOT[value]
  return (
    <button
      onClick={onClick}
      className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium border transition-all ${
        active
          ? 'bg-slate-700 text-white border-slate-600'
          : 'bg-slate-900 text-slate-400 border-slate-800 hover:border-slate-700 hover:text-slate-300'
      }`}
    >
      {dot && <span className={`w-1.5 h-1.5 rounded-full ${dot}`} />}
      {FILTER_LABEL[value] ?? value}
    </button>
  )
}
