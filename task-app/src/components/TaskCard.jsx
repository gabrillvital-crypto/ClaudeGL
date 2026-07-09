import { PRIORITY, IN_PROGRESS_COLOR, fmtDate, deadlineStatus } from '../lib/utils'

export default function TaskCard({ task, onOpen, onStatusChange }) {
  const p = PRIORITY[task.priority] || PRIORITY.media
  const dl = deadlineStatus(task.deadline)
  const ck = task._checklist || []
  const ckDone = ck.filter(i => i.is_done).length
  const isIP = task.status === 'in_progress'

  const dotColor = isIP ? IN_PROGRESS_COLOR : p.color

  const dlStyle = dl === 'overdue'
    ? { background: '#FEE2E2', color: '#B91C1C' }
    : dl === 'today'
    ? { background: '#FEF9C3', color: '#854D0E' }
    : { background: '#F1F5F9', color: '#64748B' }

  function handleContext(e) {
    e.preventDefault()
    const menu = [
      isIP
        ? { label: '↩ Voltar para pendente', status: 'pending' }
        : { label: '▶ Marcar em andamento', status: 'in_progress' },
      { label: '✓ Concluir', status: 'done' },
    ]
    showContextMenu(e.clientX, e.clientY, menu, s => onStatusChange(task.id, s))
  }

  return (
    <div
      onClick={() => onOpen(task.id)}
      onContextMenu={handleContext}
      className="bg-white rounded-xl p-4 cursor-pointer transition-all select-none hover:shadow-md"
      style={{ border: '1px solid #E8EEF4' }}
    >
      {/* Linha título */}
      <div className="flex items-start gap-2.5">
        <span
          className="mt-[5px] w-2 h-2 rounded-full shrink-0"
          style={{ backgroundColor: dotColor }}
        />
        <p className="text-sm font-medium leading-snug flex-1 min-w-0" style={{ color: isIP ? IN_PROGRESS_COLOR : '#1E293B' }}>
          {isIP && <span className="mr-1 text-xs">▶</span>}
          {task.title}
        </p>
      </div>

      {/* Linha de badges */}
      <div className="flex items-center gap-1.5 flex-wrap mt-2.5 ml-[18px]">
        <span
          className="text-xs font-medium px-1.5 py-0.5 rounded"
          style={{ backgroundColor: p.bg, color: p.color }}
        >
          {p.label}
        </span>

        {task.deadline && (
          <span className="text-xs font-medium px-1.5 py-0.5 rounded" style={dlStyle}>
            📅 {fmtDate(task.deadline)}
          </span>
        )}

        {ck.length > 0 && (
          <span className="text-xs" style={{ color: '#94A3B8' }}>
            ☑ {ckDone}/{ck.length}
          </span>
        )}

        {task.clients?.name && (
          <span
            className="text-xs px-1.5 py-0.5 rounded truncate max-w-[130px]"
            style={{ background: '#EFF6FF', color: '#3B82F6' }}
          >
            {task.clients.name}
          </span>
        )}
      </div>

      {task.notes && (
        <p className="text-xs mt-2 ml-[18px] truncate" style={{ color: '#94A3B8' }}>{task.notes}</p>
      )}
    </div>
  )
}

// ── Context menu ──────────────────────────────────────────────────────────────

function showContextMenu(x, y, items, onSelect) {
  const existing = document.getElementById('ctx-menu')
  if (existing) existing.remove()

  const menu = document.createElement('div')
  menu.id = 'ctx-menu'
  menu.style.cssText = [
    `position:fixed`, `top:${y}px`, `left:${x}px`, `z-index:9999`,
    `background:#fff`, `border:1px solid #E8EEF4`, `border-radius:10px`,
    `box-shadow:0 8px 30px rgba(0,0,0,.12)`, `min-width:210px`, `overflow:hidden`,
    `padding:4px`,
  ].join(';')

  items.forEach(item => {
    const btn = document.createElement('button')
    btn.textContent = item.label
    btn.style.cssText = 'display:block;width:100%;text-align:left;padding:8px 12px;font-size:13px;background:none;border:none;cursor:pointer;color:#374151;border-radius:6px'
    btn.onmouseenter = () => { btn.style.background = '#F8FAFC'; btn.style.color = '#111827' }
    btn.onmouseleave = () => { btn.style.background = 'none'; btn.style.color = '#374151' }
    btn.onclick = () => { onSelect(item.status); menu.remove() }
    menu.appendChild(btn)
  })

  document.body.appendChild(menu)
  setTimeout(() => document.addEventListener('click', () => menu.remove(), { once: true }), 0)
}
