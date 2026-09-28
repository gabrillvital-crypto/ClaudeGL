import { useState, useEffect } from 'react'
import {
  getDailyLog, saveDailyLog, fetchDailyLogs,
  fetchTasksCompletedToday, fetchTasksForDate,
  addTask, setTaskStatus, fetchClients,
} from '../lib/firebase'
import { extractTasksWithClients } from '../lib/claude'
import { TEAL, TEAL_SOFT, isoToday, fmtDate } from '../lib/utils'

const TODAY    = isoToday()
const TOMORROW = (() => {
  const d = new Date()
  d.setDate(d.getDate() + 1)
  return d.toISOString().split('T')[0]
})()

const WEEK_DAYS     = ['Domingo', 'Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado']
const ENERGY_LABELS = { 1:'Exausto 😩', 2:'Cansado 😴', 3:'Normal 😐', 4:'Bem disposto 😊', 5:'Energizado! 🚀' }

function formatLabel(dateStr) {
  const [, m, d] = dateStr.split('-')
  return `${d}/${m}`
}

// ── Gráfico de barras ─────────────────────────────────────────────────────────

function ProductivityChart({ history }) {
  const sorted = [...history].sort((a, b) => a.date.localeCompare(b.date)).slice(-14)
  const maxTasks = Math.max(...sorted.map(h => h.tasks_done_count || 0), 1)
  const BAR_MAX = 72

  return (
    <div style={{ display: 'flex', alignItems: 'flex-end', gap: 6 }}>
      {sorted.map(h => {
        const count   = h.tasks_done_count || 0
        const barH    = count > 0 ? Math.max((count / maxTasks) * BAR_MAX, 8) : 2
        const isToday = h.date === TODAY
        return (
          <div key={h.date} title={`${fmtDate(h.date)}: ${count} tarefa(s), energia ${h.energy || '-'}/5`}
            style={{ display:'flex', flexDirection:'column', alignItems:'center', flex:1, minWidth:0 }}>
            <span style={{ fontSize:10, color:'#64748B', marginBottom:2, fontWeight:600, minHeight:14 }}>
              {count > 0 ? count : ''}
            </span>
            <div style={{ height: BAR_MAX, display:'flex', alignItems:'flex-end', width:'100%' }}>
              <div style={{
                width:'100%', height: barH, borderRadius:'4px 4px 0 0', minWidth:6,
                background: isToday ? TEAL : count > 0 ? '#C7E9EF' : '#F1F5F9',
              }} />
            </div>
            <div style={{ height:2, background:'#E2E8F0', width:'100%' }} />
            <span style={{ fontSize:9, color:'#94A3B8', marginTop:4, fontWeight:500 }}>
              {formatLabel(h.date)}
            </span>
            <div style={{ display:'flex', gap:2, marginTop:4 }}>
              {[1,2,3,4,5].map(i => (
                <div key={i} style={{
                  width:4, height:4, borderRadius:'50%',
                  background: i <= (h.energy || 0) ? '#F59E0B' : '#E2E8F0',
                }} />
              ))}
            </div>
          </div>
        )
      })}
    </div>
  )
}

// ── Lista de tarefas extraídas pela IA ───────────────────────────────────────

