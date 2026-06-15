import { DimensionScore, MetricaScore, StatusHS } from '../types'

// Cor semântica APENAS nas barras de progresso
const BAR_COLOR: Record<StatusHS | 'nd', string> = {
  verde:    'bg-emerald-500',
  amarelo:  'bg-amber-400',
  vermelho: 'bg-red-500',
  nd:       'bg-slate-600',
}

// Badge da métrica — mínimo de cor, máximo de legibilidade
const BADGE: Record<StatusHS | 'nd', string> = {
  verde:    'bg-emerald-500/15 text-emerald-400',
  amarelo:  'bg-amber-400/15   text-amber-400',
  vermelho: 'bg-red-500/15     text-red-400',
  nd:       'bg-slate-700/50   text-slate-500',
}

function dimStatus(score: number): StatusHS | 'nd' {
  return score >= 85 ? 'verde' : score >= 60 ? 'amarelo' : 'vermelho'
}

function MetricaLine({ m, isEven }: { m: MetricaScore; isEven: boolean }) {
  return (
    <div
      className={`flex items-center gap-3 py-2 px-4 text-sm transition-colors hover:bg-slate-700/30
        ${isEven ? 'bg-slate-800/30' : ''}
        border-b border-slate-700/30 last:border-0`}
    >
      <span className="text-slate-500 w-44 shrink-0 text-xs">{m.nome}</span>
      <span className="text-slate-300 flex-1 text-xs">{m.valor}</span>
      <span className={`text-[10px] font-semibold px-2 py-0.5 rounded-full shrink-0 tabular-nums ${BADGE[m.status]}`}>
        {m.status === 'nd' ? 'N/D' : `${m.pts} pts`}
      </span>
    </div>
  )
}

export function DimensionRow({ dim }: { dim: DimensionScore }) {
  const status = dimStatus(dim.score)

  return (
    <div>
      {/* ── Cabeçalho da dimensão ─────────────────────────────────── */}
      <div className="flex items-center gap-3 mb-1.5">
        <span className="text-xs font-medium text-slate-300 w-36 shrink-0">{dim.nome}</span>

        {/* Barra de progresso */}
        <div className="flex-1 h-1.5 bg-slate-700/60 rounded-full overflow-hidden">
          <div
            className={`h-full rounded-full transition-all ${BAR_COLOR[status]}`}
            style={{ width: `${dim.score}%` }}
          />
        </div>

        {/* Score — branco sempre, contraste pelo fundo */}
        <span className="text-sm font-bold text-white tabular-nums w-8 text-right shrink-0">
          {dim.score}
        </span>

        {/* Peso — muito sutil */}
        <span className="text-[10px] text-slate-600 w-8 text-right shrink-0 tabular-nums">
          {dim.peso}%
        </span>
      </div>

      {/* ── Métricas detalhadas (tabela dark com zebra sutil) ─────── */}
      <div className="ml-36 rounded-lg overflow-hidden border border-slate-700/40 bg-slate-800/20">
        {dim.metricas.map((m, i) => (
          <MetricaLine key={m.nome} m={m} isEven={i % 2 === 1} />
        ))}
      </div>
    </div>
  )
}
