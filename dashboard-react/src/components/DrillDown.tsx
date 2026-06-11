import { useState, useMemo } from 'react'
import type { DrillDoc } from '../types'

interface Props {
  drillData: Record<string, Record<string, DrillDoc[]>>
}

function corNC(pct: number) {
  return pct <= 30 ? '#28A745' : pct <= 60 ? '#FFC107' : '#DC3545'
}

function badgeDrill(status: string) {
  const map: Record<string, string> = {
    'Aprovado':             'bg-[#d4edda] text-[#28A745]',
    'Reprovado':            'bg-[#ffeaea] text-[#DC3545]',
    'Não anexado':          'bg-[#fff3cd] text-[#856404]',
    'Aguardando Submissão': 'bg-[#fff3cd] text-[#856404]',
    'Em Análise':           'bg-[#e8f4f7] text-[#0E8FA3]',
  }
  return map[status] ?? 'bg-gray-100 text-gray-600'
}

export function DrillDown({ drillData }: Props) {
  const [level, setLevel] = useState<1 | 2 | 3>(1)
  const [selForn, setSelForn] = useState('')
  const [selTerc, setSelTerc] = useState('')

  const fornStats = useMemo(() => {
    return Object.entries(drillData).map(([forn, terceiros]) => {
      let aprov = 0, reprov = 0, naoAnex = 0, aguard = 0
      Object.values(terceiros).forEach(docs => {
        docs.forEach(d => {
          if (d.status === 'Aprovado') aprov++
          else if (d.status === 'Reprovado') reprov++
          else if (d.status === 'Não anexado') naoAnex++
          else aguard++ // Aguardando Submissão + Em Análise
        })
      })
      const total = aprov + reprov + naoAnex + aguard
      const pct_nc = total > 0 ? Math.round((reprov + naoAnex + aguard) / total * 1000) / 10 : 0
      return { forn, aprov, reprov, naoAnex, aguard, total, pct_nc, trabCount: Object.keys(terceiros).length }
    }).sort((a, b) => b.pct_nc - a.pct_nc)
  }, [drillData])

  function goLevel2(forn: string) { setSelForn(forn); setLevel(2) }
  function goLevel3(terc: string) { setSelTerc(terc); setLevel(3) }
  function back1() { setLevel(1); setSelForn(''); setSelTerc('') }
  function back2() { setLevel(2); setSelTerc('') }

  return (
    <div className="bg-white rounded-xl shadow-sm p-5">
      <p className="text-[13px] text-[#666] mb-4">
        Clique num fornecedor para ver os terceiros. Clique num terceiro para ver os documentos.
      </p>

      {level === 1 && (
        <div className="grid gap-3" style={{ gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))' }}>
          {fornStats.map(s => {
            const pAprov   = s.total > 0 ? (s.aprov   / s.total * 100) : 0
            const pReprov  = s.total > 0 ? (s.reprov  / s.total * 100) : 0
            const pNaoAnex = s.total > 0 ? (s.naoAnex / s.total * 100) : 0
            const pAguard  = s.total > 0 ? (s.aguard  / s.total * 100) : 0
            return (
              <div key={s.forn} onClick={() => goLevel2(s.forn)}
                className="bg-[#f8f9fa] rounded-xl p-4 cursor-pointer border-2 border-[#e0e0e0] hover:border-[#0E8FA3] hover:shadow-md hover:-translate-y-0.5 transition-all select-none">
                <div className="text-[30px] font-black leading-none" style={{ color: corNC(s.pct_nc) }}>{s.pct_nc}%</div>
                <div className="text-[10px] text-[#888] font-semibold uppercase mt-0.5">não aprovado</div>
                <div className="text-[12px] font-bold text-[#333] mt-1.5 leading-snug min-h-[32px]">{s.forn}</div>
                <div className="text-[11px] text-[#888] mt-1">{s.trabCount} terceiros · {s.total} docs</div>
                <div className="flex h-1.5 rounded overflow-hidden bg-[#ddd] mt-2.5">
                  <span style={{ width: `${pAprov}%`,   background: '#28A745' }} />
                  <span style={{ width: `${pReprov}%`,  background: '#DC3545' }} />
                  <span style={{ width: `${pNaoAnex}%`, background: '#FFC107' }} />
                  <span style={{ width: `${pAguard}%`,  background: '#0E8FA3' }} />
                </div>
              </div>
            )
          })}
          {fornStats.length === 0 && <p className="text-[#999] text-[13px] text-center py-6 col-span-full">Nenhum dado disponível</p>}
        </div>
      )}

      {level === 2 && (
        <div>
          <div className="flex items-center gap-2 mb-4 flex-wrap">
            <span onClick={back1} className="bg-[#e8f7fa] text-[#0E8FA3] cursor-pointer font-bold text-sm px-2.5 py-1 rounded hover:bg-[#d0eff5]">← Fornecedores</span>
            <span className="text-[#bbb] text-lg">›</span>
            <span className="font-bold text-sm text-[#333]">{selForn}</span>
          </div>
          {Object.entries(drillData[selForn] || {}).map(([terc, docs]) => {
            const aprov   = docs.filter(d => d.status === 'Aprovado').length
            const reprov  = docs.filter(d => d.status === 'Reprovado').length
            const naoAnex = docs.filter(d => d.status === 'Não anexado').length
            const aguard  = docs.filter(d => d.status === 'Aguardando Submissão' || d.status === 'Em Análise').length
            return (
              <div key={terc} onClick={() => goLevel3(terc)}
                className="flex items-center gap-3 px-4 py-3 cursor-pointer rounded-lg hover:bg-[#f0f8fa] border-b border-[#f0f0f0] transition-colors">
                <div className="flex-1 font-bold text-sm text-[#222]">{terc || '(sem nome)'}</div>
                <div className="flex gap-1.5 flex-wrap">
                  {aprov   > 0 && <span className="text-[11px] font-bold px-2 py-0.5 rounded-full bg-[#d4edda] text-[#28A745]">✓ {aprov}</span>}
                  {reprov  > 0 && <span className="text-[11px] font-bold px-2 py-0.5 rounded-full bg-[#ffeaea] text-[#DC3545]">✗ {reprov}</span>}
                  {naoAnex > 0 && <span className="text-[11px] font-bold px-2 py-0.5 rounded-full bg-[#fff3cd] text-[#856404]">○ {naoAnex}</span>}
                  {aguard  > 0 && <span className="text-[11px] font-bold px-2 py-0.5 rounded-full bg-[#e8f4f7] text-[#0E8FA3]">⏳ {aguard}</span>}
                </div>
                <span className="text-2xl text-[#bbb] font-light">›</span>
              </div>
            )
          })}
        </div>
      )}

      {level === 3 && (
        <div>
          <div className="flex items-center gap-2 mb-4 flex-wrap">
            <span onClick={back1} className="bg-[#e8f7fa] text-[#0E8FA3] cursor-pointer font-bold text-sm px-2.5 py-1 rounded hover:bg-[#d0eff5]">← Fornecedores</span>
            <span className="text-[#bbb] text-lg">›</span>
            <span onClick={back2} className="bg-[#e8f7fa] text-[#0E8FA3] cursor-pointer font-bold text-sm px-2.5 py-1 rounded hover:bg-[#d0eff5]">{selForn}</span>
            <span className="text-[#bbb] text-lg">›</span>
            <span className="font-bold text-sm text-[#333]">{selTerc}</span>
          </div>
          {(drillData[selForn]?.[selTerc] || []).map((doc, i) => (
            <div key={i} className={`flex items-center gap-3 px-4 py-2.5 border-b border-[#f0f0f0] ${i % 2 === 1 ? 'bg-[#fafafa]' : ''}`}>
              <div className="flex-1 text-[13px] text-[#333]">{doc.doc || '—'}</div>
              <span className={`text-[11px] font-bold px-2.5 py-0.5 rounded-full ${badgeDrill(doc.status)}`}>{doc.status}</span>
              <div className="text-[12px] text-[#888] min-w-[90px] text-right">{doc.venc || '—'}</div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
