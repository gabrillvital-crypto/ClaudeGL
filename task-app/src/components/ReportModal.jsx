import { useState } from 'react'
import { fetchDoneRange, fetchClients } from '../lib/firebase'
import { isoToday, fmtDate, fmtDateTime, TEAL, TEAL_SOFT, NAVY } from '../lib/utils'

function addDays(iso, n) {
  const d = new Date(iso)
  d.setDate(d.getDate() + n)
  return d.toISOString().split('T')[0]
}

function mondayOfWeek(iso) {
  const d = new Date(iso)
  const day = d.getDay() || 7
  d.setDate(d.getDate() - day + 1)
  return d.toISOString().split('T')[0]
}

function firstOfMonth(iso) {
  return iso.slice(0, 7) + '-01'
}

function buildTextSummary(tasks, clients, dateFrom, dateTo) {
  const clientMap = {}
  for (const c of clients) clientMap[c.id] = c.name

  // Agrupa por cliente
  const groups = {}
  for (const t of tasks) {
    const key = t.client_id ? (clientMap[t.client_id] || 'Sem cliente') : 'Sem cliente'
    if (!groups[key]) groups[key] = []
    groups[key].push(t)
  }

  const lines = []
  lines.push(`RESUMO DE ATIVIDADES — ${fmtDate(dateFrom)} a ${fmtDate(dateTo)}`)
  lines.push(`${tasks.length} tarefa${tasks.length !== 1 ? 's' : ''} concluída${tasks.length !== 1 ? 's' : ''}`)
  lines.push('')

  // Clientes com tarefas primeiro, sem cliente por último
  const sorted = Object.entries(groups).sort(([a], [b]) => {
    if (a === 'Sem cliente') return 1
    if (b === 'Sem cliente') return -1
    return a.localeCompare(b)
  })

  for (const [clientName, taskList] of sorted) {
    lines.push(`${clientName.toUpperCase()} (${taskList.length})`)
    for (const t of taskList) {
      const prio = t.priority === 'alta' ? ' ⚡' : ''
      lines.push(`  · ${t.title}${prio}`)
    }
    lines.push('')
  }

  lines.push(`Gerado em ${fmtDateTime(new Date().toISOString())}`)
  return lines.join('\n')
}

