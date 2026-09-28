import { useState, useEffect } from 'react'
import {
  getDailyLog, saveDailyLog, fetchDailyLogs,
  fetchTasksCompletedToday, fetchTasksForDate,
} from '../lib/firebase'
import { TEAL, TEAL_SOFT, NAVY, isoToday, fmtDate } from '../lib/utils'

const TODAY    = isoToday()
const TOMORROW = (() => {
  const d = new Date()
  d.setDate(d.getDate() + 1)
  return d.toISOString().split('T')[0]
})()

const WEEK_DAYS = ['Domingo', 'Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado']

const ENERGY_LABELS = {
  1: 'Exausto 😩',
  2: 'Cansado 😴',
  3: 'Normal 😐',
  4: 'Bem disposto 😊',
  5: 'Energizado! 🚀',
}

function formatLabel(dateStr) {
  const [, m, d] = dateStr.split('-')
  return `${d}/${m}`
}

// ── Gráfico de barras simples ─────────────────────────────────────────────────

function ProductivityChart({ history }) {
  const sorted = [...history].sort((a, b) => a.date.localeCompare(b.date)).slice(-14)
  const maxTasks = Math.max(...sorted.map(h => h.tasks_done_count || 0), 1)
  const BAR_MAX = 80 // px

  return (
    <div style={{ display: 'flex', alignItems: 'flex-end', gap: 6 }}>
      {sorted.map(h => {
        const count   = h.tasks_done_count || 0
        const barH    = count > 0 ? Math.max((count / maxTasks) * BAR_MAX, 8) : 2
        const isToday = h.date === TODAY
        const bg      = isToday ? TEAL : count > 0 ? '#C7E9EF' : '#F1F5F9'

        return (
          <div
            key={h.date}
            title={`${fmtDate(h.date)}: ${count} tarefa${count !== 1 ? 's' : ''}, energia ${h.energy || '-'}/5`}
            style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', flex: 1, minWidth: 0 }}
          >
            {/* Contagem */}
            <span style={{ fontSize: 10, color: '#64748B', marginBottom: 2, fontWeight: 600, minHeight: 14 }}>
              {count > 0 ? count : ''}
            </span>

            {/* Barra */}
            <div style={{ height: BAR_MAX, display: 'flex', alignItems: 'flex-end', width: '100%' }}>
              <div style={{
                width: '100%', height: barH, background: bg,
                borderRadius: '4px 4px 0 0', minWidth: 6,
              }} />
            </div>

            {/* Linha base */}
            <div style={{ height: 2, background: '#E2E8F0', width: '100%' }} />

            {/* Data */}
            <span style={{ fontSize: 9, color: '#94A3B8', marginTop: 4, fontWeight: 500 }}>
              {formatLabel(h.date)}
            </span>

            {/* Pontos de energia */}
            <div style={{ display: 'flex', gap: 2, marginTop: 4 }}>
              {[1, 2, 3, 4, 5].map(i => (
                <div key={i} style={{
                  width: 4, height: 4, borderRadius: '50%',
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

// ── Componente principal ──────────────────────────────────────────────────────

export default function TabDiario() {
  const [loading,    setLoading]    = useState(true)
  const [saving,     setSaving]     = useState(false)
  const [savedFlash, setSavedFlash] = useState(false)

  const [log,           setLog]           = useState(null)
  const [doneTasks,     setDoneTasks]     = useState([])
  const [tomorrowTasks, setTomorrowTasks] = useState([])
  const [history,       setHistory]       = useState([])

  const [doneFreeText, setDoneFreeText] = useState('')
  const [plannedText,  setPlannedText]  = useState('')
  const [energy,       setEnergy]       = useState(3)

  useEffect(() => { load() }, [])

  async function load() {
    setLoading(true)
    const [logData, done, tomorrow, hist] = await Promise.all([
      getDailyLog(TODAY),
      fetchTasksCompletedToday(),
      fetchTasksForDate(TOMORROW),
      fetchDailyLogs(30),
    ])
    setDoneTasks(done)
    setTomorrowTasks(tomorrow)
    setHistory(hist)
    if (logData) {
      setLog(logData)
      setDoneFreeText(logData.done_free_text || '')
      setPlannedText(logData.planned_text    || '')
      setEnergy(logData.energy || 3)
    }
    setLoading(false)
  }

  async function handleSave() {
    setSaving(true)
    const saved = await saveDailyLog(TODAY, {
      done_free_text:   doneFreeText,
      planned_text:     plannedText,
      energy,
      tasks_done_count: doneTasks.length,
    })
    setLog(saved)
    const hist = await fetchDailyLogs(30)
    setHistory(hist)
    setSaving(false)
    setSavedFlash(true)
    setTimeout(() => setSavedFlash(false), 2500)
  }

  // Plano registrado para hoje (ontem ou mais recente antes de hoje)
  const yesterdayLog = history
    .filter(h => h.date < TODAY)
    .sort((a, b) => b.date.localeCompare(a.date))[0]

  // Streak: dias consecutivos com check-in até hoje
  const streak = (() => {
    let count = 0
    const d = new Date()
    for (let i = 0; i < 60; i++) {
      const ds = d.toISOString().split('T')[0]
      if (history.find(h => h.date === ds)) {
        count++
        d.setDate(d.getDate() - 1)
      } else {
        break
      }
    }
    return count
  })()

  // KPIs da semana corrente (Dom–Sáb)
  const weekStart = (() => {
    const d = new Date()
    d.setDate(d.getDate() - d.getDay())
    return d.toISOString().split('T')[0]
  })()
  const thisWeekLogs    = history.filter(h => h.date >= weekStart)
  const weekTasksDone   = thisWeekLogs.reduce((s, h) => s + (h.tasks_done_count || 0), 0)
  const weekAvgEnergy   = thisWeekLogs.length
    ? (thisWeekLogs.reduce((s, h) => s + (h.energy || 0), 0) / thisWeekLogs.length).toFixed(1)
    : '—'

  const weekDay = WEEK_DAYS[new Date().getDay()]

  // ── Estilos reutilizáveis ────────────────────────────────────────────────────

  function cardStyle() {
    return { background: '#fff', borderRadius: 12, border: '1px solid #E8EEF4', padding: 20 }
  }

  function labelStyle() {
    return { fontSize: 10, fontWeight: 700, color: '#94A3B8', letterSpacing: '0.08em',
             textTransform: 'uppercase', marginBottom: 8, display: 'block' }
  }

  function textareaStyle(focused) {
    return {
      width: '100%', fontSize: 13, color: '#1E293B',
      border: `1.5px solid ${focused ? TEAL : '#E2E8F0'}`,
      borderRadius: 8, padding: '10px 12px', resize: 'none',
      outline: 'none', fontFamily: 'inherit', lineHeight: 1.6,
      background: '#FAFCFE', transition: 'border-color .15s',
    }
  }

  const [focusDone, setFocusDone] = useState(false)
  const [focusPlan, setFocusPlan] = useState(false)

  // ── Render ───────────────────────────────────────────────────────────────────

  if (loading) {
    return (
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%' }}>
        <span style={{ fontSize: 13, color: '#94A3B8' }}>Carregando diário...</span>
      </div>
    )
  }

  return (
    <div style={{ height: '100%', overflowY: 'auto', background: '#F8FAFC' }}>
      <div style={{ maxWidth: 960, margin: '0 auto', padding: '24px 24px 40px' }}>

        {/* ── Cabeçalho ─────────────────────────────────────────────────────── */}
        <div style={{ display: 'flex', flexWrap: 'wrap', alignItems: 'flex-start',
                      justifyContent: 'space-between', gap: 12, marginBottom: 20 }}>
          <div>
            <h1 style={{ margin: 0, fontSize: 20, fontWeight: 700, color: '#0F172A' }}>
              {weekDay}, {fmtDate(TODAY)}
            </h1>
            <p style={{ margin: '4px 0 0', fontSize: 13, color: '#64748B' }}>
              Registro diário de produtividade
            </p>
          </div>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8, alignItems: 'center' }}>
            {streak > 0 && (
              <span style={{ padding: '5px 12px', borderRadius: 20, fontSize: 12, fontWeight: 600,
                             background: '#FFF4E0', color: '#B8600A' }}>
                🔥 {streak} dia{streak !== 1 ? 's' : ''} seguidos
              </span>
            )}
            <span style={{ padding: '5px 12px', borderRadius: 20, fontSize: 12, fontWeight: 600,
                           background: TEAL_SOFT, color: TEAL }}>
              ✅ {doneTasks.length} tarefa{doneTasks.length !== 1 ? 's' : ''} hoje
            </span>
            {log && (
              <span style={{ padding: '5px 12px', borderRadius: 20, fontSize: 12, fontWeight: 600,
                             background: '#F0FDF4', color: '#15803D' }}>
                💾 Check-in salvo
              </span>
            )}
          </div>
        </div>

        {/* ── KPIs da semana ────────────────────────────────────────────────── */}
        {thisWeekLogs.length > 0 && (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 12, marginBottom: 20 }}>
            {[
              { label: 'Tarefas esta semana', value: weekTasksDone, icon: '📋' },
              { label: 'Energia média (semana)', value: weekAvgEnergy, icon: '⚡' },
              { label: 'Check-ins esta semana', value: thisWeekLogs.length, icon: '📅' },
            ].map(kpi => (
              <div key={kpi.label} style={{ ...cardStyle(), textAlign: 'center', padding: '16px 12px' }}>
                <div style={{ fontSize: 20, marginBottom: 4 }}>{kpi.icon}</div>
                <div style={{ fontSize: 28, fontWeight: 700, color: TEAL, lineHeight: 1 }}>{kpi.value}</div>
                <div style={{ fontSize: 11, color: '#94A3B8', marginTop: 4 }}>{kpi.label}</div>
              </div>
            ))}
          </div>
        )}

        {/* ── Planejei ontem para hoje ──────────────────────────────────────── */}
        {yesterdayLog?.planned_text && (
          <div style={{ background: '#F0FDF4', border: '1px solid #BBF7D0', borderRadius: 10,
                        padding: '12px 16px', marginBottom: 20 }}>
            <p style={{ margin: '0 0 6px', fontSize: 12, fontWeight: 700, color: '#15803D' }}>
              📌 Você planejou para hoje ({fmtDate(yesterdayLog.date)}):
            </p>
            <p style={{ margin: 0, fontSize: 13, color: '#374151', whiteSpace: 'pre-line', lineHeight: 1.6 }}>
              {yesterdayLog.planned_text}
            </p>
          </div>
        )}

        {/* ── Grid principal ────────────────────────────────────────────────── */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(340px, 1fr))', gap: 16 }}>

          {/* COLUNA ESQUERDA: O que fiz hoje */}
          <div style={cardStyle()}>
            <h2 style={{ margin: '0 0 16px', fontSize: 15, fontWeight: 700, color: '#0F172A' }}>
              📝 O que fiz hoje
            </h2>

            {/* Tarefas do app concluídas hoje */}
            {doneTasks.length > 0 && (
              <div style={{ marginBottom: 16 }}>
                <span style={labelStyle()}>Tarefas concluídas no app</span>
                <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
                  {doneTasks.map(t => (
                    <div key={t.id} style={{ display: 'flex', alignItems: 'flex-start', gap: 8,
                                            background: TEAL_SOFT, borderRadius: 8, padding: '7px 10px' }}>
                      <span style={{ color: TEAL, fontWeight: 700, fontSize: 13, marginTop: 1, flexShrink: 0 }}>✓</span>
                      <span style={{ fontSize: 13, color: '#1E293B', flex: 1, lineHeight: 1.4 }}>{t.title}</span>
                      {t.clients?.name && (
                        <span style={{ flexShrink: 0, fontSize: 10, padding: '2px 7px', borderRadius: 10,
                                       background: '#EDF2F7', color: '#4A5568', fontWeight: 600 }}>
                          {t.clients.name}
                        </span>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Texto livre */}
            <div style={{ marginBottom: 16 }}>
              <span style={labelStyle()}>Outras realizações</span>
              <textarea
                rows={5}
                value={doneFreeText}
                onChange={e => setDoneFreeText(e.target.value)}
                onFocus={() => setFocusDone(true)}
                onBlur={() => setFocusDone(false)}
                placeholder="Reuniões, entregas, alinhamentos, follow-ups, prospecções..."
                style={textareaStyle(focusDone)}
              />
            </div>

            {/* Energia */}
            <div>
              <span style={labelStyle()}>Como foi sua energia hoje?</span>
              <div style={{ display: 'flex', gap: 8 }}>
                {[1, 2, 3, 4, 5].map(v => (
                  <button
                    key={v}
                    onClick={() => setEnergy(v)}
                    style={{
                      flex: 1, height: 36, borderRadius: 8, fontSize: 13, fontWeight: 700,
                      cursor: 'pointer', border: 'none', transition: 'all .15s',
                      background: energy === v ? TEAL : '#F1F5F9',
                      color:      energy === v ? '#fff' : '#64748B',
                      boxShadow:  energy === v ? `0 0 0 2px ${TEAL}44` : 'none',
                    }}
                  >
                    {v}
                  </button>
                ))}
              </div>
              <p style={{ margin: '6px 0 0', fontSize: 12, color: '#94A3B8' }}>{ENERGY_LABELS[energy]}</p>
            </div>
          </div>

          {/* COLUNA DIREITA: Tarefas para amanhã */}
          <div style={cardStyle()}>
            <h2 style={{ margin: '0 0 16px', fontSize: 15, fontWeight: 700, color: '#0F172A' }}>
              🎯 Tarefas para amanhã
            </h2>

            {/* Tarefas com deadline amanhã já no app */}
            {tomorrowTasks.length > 0 && (
              <div style={{ marginBottom: 16 }}>
                <span style={labelStyle()}>Já agendadas no app para amanhã</span>
                <div style={{ display: 'flex', flexDirection: 'column', gap: 5 }}>
                  {tomorrowTasks.map(t => (
                    <div key={t.id} style={{ display: 'flex', alignItems: 'flex-start', gap: 8,
                                            fontSize: 13, color: '#374151' }}>
                      <span style={{ flexShrink: 0, marginTop: 1, color: '#94A3B8' }}>◇</span>
                      <span style={{ flex: 1 }}>{t.title}</span>
                    </div>
                  ))}
                </div>
                <hr style={{ margin: '12px 0', border: 'none', borderTop: '1px solid #E8EEF4' }} />
              </div>
            )}

            <span style={labelStyle()}>Outras prioridades para amanhã</span>
            <textarea
              rows={tomorrowTasks.length > 0 ? 8 : 12}
              value={plannedText}
              onChange={e => setPlannedText(e.target.value)}
              onFocus={() => setFocusPlan(true)}
              onBlur={() => setFocusPlan(false)}
              placeholder={"Liste o que quer fazer amanhã:\n— Reunião de alinhamento Zurich\n— Enviar proposta Dock Brasil\n— Análise de saúde da carteira"}
              style={textareaStyle(focusPlan)}
            />
          </div>
        </div>

        {/* ── Botão Salvar ───────────────────────────────────────────────────── */}
        <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: 16 }}>
          <button
            onClick={handleSave}
            disabled={saving}
            style={{
              display: 'flex', alignItems: 'center', gap: 8,
              padding: '10px 24px', borderRadius: 8, border: 'none',
              fontSize: 13, fontWeight: 700, color: '#fff', cursor: saving ? 'not-allowed' : 'pointer',
              background: savedFlash ? '#22C55E' : saving ? '#94A3B8' : TEAL,
              transition: 'background .2s',
            }}
          >
            {saving ? '⏳ Salvando...' : savedFlash ? '✓ Check-in salvo!' : '💾 Salvar check-in'}
          </button>
        </div>

        {/* ── Gráfico histórico ─────────────────────────────────────────────── */}
        {history.length > 0 && (
          <div style={{ ...cardStyle(), marginTop: 20 }}>
            <h2 style={{ margin: '0 0 4px', fontSize: 15, fontWeight: 700, color: '#0F172A' }}>
              📈 Histórico de produtividade
            </h2>
            <p style={{ margin: '0 0 20px', fontSize: 12, color: '#94A3B8' }}>
              Barras = tarefas concluídas · Pontos = energia (1–5)
            </p>
            <ProductivityChart history={history} />
          </div>
        )}

      </div>
    </div>
  )
}
