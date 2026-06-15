import { useState } from 'react'
import { ClienteScore, StatusHS } from '../types'
import { DimensionRow } from './DimensionRow'

// Borda esquerda — única cor usada por status no container
const STATUS_BORDER: Record<StatusHS, string> = {
  verde:    'border-l-emerald-500',
  amarelo:  'border-l-amber-400',
  vermelho: 'border-l-red-500',
}

// Anel do score circle — indica status sem colorir o fundo
const STATUS_RING: Record<StatusHS, string> = {
  verde:    'ring-emerald-500/60',
  amarelo:  'ring-amber-400/60',
  vermelho: 'ring-red-500/60',
}

// Dot semântico no label
const STATUS_DOT: Record<StatusHS, string> = {
  verde:    'bg-emerald-400',
  amarelo:  'bg-amber-400',
  vermelho: 'bg-red-400',
}

const STATUS_TEXT: Record<StatusHS, string> = {
  verde:    'Saudável',
  amarelo:  'Em atenção',
  vermelho: 'Em risco',
}

// Tier — neutros, sem cor decorativa
const TIER_BADGE: Record<string, string> = {
  A:   'bg-slate-700/80 text-slate-200',
  'B+':'bg-slate-700/60 text-slate-300',
  B:   'bg-slate-800    text-slate-400',
  C:   'bg-slate-800/60 text-slate-500',
}

// Cor semântica nas mini-barras (colapso)
const DIM_BAR: Record<StatusHS, string> = {
  verde:    'bg-emerald-500',
  amarelo:  'bg-amber-400',
  vermelho: 'bg-red-500',
}

function fmt(n: number) {
  return n.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })
}

export function ClienteCard({ cs }: { cs: ClienteScore }) {
  const [expanded, setExpanded] = useState(false)
  const { input, score, status, dimensoes, alertas } = cs

  return (
    <div
      className={`bg-slate-900 rounded-xl border border-slate-800/50 border-l-4 ${STATUS_BORDER[status]} overflow-hidden transition-all`}
    >
      {/* ── Header clicável ─────────────────────────────────────────── */}
      <button
        className="w-full text-left px-6 py-5 flex items-center gap-5 hover:bg-slate-800/40 transition-colors"
        onClick={() => setExpanded(v => !v)}
      >
        {/* Score circle */}
        <div
          className={`w-14 h-14 rounded-full bg-slate-800 ring-2 ring-offset-2 ring-offset-slate-900 ${STATUS_RING[status]} flex items-center justify-center shrink-0`}
        >
          <span className="text-xl font-bold text-white tabular-nums">{score}</span>
        </div>

        {/* Identidade */}
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2.5 flex-wrap">
            <span className="font-semibold text-slate-100 text-base leading-tight">{input.cliente}</span>
            <span className={`text-[10px] font-semibold px-2 py-0.5 rounded-full ${TIER_BADGE[input.tier]}`}>
              Tier {input.tier}
            </span>
            <span className="flex items-center gap-1.5 text-xs text-slate-500">
              <span className={`w-1.5 h-1.5 rounded-full ${STATUS_DOT[status]}`} />
              {STATUS_TEXT[status]}
            </span>
          </div>

          <div className="flex items-center gap-4 mt-1 text-xs text-slate-500">
            <span>
              MRR <strong className="text-slate-300 font-semibold">{fmt(input.mrr)}</strong>
            </span>
            {input.dias_renovacao <= 90 && (
              <span className="flex items-center gap-1 text-amber-400/90 font-medium">
                <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M8.485 2.495c.673-1.167 2.357-1.167 3.03 0l6.28 10.875c.673 1.167-.17 2.625-1.516 2.625H3.72c-1.347 0-2.189-1.458-1.515-2.625L8.485 2.495zM10 5a.75.75 0 01.75.75v3.5a.75.75 0 01-1.5 0v-3.5A.75.75 0 0110 5zm0 9a1 1 0 100-2 1 1 0 000 2z" clipRule="evenodd" />
                </svg>
                Renovação em {input.dias_renovacao} dias
              </span>
            )}
          </div>

          {/* Mini-barras de dimensão (visível apenas colapsado) */}
          {!expanded && (
            <div className="flex gap-2 mt-3">
              {dimensoes.map(d => {
                const s: StatusHS = d.score >= 85 ? 'verde' : d.score >= 60 ? 'amarelo' : 'vermelho'
                return (
                  <div key={d.nome} title={`${d.nome}: ${d.score}`} className="flex flex-col items-center gap-1">
                    <div className="w-10 h-1 bg-slate-700 rounded-full overflow-hidden">
                      <div className={`h-full rounded-full ${DIM_BAR[s]}`} style={{ width: `${d.score}%` }} />
                    </div>
                    <span className="text-[9px] text-slate-600 tabular-nums leading-none">{d.score}</span>
                  </div>
                )
              })}
            </div>
          )}
        </div>

        {/* Badge alertas */}
        {alertas.length > 0 && (
          <span className="shrink-0 bg-red-500/15 text-red-400 border border-red-500/25 text-[10px] font-semibold px-2.5 py-1 rounded-full">
            {alertas.length} alerta{alertas.length > 1 ? 's' : ''}
          </span>
        )}

        {/* Chevron */}
        <svg
          className={`w-4 h-4 text-slate-600 shrink-0 transition-transform ${expanded ? 'rotate-180' : ''}`}
          fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}
        >
          <path strokeLinecap="round" strokeLinejoin="round" d="m19 9-7 7-7-7" />
        </svg>
      </button>

      {/* ── Conteúdo expandido ──────────────────────────────────────── */}
      {expanded && (
        <div className="px-6 pb-6 border-t border-slate-800/60">

          {/* Alertas */}
          {alertas.length > 0 && (
            <div className="mt-5 mb-6 bg-red-500/10 rounded-xl p-4 border border-red-500/20">
              <div className="text-[10px] font-bold text-red-400/80 mb-3 uppercase tracking-widest">
                Alertas ativos
              </div>
              <ul className="space-y-2">
                {alertas.map(a => (
                  <li key={a} className="flex items-start gap-2.5 text-sm text-red-300/90">
                    <svg className="w-3.5 h-3.5 mt-0.5 shrink-0 text-red-500" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M8.485 2.495c.673-1.167 2.357-1.167 3.03 0l6.28 10.875c.673 1.167-.17 2.625-1.516 2.625H3.72c-1.347 0-2.189-1.458-1.515-2.625L8.485 2.495zM10 5a.75.75 0 01.75.75v3.5a.75.75 0 01-1.5 0v-3.5A.75.75 0 0110 5zm0 9a1 1 0 100-2 1 1 0 000 2z" clipRule="evenodd" />
                    </svg>
                    {a}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Dimensões */}
          <div className="mt-5">
            <div className="text-[10px] font-bold text-slate-600 uppercase tracking-widest mb-4">
              Breakdown por dimensão
            </div>
            <div className="space-y-4">
              {dimensoes.map(d => <DimensionRow key={d.nome} dim={d} />)}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
