import { useState, useEffect, useCallback } from 'react'
import { fetchTasks, addTask, setTaskStatus, fetchChecklist } from '../lib/supabase'
import supabase from '../lib/supabase'
import TaskCard from '../components/TaskCard'
import DatePicker from '../components/DatePicker'

export default function TabList({ tab, onOpenTask }) {
  const [tasks, setTasks] = useState([])
  const [showDone, setShowDone] = useState(false)
  const [prio, setPrio] = useState('todos')
  const [loading, setLoading] = useState(true)
  const [showAdd, setShowAdd] = useState(false)
  const [newTitle, setNewTitle] = useState('')
  const [newPrio, setNewPrio] = useState('media')
  const [newDeadline, setNewDeadline] = useState(null)
  const [showDateAdd, setShowDateAdd] = useState(false)
  const [addError, setAddError] = useState('')
  const [saving, setSaving] = useState(false)

  const load = useCallback(async () => {
    const data = await fetchTasks(tab, showDone, prio)
    // Bulk-load checklists
    const ids = data.map(t => t.id)
    if (ids.length) {
      const { data: ck } = await supabase.from('checklist_items').select('*').in('task_id', ids)
      const byId = {}
      for (const item of ck || []) {
        if (!byId[item.task_id]) byId[item.task_id] = []
        byId[item.task_id].push(item)
      }
      data.forEach(t => { t._checklist = byId[t.id] || [] })
    }
    setTasks(data)
    setLoading(false)
  }, [tab, showDone, prio])

  useEffect(() => { load() }, [load])

  // Polling a cada 5s
  useEffect(() => {
    const interval = setInterval(load, 5000)
    return () => clearInterval(interval)
  }, [load])

  async function handleAdd() {
    const title = newTitle.trim()
    if (!title) return
    setSaving(true)
    setAddError('')
    try {
      await addTask({ tab, title, priority: newPrio, deadline: newDeadline })
      setNewTitle(''); setNewPrio('media'); setNewDeadline(null); setShowAdd(false)
      await load()
    } catch (err) {
      setAddError('Erro ao salvar: ' + (err.message || 'verifique a conexão'))
    } finally {
      setSaving(false)
    }
  }

  async function handleStatusChange(id, status) {
    await setTaskStatus(id, status)
    load()
  }

  const tabLabel = tab === 'pessoal' ? 'Pessoal' : 'Profissional Efcaz'
  const pending = tasks.filter(t => t.status !== 'done').length
  const done = tasks.filter(t => t.status === 'done').length

  return (
    <div className="flex flex-col h-full">
      {/* Barra de filtros */}
      <div className="flex items-center gap-2 px-5 py-3 bg-white flex-wrap" style={{ borderBottom: '1px solid #E8EEF4' }}>
        <div className="flex gap-1">
          {['todos', 'alta', 'media', 'baixa'].map(p => (
            <button
              key={p}
              onClick={() => setPrio(p)}
              className="text-xs px-3 py-1.5 rounded-lg font-medium transition-colors"
              style={prio === p
                ? { background: '#0E8FA3', color: '#fff' }
                : { background: '#F1F5F9', color: '#64748B' }
              }
            >
              {p === 'todos' ? 'Todos' : p === 'alta' ? 'Alta' : p === 'media' ? 'Média' : 'Baixa'}
            </button>
          ))}
        </div>

        <button
          onClick={() => setShowDone(v => !v)}
          className="text-xs px-3 py-1.5 rounded-lg font-medium transition-colors"
          style={showDone
            ? { background: '#1E293B', color: '#fff' }
            : { background: '#F1F5F9', color: '#64748B' }
          }
        >
          {showDone ? 'Ocultar concluídas' : `Concluídas (${done})`}
        </button>

        <div className="flex-1" />

        <span className="text-xs font-medium" style={{ color: '#94A3B8' }}>
          {pending} pendente{pending !== 1 ? 's' : ''}
        </span>

        <button
          onClick={() => setShowAdd(v => !v)}
          className="text-xs font-semibold px-4 py-1.5 rounded-lg text-white transition-opacity hover:opacity-90"
          style={{ background: '#0E8FA3' }}
        >
          + Nova tarefa
        </button>
      </div>

      {/* Formulário de adição */}
      {showAdd && (
        <div className="mx-5 mt-3 mb-1 p-4 rounded-xl space-y-3" style={{ background: '#F8FAFC', border: '1px solid #E8EEF4' }}>
          <input
            autoFocus
            className="w-full text-sm rounded-lg px-3 py-2 outline-none"
            style={{ border: '1px solid #CBD5E1', color: '#1E293B' }}
            placeholder="Título da tarefa…"
            value={newTitle}
            onChange={e => setNewTitle(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && handleAdd()}
          />
          {addError && <p className="text-xs" style={{ color: '#B91C1C' }}>{addError}</p>}
          <div className="flex gap-2 flex-wrap items-center">
            {['alta', 'media', 'baixa'].map(p => {
              const colors = { alta: '#B83232', media: '#8B6A10', baixa: '#27875A' }
              const bgs = { alta: '#FDECEA', media: '#FDF4DC', baixa: '#E8F7EE' }
              const active = newPrio === p
              return (
                <button
                  key={p}
                  onClick={() => setNewPrio(p)}
                  className="text-xs px-2.5 py-1 rounded-lg font-medium transition-all"
                  style={active
                    ? { background: colors[p], color: '#fff' }
                    : { background: bgs[p], color: colors[p] }
                  }
                >
                  {p === 'alta' ? 'Alta' : p === 'media' ? 'Média' : 'Baixa'}
                </button>
              )
            })}
            <button
              onClick={() => setShowDateAdd(true)}
              className="text-xs px-2.5 py-1 rounded-lg font-medium transition-all"
              style={newDeadline
                ? { background: '#E6F4F7', color: '#0E8FA3', border: '1px solid #0E8FA3' }
                : { background: '#F1F5F9', color: '#64748B', border: '1px solid transparent' }
              }
            >
              📅 {newDeadline ? newDeadline.split('-').reverse().join('/') : 'Prazo'}
            </button>
            <button
              onClick={handleAdd}
              disabled={saving}
              className="ml-auto text-xs font-semibold px-4 py-1.5 rounded-lg text-white disabled:opacity-60"
              style={{ background: '#0E8FA3' }}
            >
              {saving ? 'Salvando…' : 'Adicionar'}
            </button>
            <button
              onClick={() => { setShowAdd(false); setAddError('') }}
              className="text-xs px-3 py-1.5 rounded-lg font-medium"
              style={{ background: '#F1F5F9', color: '#64748B' }}
            >
              Cancelar
            </button>
          </div>
        </div>
      )}

      {/* Lista */}
      <div className="flex-1 overflow-y-auto px-5 py-4">
        {loading ? (
          <p className="text-center text-sm mt-8" style={{ color: '#94A3B8' }}>Carregando…</p>
        ) : tasks.length === 0 ? (
          <p className="text-center text-sm mt-8" style={{ color: '#94A3B8' }}>Nenhuma tarefa em {tabLabel} 🎉</p>
        ) : (
          <div className="grid grid-cols-1 xl:grid-cols-2 gap-2">
            {tasks.map(t => (
              <TaskCard
                key={t.id}
                task={t}
                onOpen={onOpenTask}
                onStatusChange={handleStatusChange}
              />
            ))}
          </div>
        )}
      </div>

      {showDateAdd && (
        <DatePicker
          value={newDeadline}
          onChange={setNewDeadline}
          onClose={() => setShowDateAdd(false)}
        />
      )}
    </div>
  )
}
