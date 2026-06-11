import { useState, useMemo } from 'react'
import type { SitTerceiroRow } from '../types'

type StatusCounts = { aprov: number; reprov: number; naoAnex: number; aguard: number }

function countStatuses(docs: SitTerceiroRow[]): StatusCounts {
  const c: StatusCounts = { aprov: 0, reprov: 0, naoAnex: 0, aguard: 0 }
  docs.forEach(d => {
    if (d.Status === 'Aprovado') c.aprov++
    else if (d.Status === 'Reprovado') c.reprov++
    else if (d.Status === 'Não anexado') c.naoAnex++
    else c.aguard++
  })
  return c
}

function StatusBadges({ c }: { c: StatusCounts }) {
  return (
    <div className="flex gap-1 flex-wrap">
      {c.aprov   > 0 && <span className="text-[11px] font-bold px-2 py-0.5 rounded-full bg-[#d4edda] text-[#28A745]">✓ {c.aprov}</span>}
      {c.reprov  > 0 && <span className="text-[11px] font-bold px-2 py-0.5 rounded-full bg-[#ffeaea] text-[#DC3545]">✗ {c.reprov}</span>}
      {c.naoAnex > 0 && <span className="text-[11px] font-bold px-2 py-0.5 rounded-full bg-[#fff3cd] text-[#856404]">○ {c.naoAnex}</span>}
      {c.aguard  > 0 && <span className="text-[11px] font-bold px-2 py-0.5 rounded-full bg-[#e8f4f7] text-[#0E8FA3]">⏳ {c.aguard}</span>}
    </div>
  )
}

function docBadge(status: string) {
  const m: Record<string, string> = {
    'Aprovado':             'bg-[#d4edda] text-[#28A745]',
    'Reprovado':            'bg-[#ffeaea] text-[#DC3545]',
    'Não anexado':          'bg-[#fff3cd] text-[#856404]',
    'Aguardando Submissão': 'bg-[#fff3cd] text-[#856404]',
    'Em Análise':           'bg-[#e8f4f7] text-[#0E8FA3]',
  }
  return (
    <span className={`inline-block px-2 py-0.5 rounded-full text-[11px] font-bold ${m[status] ?? 'bg-gray-100 text-gray-600'}`}>
      {status}
    </span>
  )
}

interface TercRow {
  terc: string
  docs: SitTerceiroRow[]
  counts: StatusCounts
}

interface FornGroup {
  forn: string
  tercList: TercRow[]
  total: number
  pct_c: number
  pct_nc: number
  counts: StatusCounts
}

interface Props {
  data: SitTerceiroRow[]
}

