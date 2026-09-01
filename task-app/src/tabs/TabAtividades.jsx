import { useState, useEffect } from 'react'
import { fetchTasksDone, setTaskStatus } from '../lib/firebase'
import { PRIORITY, fmtDateTime } from '../lib/utils'

export default function TabAtividades({ refresh }) {
  const [tasks, setTasks] = useState([])
  const [prio, setPrio] = useState('todos')
  const [loading, setLoading] = useState(true)

  async function load() {
    const data = await fetchTasksDone(prio)
    setTasks(data)
    setLoading(false)
  }

  useEffect(() => { load() }, [prio, refresh])

  async function reactivate(id) {
    await setTaskStatus(id, 'pending')
    load()
  }

  return (
    <div className="flex flex-col h-full">
      {/* Filtro */}
      <div className="flex gap-1 px-4 pt-4 pb-2 flex-wrap">
        {['todos', 'alta', 'media', 'baixa'].map(p => (
          <button
            key={p}
            onClick={() => setPrio(p)}
            className={`text-xs px-3 py-1 rounded-full font-medium transition-colors ${prio === p ? 'text-white' : 'bg-gray-100 text-gray-500'}`}
            style={prio === p ? { background: '#059669' } : {}}
          >
            {p === 'todos' ? 'Todos' : p === 'alta' ? 'Alta' : p === 'media' ? 'MÃ©dia' : 'Baixa'}
          </button>
        ))}
        <span className="ml-auto text-xs text-gray-400 py-1">{tasks.length} concluÃ­da{tasks.length !== 1 ? 's' : ''}</span>
      </div>

      <div className="flex-1 overflow-y-auto px-4 pb-4">
        {loading ? (
          <p className="text-center text-gray-400 mt-8 text-sm">Carregandoâ€¦</p>
        ) : tasks.length === 0 ? (
          <p className="text-center text-gray-400 mt-8 text-sm">Nenhuma tarefa concluÃ­da</p>
        ) : (
          tasks.map(t => {
            const p = PRIORITY[t.priority] || PRIORITY.media
            const tabBadge = t.tab === 'profissional' ? 'bg-blue-50 text-blue-600' : 'bg-pink-50 text-pink-600'
            return (
              <div key={t.id} className="bg-green-50 border border-green-200 rounded-xl p-3 mb-2">
                <div className="flex items-start gap-2">
                  <span className="text-green-600 font-bold text-lg mt-0.5">âœ“</span>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-semibold text-gray-700 line-through truncate">{t.title}</p>
                    <div className="flex gap-2 mt-1 flex-wrap items-center">
                      <span className="text-xs font-bold px-2 py-0.5 rounded-full text-white" style={{ background: p.color }}>{p.label}</span>
                      <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${tabBadge}`}>
                        {t.tab === 'profissional' ? 'Profissional' : 'Pessoal'}
                      </span>
                      {t.completed_at && (
                        <span className="text-xs text-gray-400">{fmtDateTime(t.completed_at)}</span>
                      )}
                    </div>
                  </div>
                  <button
                    onClick={() => reactivate(t.id)}
                    className="shrink-0 text-xs px-2 py-1 rounded-lg bg-white border border-gray-200 text-gray-500 hover:bg-gray-50"
                  >â†© Reativar</button>
                </div>
              </div>
            )
          })
        )}
      </div>
    </div>
  )
}

