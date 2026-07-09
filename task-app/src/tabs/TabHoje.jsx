import { useState, useEffect } from 'react'
import { fetchTasksToday, fetchTasksOverdue, setTaskStatus } from '../lib/supabase'
import TaskCard from '../components/TaskCard'

export default function TabHoje({ onOpenTask, refresh }) {
  const [today, setToday] = useState([])
  const [overdue, setOverdue] = useState([])
  const [loading, setLoading] = useState(true)

  async function load() {
    const [t, o] = await Promise.all([fetchTasksToday(), fetchTasksOverdue()])
    setToday(t)
    setOverdue(o)
    setLoading(false)
  }

  useEffect(() => { load() }, [refresh])

  async function handleStatusChange(id, status) {
    await setTaskStatus(id, status)
    load()
  }

  if (loading) return <p className="text-center text-gray-400 mt-8 text-sm">Carregando…</p>

  const empty = !today.length && !overdue.length

  return (
    <div className="px-4 pb-4 pt-3 overflow-y-auto h-full">
      {empty && (
        <p className="text-center text-gray-400 mt-12 text-sm">Nenhuma tarefa para hoje 🎉</p>
      )}

      {overdue.length > 0 && (
        <>
          <div className="flex items-center gap-2 mb-2">
            <span className="text-xs font-bold text-red-500 uppercase tracking-wide">⚠ Atrasadas</span>
            <span className="text-xs bg-red-100 text-red-600 px-2 py-0.5 rounded-full font-bold">{overdue.length}</span>
          </div>
          {overdue.map(t => (
            <TaskCard key={t.id} task={t} onOpen={onOpenTask} onStatusChange={handleStatusChange} />
          ))}
        </>
      )}

      {today.length > 0 && (
        <>
          <div className={`flex items-center gap-2 mb-2 ${overdue.length ? 'mt-4' : ''}`}>
            <span className="text-xs font-bold text-orange-500 uppercase tracking-wide">📅 Vencem hoje</span>
            <span className="text-xs bg-orange-100 text-orange-600 px-2 py-0.5 rounded-full font-bold">{today.length}</span>
          </div>
          {today.map(t => (
            <TaskCard key={t.id} task={t} onOpen={onOpenTask} onStatusChange={handleStatusChange} />
          ))}
        </>
      )}
    </div>
  )
}