export function GrupoEmpresaView({ data }: Props) {
  const [expanded, setExpanded] = useState<Set<string>>(new Set())
  const [expandedTerc, setExpandedTerc] = useState<Set<string>>(new Set())

  const groups = useMemo<FornGroup[]>(() => {
    const map: Record<string, Record<string, SitTerceiroRow[]>> = {}
    data.forEach(r => {
      if (!map[r.Fornecedor]) map[r.Fornecedor] = {}
      if (!map[r.Fornecedor][r.Terceiro]) map[r.Fornecedor][r.Terceiro] = []
      map[r.Fornecedor][r.Terceiro].push(r)
    })

    return Object.entries(map)
      .map(([forn, tercs]) => {
        const allDocs = Object.values(tercs).flat()
        const total = allDocs.length
        const counts = countStatuses(allDocs)
        const pct_c = total > 0 ? Math.round(counts.aprov / total * 1000) / 10 : 0
        const pct_nc = Math.round((100 - pct_c) * 10) / 10
        const tercList: TercRow[] = Object.entries(tercs)
          .sort(([a], [b]) => a.localeCompare(b))
          .map(([terc, docs]) => ({ terc, docs, counts: countStatuses(docs) }))
        return { forn, tercList, total, pct_c, pct_nc, counts }
      })
      .sort((a, b) => b.pct_nc - a.pct_nc)
  }, [data])

  function toggleForn(forn: string) {
    setExpanded(prev => {
      const next = new Set(prev)
      next.has(forn) ? next.delete(forn) : next.add(forn)
      return next
    })
  }

  function toggleTerc(key: string) {
    setExpandedTerc(prev => {
      const next = new Set(prev)
      next.has(key) ? next.delete(key) : next.add(key)
      return next
    })
  }

  const expandAll = () => setExpanded(new Set(groups.map(g => g.forn)))
  const collapseAll = () => { setExpanded(new Set()); setExpandedTerc(new Set()) }

  return (
    <div>
      {/* Toolbar */}
      <div className="flex items-center gap-3 mb-4">
        <button
          onClick={expandAll}
          className="text-[12px] text-[#0E8FA3] font-bold hover:underline transition-colors"
        >
          ▼ Expandir tudo
        </button>
        <span className="text-[#d0d0d0]">|</span>
        <button
          onClick={collapseAll}
          className="text-[12px] text-[#0E8FA3] font-bold hover:underline transition-colors"
        >
          ▲ Recolher tudo
        </button>
        <span className="ml-auto text-[12px] text-[#888]">
          {groups.length} empresa(s) · {data.length} doc(s)
        </span>
      </div>

      {/* Cards */}
      <div className="space-y-2.5">
        {groups.map(g => {
          const isOpen = expanded.has(g.forn)
          const borderColor =
            g.pct_nc <= 30 ? '#10B981' : g.pct_nc <= 60 ? '#FFC107' : '#EF4444'

          return (
            <div
              key={g.forn}
              className="bg-white rounded-xl shadow-sm overflow-hidden"
              style={{ borderLeft: `4px solid ${borderColor}` }}
            >
              {/* Header do grupo (clicável) */}
              <div
                className="flex items-center gap-3 px-5 py-3.5 cursor-pointer hover:bg-[#f8fafb] transition-colors select-none"
                onClick={() => toggleForn(g.forn)}
              >
                <div className="flex-1 min-w-0">
                  <span className="font-bold text-[14px] text-[#1a2a35]">{g.forn}</span>
                  <span className="ml-3 text-[11px] text-[#888]">
                    {g.tercList.length} terceiro(s) · {g.total} doc(s)
                  </span>
                </div>

                <div className="flex items-center gap-2 shrink-0">
                  <span
                    className="text-[11px] font-bold px-2.5 py-0.5 rounded-full"
                    style={{
                      background: `${borderColor}22`,
                      color: borderColor,
                    }}
                  >
                    {g.pct_nc}% NC
                  </span>
                  <span className="text-[11px] font-bold px-2.5 py-0.5 rounded-full bg-[#d4edda] text-[#28A745]">
                    {g.pct_c}% ✓
                  </span>
                  <StatusBadges c={g.counts} />
                </div>

                <span className="text-[#aaa] text-xl font-light shrink-0">
                  {isOpen ? '▲' : '▼'}
                </span>
              </div>

              {/* Conteúdo expandido */}
              {isOpen && (
                <div className="border-t border-[#f0f0f0]">
                  {g.tercList.map(({ terc, docs, counts }) => {
                    const tercKey = `${g.forn}|||${terc}`
                    const isTercOpen = expandedTerc.has(tercKey)

                    return (
                      <div key={terc} className="border-b border-[#f5f5f5] last:border-0">
                        {/* Linha do terceiro */}
                        <div
                          className="flex items-center gap-3 px-6 py-2.5 bg-[#f8f9fa] cursor-pointer hover:bg-[#f0f4f5] transition-colors select-none"
                          onClick={() => toggleTerc(tercKey)}
                        >
                          <span className="text-[#0E8FA3]">👤</span>
                          <span className="font-semibold text-[13px] text-[#333] flex-1">
                            {terc || '(sem nome)'}
                          </span>
                          <span className="text-[11px] text-[#888]">
                            {docs.length} doc(s)
                          </span>
                          <StatusBadges c={counts} />
                          <span className="text-[#bbb] font-light">
                            {isTercOpen ? '▲' : '▼'}
                          </span>
                        </div>

                        {/* Documentos do terceiro */}
                        {isTercOpen && (
                          <div>
                            {docs.map((doc, i) => (
                              <div
                                key={i}
                                className={`flex items-center gap-3 px-10 py-2 ${
                                  i % 2 === 0 ? '' : 'bg-[#fafafa]'
                                }`}
                              >
                                <span className="flex-1 text-[12px] text-[#444]">
                                  {doc.Documento || '—'}
                                </span>
                                {docBadge(doc.Status)}
                                <span className="text-[11px] text-[#888] min-w-[85px] text-right">
                                  {doc.Vencimento || '—'}
                                </span>
                              </div>
                            ))}
                          </div>
                        )}
                      </div>
                    )
                  })}
                </div>
              )}
            </div>
          )
        })}

        {groups.length === 0 && (
          <div className="text-center py-10 text-[#999] text-[13px]">
            Nenhum dado disponível para o filtro ativo
          </div>
        )}
      </div>
    </div>
  )
}