function ExtractedList({ items, onToggle, onCreate, creating, label, btnColor }) {
  if (!items.length) return null
  const PRIO = { alta:{ bg:'#FDECEA', color:'#B83232' }, media:{ bg:'#FDF4DC', color:'#8B6A10' }, baixa:{ bg:'#E8F7EE', color:'#27875A' } }

  return (
    <div style={{ marginTop:12, background:'#F8FAFC', border:'1px solid #E2E8F0', borderRadius:8, padding:12 }}>
      <p style={{ margin:'0 0 10px', fontSize:11, fontWeight:700, color:'#64748B', textTransform:'uppercase', letterSpacing:'0.07em' }}>
        ✨ {items.length} item{items.length !== 1 ? 's' : ''} identificado{items.length !== 1 ? 's' : ''} pela IA
      </p>
      <div style={{ display:'flex', flexDirection:'column', gap:6, marginBottom:12 }}>
        {items.map((t, i) => {
          const p = PRIO[t.priority] || PRIO.media
          return (
            <label key={i} style={{ display:'flex', alignItems:'flex-start', gap:8, cursor:'pointer',
                                    padding:'6px 8px', borderRadius:6,
                                    background: t.selected ? '#fff' : '#F1F5F9',
                                    border: `1px solid ${t.selected ? '#E2E8F0' : 'transparent'}` }}>
              <input type="checkbox" checked={t.selected}
                onChange={() => onToggle(i)}
                style={{ marginTop:2, accentColor: TEAL, flexShrink:0 }} />
              <div style={{ flex:1, minWidth:0 }}>
                <div style={{ display:'flex', alignItems:'center', gap:6, flexWrap:'wrap' }}>
                  <span style={{ fontSize:13, color: t.selected ? '#1E293B' : '#94A3B8',
                                 textDecoration: t.selected ? 'none' : 'line-through' }}>
                    {t.title}
                  </span>
                  {t.client_name && (
                    <span style={{ fontSize:10, padding:'2px 7px', borderRadius:10, fontWeight:600,
                                   background:'rgba(20,179,204,0.12)', color:'#0E8FA3', flexShrink:0 }}>
                      🔗 {t.client_name}
                    </span>
                  )}
                </div>
                {t.notes && (
                  <span style={{ display:'block', fontSize:11, color:'#94A3B8', marginTop:1 }}>{t.notes}</span>
                )}
              </div>
              <span style={{ fontSize:10, padding:'2px 7px', borderRadius:10, fontWeight:600,
                             background: p.bg, color: p.color, flexShrink:0 }}>
                {t.priority}
              </span>
            </label>
          )
        })}
      </div>
      <button onClick={onCreate} disabled={creating || !items.some(t => t.selected)}
        style={{
          width:'100%', padding:'8px 0', borderRadius:7, border:'none',
          fontSize:13, fontWeight:700, color:'#fff', cursor:'pointer',
          background: creating || !items.some(t => t.selected) ? '#94A3B8' : btnColor,
          transition:'background .15s',
        }}>
        {creating ? '⏳ Criando...' : label}
      </button>
    </div>
  )
}

// ── Componente principal ──────────────────────────────────────────────────────

