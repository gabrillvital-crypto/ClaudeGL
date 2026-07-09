import { PRIORITY, fmtDate, deadlineStatus } from '../lib/utils'

export default function TaskCard({ task, onOpen, onStatusChange }) {
  const p = PRIORITY[task.priority] || PRIORITY.media
  const dl = deadlineStatus(task.deadline)
  const ck = task._checklist || []
  const ckDone = ck.filter(i => i.is_done).length

  const dlBadge = dl === 'overdue'
    ? 'bg-red-100 text-red-700'
    : dl === 'today'
    ? 'bg-orange-100 text-orange-700'
    : 'bg-gray-100 text-gray-500'

  const isIP = task.status === 'in_progress'

  function handleContext(e) {
    e.preventDefault()
    const menu = [
      isIP
        ? { label: '↩ Voltar para pendente', status: 'pending' }
        : { label: '▶ Marcar em andamento', status: 'in_progress' },
      { label: '✓ Concluir', status: 'done' },
    ]
    showContextMenu(e.clientX, e.clientY, menu, (s) => onStatusChange(task.id, s))
  }

  return (
    <div
      onClick={() => onOpen(task.id)}
      onContextMenu={handleContext}
      className={`bg-white rounded-xl p-4 mb-2 cursor-pointer border-l-4 shadow-sm hover:shadow-md transition-shadow select-none ${
        isIP ? 'border-amber-500' : 'border-gray-200'
      }`}
    >
      <div className="flex items-start gap-3">
        {/* Prioridade pill */}
        <span
          className="mt-0.5 shrink-0 text-xs font-bold px-2 py-0.5 rounded-full text-white"
          style={{ backgroundColor: p.color }}
        >
          {p.label}
        </span>

        <div className="flex-1 min-w-0">
          <p className={`text-sm font-semibold text-gray-800 truncate ${isIP ? 'text-amber-700' : ''}`}>
            {isIP && <span className="mr-1">▶</span>}
            {task.title}
          </p>

          {task.notes && (
            <p className="text-xs text-gray-400 mt-0.5 truncate">{task.notes}</p>
          )}

          <div className="flex items-center gap-2 mt-1.5 flex-wrap">
            {/* Deadline badge */}
            {task.deadline && (
              <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${dlBadge}`}>
                📅 {fmtDate(task.deadline)}
              </span>
            )}

            {/* Checklist badge */}
            {ck.length > 0 && (
              <span className="text-xs text-gray-400">
                ☑ {ckDone}/{ck.length}
              </span>
            )}

            {/* Cliente badge */}
            {task.clients?.name && (
              <span className="text-xs bg-blue-50 text-blue-600 px-2 py-0.5 rounded-full truncate max-w-[120px]">
                {task.clients.name}
              </span>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

// ── Context menu imperativo (simples, sem dependência) ────────────────────────

function showContextMenu(x, y, items, onSelect) {
  const existing = document.getElementById('ctx-menu')
  if (existing) existing.remove()

  const menu = document.createElement('div')
  menu.id = 'ctx-menu'
  menu.style.cssText = `position:fixed;top:${y}px;left:${x}px;z-index:9999;background:white;border:1px solid #e5e7eb;border-radius:8px;box-shadow:0 4px 20px rgba(0,0,0,.15);min-width:200px;overflow:hidden`

  items.forEach(item => {
    const btn = document.createElement('button')
    btn.textContent = item.label
    btn.style.cssText = 'display:block;width:100%;text-align:left;padding:10px 16px;font-size:13px;background:none;border:none;cursor:pointer;color:#374151'
    btn.onmouseenter = () => btn.style.background = '#f3f4f6'
    btn.onmouseleave = () => btn.style.background = 'none'
    btn.onclick = () => { onSelect(item.status); menu.remove() }
    menu.appendChild(btn)
  })

  document.body.appendChild(menu)
  setTimeout(() => document.addEventListener('click', () => menu.remove(), { once: true }), 0)
}
