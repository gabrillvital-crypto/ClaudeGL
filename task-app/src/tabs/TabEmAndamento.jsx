import { useState, useEffect } from 'react'
import { fetchTasksInProgress, setTaskStatus } from '../lib/supabase'
import TaskCard from '../components/TaskCard'

export default function TabEmAndamento({ onOpenTask, refresh }) {
  const [tasks, setTasks] = useState([])
  const [loading, setLoading] = useState(true)

  async function load() {
    const data = await fetchTasksInProgress()
    setTasks(data)
    setLoading(false)
  }

  useEffect(() => { load() }, [refresh])

  async function handleStatusChange(id, status) {
    await setTaskStatus(id, status)
    load()
  }

  return (
    <div className="px-4 pb-4 pt-3 overflow-y-auto h-full">
      {loading ? (
        <p className="text-center text-gray-400 mt-8 text-sm">Carregando…</p>
      ) : tasks.length === 0 ? (
        <p className="text-center text-gray-400 mt-12 text-sm">Nenhuma tarefa em andamento</p>
      ) : (
        <>
          <div className="flex items-center gap-2 mb-3">
            <span className="text-xs font-bold text-amber-600 uppercase tracking-wide">▶ Em andamento</span>
            <span className="text-xs bg-amber-100 text-amber-700 px-2 py-0.5 rounded-full font-bold">{tasks.length}</span>
          </div>
          {tasks.map(t => (
            <TaskCard key={t.id} task={t} onOpen={onOpenTask} onStatusChange={handleStatusChange} />
          ))}
        </>
      )}
    </div>
  )
}