export default function TabDiario() {
  const [loading,    setLoading]    = useState(true)
  const [error,      setError]      = useState(null)
  const [saving,     setSaving]     = useState(false)
  const [savedFlash, setSavedFlash] = useState(false)

  const [log,           setLog]           = useState(null)
  const [doneTasks,     setDoneTasks]     = useState([])
  const [tomorrowTasks, setTomorrowTasks] = useState([])
  const [history,       setHistory]       = useState([])
  const [clients,       setClients]       = useState([])

  const [doneFreeText, setDoneFreeText] = useState('')
  const [plannedText,  setPlannedText]  = useState('')
  const [energy,       setEnergy]       = useState(3)
  const [focusDone,    setFocusDone]    = useState(false)
  const [focusPlan,    setFocusPlan]    = useState(false)

  // IA: done
  const [extractingDone, setExtractingDone] = useState(false)
  const [extractedDone,  setExtractedDone]  = useState([])
  const [creatingDone,   setCreatingDone]   = useState(false)

  // IA: plan
  const [extractingPlan, setExtractingPlan] = useState(false)
  const [extractedPlan,  setExtractedPlan]  = useState([])
  const [creatingPlan,   setCreatingPlan]   = useState(false)

  useEffect(() => { load() }, [])

  async function load() {
    setLoading(true)
    setError(null)
    try {
      const [logData, done, tomorrow, hist, clientList] = await Promise.all([
        getDailyLog(TODAY),
        fetchTasksCompletedToday(),
        fetchTasksForDate(TOMORROW),
        fetchDailyLogs(30),
        fetchClients(),
      ])
      setDoneTasks(done)
      setTomorrowTasks(tomorrow)
      setHistory(hist)
      setClients(clientList)
      if (logData) {
        setLog(logData)
        setDoneFreeText(logData.done_free_text || '')
        setPlannedText(logData.planned_text    || '')
        setEnergy(logData.energy || 3)
      }
    } catch (err) {
      console.error('Erro ao carregar diário:', err)
      setError(err.message || 'Erro ao carregar dados do Firebase.')
    } finally {
      setLoading(false)
    }
  }

  async function handleSave() {
    setSaving(true)
    try {
      const saved = await saveDailyLog(TODAY, {
        done_free_text:   doneFreeText,
        planned_text:     plannedText,
        energy,
        tasks_done_count: doneTasks.length,
      })
      setLog(saved)
      const hist = await fetchDailyLogs(30)
      setHistory(hist)
      setSavedFlash(true)
      setTimeout(() => setSavedFlash(false), 2500)
    } catch (err) {
      console.error('Erro ao salvar:', err)
      alert('Erro ao salvar: ' + err.message)
    } finally {
      setSaving(false)
    }
  }

  // ── IA: extrair realizações ───────────────────────────────────────────────

  async function handleExtractDone() {
    if (!doneFreeText.trim()) return
    setExtractingDone(true)
    setExtractedDone([])
    try {
      const items = await extractTasksWithClients(doneFreeText, clients, 'profissional')
      setExtractedDone(items.map(t => ({ ...t, selected: true })))
    } catch (err) {
      alert('Erro na extração: ' + err.message)
    } finally {
      setExtractingDone(false)
    }
  }

  async function handleCreateDone() {
    const selecionados = extractedDone.filter(t => t.selected)
    if (!selecionados.length) return
    setCreatingDone(true)
    try {
      for (const t of selecionados) {
        const task = await addTask({ tab: t.tab, title: t.title, notes: t.notes, priority: t.priority, client_id: t.client_id || null })
        await setTaskStatus(task.id, 'done')
      }
      setExtractedDone([])
      const done = await fetchTasksCompletedToday()
      setDoneTasks(done)
    } catch (err) {
      alert('Erro ao criar tarefas: ' + err.message)
    } finally {
      setCreatingDone(false)
    }
  }

  // ── IA: extrair planejamento ──────────────────────────────────────────────

  async function handleExtractPlan() {
    if (!plannedText.trim()) return
    setExtractingPlan(true)
    setExtractedPlan([])
    try {
      const items = await extractTasksWithClients(plannedText, clients, 'profissional')
      setExtractedPlan(items.map(t => ({ ...t, selected: true })))
    } catch (err) {
      alert('Erro na extração: ' + err.message)
    } finally {
      setExtractingPlan(false)
    }
  }

  async function handleCreatePlan() {
    const selecionados = extractedPlan.filter(t => t.selected)
    if (!selecionados.length) return
    setCreatingPlan(true)
    try {
      for (const t of selecionados) {
        await addTask({ tab: t.tab, title: t.title, notes: t.notes, priority: t.priority, deadline: TOMORROW, client_id: t.client_id || null })
      }
      setExtractedPlan([])
      const tomorrow = await fetchTasksForDate(TOMORROW)
      setTomorrowTasks(tomorrow)
    } catch (err) {
      alert('Erro ao criar tarefas: ' + err.message)
    } finally {
      setCreatingPlan(false)
    }
  }

  // ── Derivações ────────────────────────────────────────────────────────────

  const yesterdayLog = history
    .filter(h => h.date < TODAY)
    .sort((a, b) => b.date.localeCompare(a.date))[0]

  const streak = (() => {
    let count = 0
    const d = new Date()
    for (let i = 0; i < 60; i++) {
      const ds = d.toISOString().split('T')[0]
      if (history.find(h => h.date === ds)) { count++; d.setDate(d.getDate() - 1) }
      else break
    }
    return count
  })()

  const weekStart = (() => {
    const d = new Date(); d.setDate(d.getDate() - d.getDay())
    return d.toISOString().split('T')[0]
  })()
  const thisWeekLogs  = history.filter(h => h.date >= weekStart)
  const weekTasksDone = thisWeekLogs.reduce((s, h) => s + (h.tasks_done_count || 0), 0)
  const weekAvgEnergy = thisWeekLogs.length
    ? (thisWeekLogs.reduce((s, h) => s + (h.energy || 0), 0) / thisWeekLogs.length).toFixed(1) : '—'

  const weekDay = WEEK_DAYS[new Date().getDay()]

  // ── Helpers de estilo ─────────────────────────────────────────────────────

  const card = { background:'#fff', borderRadius:12, border:'1px solid #E8EEF4', padding:20 }
  const label = { fontSize:10, fontWeight:700, color:'#94A3B8', letterSpacing:'0.08em',
                  textTransform:'uppercase', marginBottom:8, display:'block' }
  const txtArea = (focused) => ({
    width:'100%', fontSize:13, color:'#1E293B', fontFamily:'inherit', lineHeight:1.6,
    border:`1.5px solid ${focused ? TEAL : '#E2E8F0'}`, borderRadius:8,
    padding:'10px 12px', resize:'none', outline:'none', background:'#FAFCFE',
    transition:'border-color .15s', boxSizing:'border-box',
  })
  const aiBtn = (disabled) => ({
    display:'flex', alignItems:'center', gap:6,
    padding:'7px 14px', borderRadius:7, border:'none', fontSize:12, fontWeight:700,
    cursor: disabled ? 'not-allowed' : 'pointer',
    background: disabled ? '#F1F5F9' : TEAL_SOFT,
    color: disabled ? '#94A3B8' : TEAL,
    transition:'background .15s',
  })

  // ── Telas de estado ───────────────────────────────────────────────────────

  if (loading) return (
    <div style={{ display:'flex', alignItems:'center', justifyContent:'center', height:'100%' }}>
      <span style={{ fontSize:13, color:'#94A3B8' }}>Carregando diário...</span>
    </div>
  )

  if (error) return (
    <div style={{ display:'flex', flexDirection:'column', alignItems:'center', justifyContent:'center', height:'100%', gap:12 }}>
      <span style={{ fontSize:14, color:'#B83232' }}>⚠️ {error}</span>
      <button onClick={load} style={{ padding:'8px 20px', borderRadius:8, border:'none',
        background: TEAL, color:'#fff', fontSize:13, fontWeight:700, cursor:'pointer' }}>
        Tentar novamente
      </button>
    </div>
  )

  // ── Render principal ──────────────────────────────────────────────────────

  return (
    <div style={{ height:'100%', overflowY:'auto', background:'#F8FAFC' }}>
      <div style={{ maxWidth:960, margin:'0 auto', padding:'24px 24px 40px' }}>

        {/* Cabeçalho */}
        <div style={{ display:'flex', flexWrap:'wrap', alignItems:'flex-start',
                      justifyContent:'space-between', gap:12, marginBottom:20 }}>
          <div>
            <h1 style={{ margin:0, fontSize:20, fontWeight:700, color:'#0F172A' }}>
              {weekDay}, {fmtDate(TODAY)}
            </h1>
            <p style={{ margin:'4px 0 0', fontSize:13, color:'#64748B' }}>
              Registro diário de produtividade
            </p>
          </div>
          <div style={{ display:'flex', flexWrap:'wrap', gap:8, alignItems:'center' }}>
            {streak > 0 && (
              <span style={{ padding:'5px 12px', borderRadius:20, fontSize:12, fontWeight:600,
                             background:'#FFF4E0', color:'#B8600A' }}>
                🔥 {streak} dia{streak !== 1 ? 's' : ''} seguidos
              </span>
            )}
            <span style={{ padding:'5px 12px', borderRadius:20, fontSize:12, fontWeight:600,
                           background: TEAL_SOFT, color: TEAL }}>
              ✅ {doneTasks.length} tarefa{doneTasks.length !== 1 ? 's' : ''} hoje
            </span>
            {log && (
              <span style={{ padding:'5px 12px', borderRadius:20, fontSize:12, fontWeight:600,
                             background:'#F0FDF4', color:'#15803D' }}>
                💾 Check-in salvo
              </span>
            )}
          </div>
        </div>

        {/* KPIs semanais */}
        {thisWeekLogs.length > 0 && (
          <div style={{ display:'grid', gridTemplateColumns:'repeat(3,1fr)', gap:12, marginBottom:20 }}>
            {[
              { label:'Tarefas esta semana',    value: weekTasksDone,       icon:'📋' },
              { label:'Energia média (semana)', value: weekAvgEnergy,       icon:'⚡' },
              { label:'Check-ins esta semana',  value: thisWeekLogs.length, icon:'📅' },
            ].map(k => (
              <div key={k.label} style={{ ...card, textAlign:'center', padding:'16px 12px' }}>
                <div style={{ fontSize:20, marginBottom:4 }}>{k.icon}</div>
                <div style={{ fontSize:26, fontWeight:700, color:TEAL, lineHeight:1 }}>{k.value}</div>
                <div style={{ fontSize:11, color:'#94A3B8', marginTop:4 }}>{k.label}</div>
              </div>
            ))}
          </div>
        )}

        {/* Planejado ontem */}
        {yesterdayLog?.planned_text && (
          <div style={{ background:'#F0FDF4', border:'1px solid #BBF7D0', borderRadius:10,
                        padding:'12px 16px', marginBottom:20 }}>
            <p style={{ margin:'0 0 6px', fontSize:12, fontWeight:700, color:'#15803D' }}>
              📌 Você planejou para hoje ({fmtDate(yesterdayLog.date)}):
            </p>
            <p style={{ margin:0, fontSize:13, color:'#374151', whiteSpace:'pre-line', lineHeight:1.6 }}>
              {yesterdayLog.planned_text}
            </p>
          </div>
        )}

        {/* Grid principal */}
        <div style={{ display:'grid', gridTemplateColumns:'repeat(auto-fit, minmax(340px, 1fr))', gap:16 }}>

          {/* ── ESQUERDA: O que fiz hoje ── */}
          <div style={card}>
            <h2 style={{ margin:'0 0 16px', fontSize:15, fontWeight:700, color:'#0F172A' }}>
              📝 O que fiz hoje
            </h2>

            {/* Tarefas concluídas auto-detectadas */}
            {doneTasks.length > 0 && (
              <div style={{ marginBottom:16 }}>
                <span style={label}>Tarefas concluídas no app</span>
                <div style={{ display:'flex', flexDirection:'column', gap:6 }}>
                  {doneTasks.map(t => (
                    <div key={t.id} style={{ display:'flex', alignItems:'flex-start', gap:8,
                                            background: TEAL_SOFT, borderRadius:8, padding:'7px 10px' }}>
                      <span style={{ color:TEAL, fontWeight:700, fontSize:13, marginTop:1, flexShrink:0 }}>✓</span>
                      <span style={{ fontSize:13, color:'#1E293B', flex:1, lineHeight:1.4 }}>{t.title}</span>
                      {t.clients?.name && (
                        <span style={{ flexShrink:0, fontSize:10, padding:'2px 7px', borderRadius:10,
                                       background:'#EDF2F7', color:'#4A5568', fontWeight:600 }}>
                          {t.clients.name}
                        </span>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Texto livre + botão IA */}
            <div style={{ marginBottom:12 }}>
              <span style={label}>Outras realizações</span>
              <textarea
                rows={5}
                value={doneFreeText}
                onChange={e => setDoneFreeText(e.target.value)}
                onFocus={() => setFocusDone(true)}
                onBlur={() => setFocusDone(false)}
                placeholder="Descreva o que mais você fez hoje: reuniões, entregas, alinhamentos, follow-ups..."
                style={txtArea(focusDone)}
              />
              <div style={{ display:'flex', justifyContent:'flex-end', marginTop:6 }}>
                <button
                  onClick={handleExtractDone}
                  disabled={extractingDone || !doneFreeText.trim()}
                  style={aiBtn(extractingDone || !doneFreeText.trim())}
                >
                  {extractingDone ? '⏳ Analisando...' : '✨ Identificar tarefas com IA'}
                </button>
              </div>
            </div>

            {/* Resultado da extração: done */}
            <ExtractedList
              items={extractedDone}
              onToggle={i => setExtractedDone(d => d.map((t, idx) => idx === i ? { ...t, selected: !t.selected } : t))}
              onCreate={handleCreateDone}
              creating={creatingDone}
              label="✅ Criar como tarefas concluídas"
              btnColor="#22C55E"
            />

            {/* Energia */}
            <div style={{ marginTop: extractedDone.length ? 16 : 0 }}>
              <span style={label}>Como foi sua energia hoje?</span>
              <div style={{ display:'flex', gap:8 }}>
                {[1,2,3,4,5].map(v => (
                  <button key={v} onClick={() => setEnergy(v)}
                    style={{
                      flex:1, height:36, borderRadius:8, fontSize:13, fontWeight:700,
                      cursor:'pointer', border:'none', transition:'all .15s',
                      background: energy === v ? TEAL : '#F1F5F9',
                      color:      energy === v ? '#fff' : '#64748B',
                      boxShadow:  energy === v ? `0 0 0 2px ${TEAL}44` : 'none',
                    }}>
                    {v}
                  </button>
                ))}
              </div>
              <p style={{ margin:'6px 0 0', fontSize:12, color:'#94A3B8' }}>{ENERGY_LABELS[energy]}</p>
            </div>
          </div>

          {/* ── DIREITA: Para amanhã ── */}
          <div style={card}>
            <h2 style={{ margin:'0 0 16px', fontSize:15, fontWeight:700, color:'#0F172A' }}>
              🎯 Tarefas para amanhã
            </h2>

            {/* Tarefas já agendadas para amanhã */}
            {tomorrowTasks.length > 0 && (
              <div style={{ marginBottom:16 }}>
                <span style={label}>Já agendadas no app para amanhã</span>
                <div style={{ display:'flex', flexDirection:'column', gap:5 }}>
                  {tomorrowTasks.map(t => (
                    <div key={t.id} style={{ display:'flex', alignItems:'flex-start', gap:8, fontSize:13, color:'#374151' }}>
                      <span style={{ flexShrink:0, marginTop:1, color:'#94A3B8' }}>◇</span>
                      <span style={{ flex:1 }}>{t.title}</span>
                    </div>
                  ))}
                </div>
                <hr style={{ margin:'12px 0', border:'none', borderTop:'1px solid #E8EEF4' }} />
              </div>
            )}

            {/* Texto livre + botão IA */}
            <span style={label}>Outras prioridades para amanhã</span>
            <textarea
              rows={tomorrowTasks.length > 0 ? 7 : 10}
              value={plannedText}
              onChange={e => setPlannedText(e.target.value)}
              onFocus={() => setFocusPlan(true)}
              onBlur={() => setFocusPlan(false)}
              placeholder={"Liste o que quer fazer amanhã:\n— Reunião Zurich\n— Proposta Dock Brasil\n— Análise saúde da carteira"}
              style={txtArea(focusPlan)}
            />
            <div style={{ display:'flex', justifyContent:'flex-end', marginTop:6 }}>
              <button
                onClick={handleExtractPlan}
                disabled={extractingPlan || !plannedText.trim()}
                style={aiBtn(extractingPlan || !plannedText.trim())}
              >
                {extractingPlan ? '⏳ Analisando...' : '✨ Criar tarefas com IA'}
              </button>
            </div>

            {/* Resultado da extração: plan */}
            <ExtractedList
              items={extractedPlan}
              onToggle={i => setExtractedPlan(d => d.map((t, idx) => idx === i ? { ...t, selected: !t.selected } : t))}
              onCreate={handleCreatePlan}
              creating={creatingPlan}
              label="➕ Criar tarefas no app"
              btnColor={TEAL}
            />
          </div>
        </div>

        {/* Botão salvar */}
        <div style={{ display:'flex', justifyContent:'flex-end', marginTop:16 }}>
          <button onClick={handleSave} disabled={saving}
            style={{
              display:'flex', alignItems:'center', gap:8,
              padding:'10px 24px', borderRadius:8, border:'none',
              fontSize:13, fontWeight:700, color:'#fff', cursor: saving ? 'not-allowed' : 'pointer',
              background: savedFlash ? '#22C55E' : saving ? '#94A3B8' : TEAL,
              transition:'background .2s',
            }}>
            {saving ? '⏳ Salvando...' : savedFlash ? '✓ Check-in salvo!' : '💾 Salvar check-in'}
          </button>
        </div>

        {/* Gráfico histórico */}
        {history.length > 0 && (
          <div style={{ ...card, marginTop:20 }}>
            <h2 style={{ margin:'0 0 4px', fontSize:15, fontWeight:700, color:'#0F172A' }}>
              📈 Histórico de produtividade
            </h2>
            <p style={{ margin:'0 0 20px', fontSize:12, color:'#94A3B8' }}>
              Barras = tarefas concluídas · Pontos = energia (1–5)
            </p>
            <ProductivityChart history={history} />
          </div>
        )}

      </div>
    </div>
  )
}