export default function ReportModal({ onClose }) {
  const today = isoToday()
  const [dateFrom,  setDateFrom]  = useState(mondayOfWeek(today))
  const [dateTo,    setDateTo]    = useState(today)
  const [clientFilter, setClientFilter] = useState('todos')
  const [loading,   setLoading]   = useState(false)
  const [summary,   setSummary]   = useState('')
  const [taskCount, setTaskCount] = useState(null)
  const [copied,    setCopied]    = useState(false)
  const [clients,   setClients]   = useState([])

  useState(() => {
    fetchClients().then(setClients).catch(() => {})
  }, [])

  function setWeek()  { setDateFrom(mondayOfWeek(today)); setDateTo(today); setSummary('') }
  function set15()    { setDateFrom(addDays(today, -14)); setDateTo(today); setSummary('') }
  function setMonth() { setDateFrom(firstOfMonth(today)); setDateTo(today); setSummary('') }

  async function generate() {
    setLoading(true)
    setSummary('')
    try {
      const from  = dateFrom + 'T00:00:00'
      const to    = dateTo   + 'T23:59:59'
      let tasks = await fetchDoneRange('todas', from, to)

      // Filtro por cliente
      if (clientFilter !== 'todos') {
        tasks = tasks.filter(t => t.client_id === clientFilter)
      }

      tasks.sort((a, b) => new Date(b.completed_at) - new Date(a.completed_at))
      setTaskCount(tasks.length)

      if (!tasks.length) {
        setSummary('Nenhuma tarefa concluida no periodo selecionado.')
      } else {
        setSummary(buildTextSummary(tasks, clients, dateFrom, dateTo))
      }
    } catch (err) {
      setSummary('Erro ao gerar resumo: ' + err.message)
    } finally {
      setLoading(false)
    }
  }

  async function copy() {
    try {
      await navigator.clipboard.writeText(summary)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    } catch {
      /* fallback: selecionar o textarea */
    }
  }

  // ── Estilos ──────────────────────────────────────────────────────────────────

  const chipActive = { background: TEAL, color: '#fff', border: 'none' }
  const chipIdle   = { background: '#F1F5F9', color: '#64748B', border: 'none' }

  return (
    <div style={{
      position:'fixed', inset:0, zIndex:50,
      display:'flex', alignItems:'center', justifyContent:'center',
      background:'rgba(0,0,0,0.45)', padding:16,
    }}>
      <div style={{
        background:'#fff', borderRadius:16, width:'100%', maxWidth:440,
        boxShadow:'0 20px 60px rgba(0,0,0,0.18)', overflow:'hidden',
      }}>
        {/* Header */}
        <div style={{ background: NAVY, padding:'16px 20px', display:'flex', alignItems:'center', justifyContent:'space-between' }}>
          <span style={{ color:'#fff', fontWeight:700, fontSize:15 }}>Resumo de Atividades</span>
          <button onClick={onClose} style={{ background:'none', border:'none', color:'rgba(255,255,255,0.6)', fontSize:18, cursor:'pointer', lineHeight:1 }}>
            x
          </button>
        </div>

        <div style={{ padding:'20px 20px 0' }}>

          {/* Atalhos */}
          <p style={{ margin:'0 0 8px', fontSize:10, fontWeight:700, color:'#94A3B8', textTransform:'uppercase', letterSpacing:'0.07em' }}>
            Periodo
          </p>
          <div style={{ display:'flex', gap:8, marginBottom:12, flexWrap:'wrap' }}>
            {[['Esta semana', setWeek], ['Ultimos 15 dias', set15], ['Este mes', setMonth]].map(([lbl, fn]) => (
              <button key={lbl} onClick={() => { fn(); setSummary('') }}
                style={{ fontSize:12, padding:'6px 12px', borderRadius:20, fontWeight:600, cursor:'pointer',
                         background: TEAL_SOFT, color: TEAL, border: 'none' }}>
                {lbl}
              </button>
            ))}
          </div>

          {/* Datas */}
          <div style={{ display:'flex', gap:12, marginBottom:16 }}>
            <div style={{ flex:1 }}>
              <label style={{ fontSize:11, color:'#94A3B8', display:'block', marginBottom:4 }}>De</label>
              <input type="date" value={dateFrom} onChange={e => { setDateFrom(e.target.value); setSummary('') }}
                style={{ width:'100%', fontSize:13, border:'1.5px solid #E2E8F0', borderRadius:8,
                         padding:'7px 10px', outline:'none', fontFamily:'inherit', boxSizing:'border-box' }} />
            </div>
            <div style={{ flex:1 }}>
              <label style={{ fontSize:11, color:'#94A3B8', display:'block', marginBottom:4 }}>Ate</label>
              <input type="date" value={dateTo} onChange={e => { setDateTo(e.target.value); setSummary('') }}
                style={{ width:'100%', fontSize:13, border:'1.5px solid #E2E8F0', borderRadius:8,
                         padding:'7px 10px', outline:'none', fontFamily:'inherit', boxSizing:'border-box' }} />
            </div>
          </div>

          {/* Filtro por cliente */}
          {clients.length > 0 && (
            <div style={{ marginBottom:16 }}>
              <p style={{ margin:'0 0 6px', fontSize:10, fontWeight:700, color:'#94A3B8', textTransform:'uppercase', letterSpacing:'0.07em' }}>
                Filtrar por cliente
              </p>
              <select value={clientFilter} onChange={e => { setClientFilter(e.target.value); setSummary('') }}
                style={{ width:'100%', fontSize:13, border:'1.5px solid #E2E8F0', borderRadius:8,
                         padding:'7px 10px', outline:'none', fontFamily:'inherit', background:'#fff', cursor:'pointer' }}>
                <option value="todos">Todos os clientes</option>
                {clients.map(c => (
                  <option key={c.id} value={c.id}>{c.name}</option>
                ))}
              </select>
            </div>
          )}

          {/* Resumo em texto */}
          {summary && (
            <div style={{ marginBottom:16 }}>
              <div style={{ display:'flex', justifyContent:'space-between', alignItems:'center', marginBottom:6 }}>
                <span style={{ fontSize:11, fontWeight:700, color: TEAL }}>
                  {taskCount} tarefa{taskCount !== 1 ? 's' : ''} encontrada{taskCount !== 1 ? 's' : ''}
                </span>
                <button onClick={copy}
                  style={{ fontSize:12, padding:'4px 12px', borderRadius:6, border:'none', cursor:'pointer',
                           background: copied ? '#22C55E' : TEAL_SOFT, color: copied ? '#fff' : TEAL,
                           fontWeight:600, transition:'all .15s' }}>
                  {copied ? 'Copiado!' : 'Copiar texto'}
                </button>
              </div>
              <textarea readOnly value={summary} rows={10}
                style={{ width:'100%', fontSize:12, fontFamily:'monospace', lineHeight:1.6,
                         border:'1px solid #E2E8F0', borderRadius:8, padding:'10px 12px',
                         resize:'none', background:'#F8FAFC', color:'#374151',
                         outline:'none', boxSizing:'border-box' }} />
            </div>
          )}
        </div>

        {/* Footer */}
        <div style={{ display:'flex', gap:8, padding:'0 20px 20px' }}>
          <button onClick={onClose}
            style={{ flex:1, fontSize:13, padding:'10px 0', borderRadius:10, border:'none',
                     background:'#F1F5F9', color:'#64748B', cursor:'pointer', fontWeight:600 }}>
            Fechar
          </button>
          <button onClick={generate} disabled={loading}
            style={{ flex:1, fontSize:13, fontWeight:700, padding:'10px 0', borderRadius:10, border:'none',
                     color:'#fff', cursor: loading ? 'not-allowed' : 'pointer',
                     background: loading ? '#94A3B8' : TEAL, transition:'background .15s' }}>
            {loading ? 'Gerando...' : summary ? 'Atualizar' : 'Gerar resumo'}
          </button>
        </div>
      </div>
    </div>
  )
}
