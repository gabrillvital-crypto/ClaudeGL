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
      {/* Header da aba */}
      <div className="flex items-center gap-3 px-4 pt-4 pb-2 flex-wrap">
        <div className="flex gap-1">
          {['todos', 'alta', 'media', 'baixa'].map(p => (
            <button
              key={p}
              onClick={() => setPrio(p)}
              className={`text-xs px-3 py-1 rounded-full font-medium transition-colors ${
                prio === p ? 'text-white' : 'bg-gray-100 text-gray-500'
              }`}
              style={prio === p ? { background: '#0E8FA3' } : {}}
            >
              {p === 'todos' ? 'Todos' : p === 'alta' ? 'Alta' : p === 'media' ? 'Média' : 'Baixa'}
            </button>
          ))}
        </div>
        <button
          onClick={() => setShowDone(v => !v)}
          className={`text-xs px-3 py-1 rounded-full font-medium transition-colors ${showDone ? 'bg-gray-700 text-white' : 'bg-gray-100 text-gray-500'}`}
        >
          {showDone ? 'Ocultar concluídas' : `Concluídas (${done})`}
        </button>
        <div className="flex-1" />
        <button
          onClick={() => setShowAdd(v => !v)}
          className="text-xs font-bold px-3 py-1 rounded-full text-white"
          style={{ background: '#0E8FA3' }}
        >+ Nova tarefa</button>
      </div>

      {/* Formulário de adição */}
      {showAdd && (
        <div className="mx-4 mb-3 p-3 bg-blue-50 rounded-xl border border-blue-200 space-y-2">
          <input
            autoFocus
            className="w-full text-sm border border-gray-200 rounded-lg px-3 py-2"
            placeholder="Título da tarefa…"
            value={newTitle}
            onChange={e => setNewTitle(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && handleAdd()}
          />
          {addError && <p className="text-xs text-red-600">{addError}</p>}
          <div className="flex gap-2 flex-wrap">
            {['alta', 'media', 'baixa'].map(p => (
              <button
                key={p}
                onClick={() => setNewPrio(p)}
                className={`text-xs px-3 py-1 rounded-full font-bold border transition-all ${newPrio === p ? 'text-white border-transparent' : 'bg-white border-gray-200 text-gray-500'}`}
                style={newPrio === p ? { background: p === 'alta' ? '#DC2626' : p === 'media' ? '#D97706' : '#059669' } : {}}
              >
                {p === 'alta' ? 'Alta' : p === 'media' ? 'Média' : 'Baixa'}
              </button>
            ))}
            <button
              onClick={() => setShowDateAdd(true)}
              className="text-xs px-3 py-1 rounded-full border"
              style={newDeadline ? { background: '#e0f7fa', color: '#0E8FA3', borderColor: '#0E8FA3' } : { background: 'white', color: '#6b7280', borderColor: '#e5e7eb' }}
            >
              📅 {newDeadline ? newDeadline.split('-').reverse().join('/') : 'Prazo'}
            </button>
            <button
              onClick={handleAdd}
              disabled={saving}
              className="ml-auto text-xs font-bold px-4 py-1 rounded-full text-white disabled:opacity-60"
              style={{ background: '#0E8FA3' }}
            >
              {saving ? 'Salvando…' : 'Adicionar'}
            </button>
            <button onClick={() => { setShowAdd(false); setAddError('') }} className="text-xs px-3 py-1 rounded-full bg-gray-100 text-gray-500">
              Cancelar
            </button>
          </div>
        </div>
      )}

      {/* Lista */}
      <div className="flex-1 overflow-y-auto px-4 pb-4">
        {loading ? (
          <p className="text-center text-gray-400 mt-8 text-sm">Carregando…</p>
        ) : tasks.length === 0 ? (
          <p className="text-center text-gray-400 mt-8 text-sm">Nenhuma tarefa em {tabLabel} 🎉</p>
        ) : (
          tasks.map(t => (
            <TaskCard
              key={t.id}
              task={t}
              onOpen={onOpenTask}
              onStatusChange={handleStatusChange}
            />
          ))
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
