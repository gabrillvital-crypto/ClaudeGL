import { useState } from 'react'
import { PRIORITY, fmtDate } from '../lib/utils'
import DatePicker from './DatePicker'

const PRIO_LABELS = { alta: 'Alta', media: 'Média', baixa: 'Baixa' }

export default function ReviewModal({ tasks, onConfirm, onClose }) {
  const [rows, setRows] = useState(() =>
    tasks.map(t => ({ ...t, checked: true, deadline: null }))
  )
  const [showDateFor, setShowDateFor] = useState(null)

  function toggle(i) {
    setRows(r => r.map((row, j) => j === i ? { ...row, checked: !row.checked } : row))
  }

  function setTitle(i, v) {
    setRows(r => r.map((row, j) => j === i ? { ...row, title: v } : row))
  }

  function setPrio(i, v) {
    setRows(r => r.map((row, j) => j === i ? { ...row, priority: v } : row))
  }

  function setDeadline(i, v) {
    setRows(r => r.map((row, j) => j === i ? { ...row, deadline: v } : row))
    setShowDateFor(null)
  }

  const selected = rows.filter(r => r.checked && r.title.trim())

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-2xl max-h-[85vh] flex flex-col overflow-hidden">

        {/* Header */}
        <div className="px-5 py-4 text-white" style={{ background: '#14B3CC' }}>
          <p className="font-bold text-base">✨ {tasks.length} tarefa{tasks.length !== 1 ? 's' : ''} identificada{tasks.length !== 1 ? 's' : ''}</p>
          <p className="text-sm opacity-80">Ajuste e confirme antes de salvar.</p>
        </div>

        {/* List */}
        <div className="overflow-y-auto flex-1 px-4 py-3 space-y-2">
          {rows.map((row, i) => (
            <div key={i} className="bg-gray-50 rounded-xl border border-gray-200 p-3">
              <div className="flex items-center gap-2">
                <input
                  type="checkbox"
                  checked={row.checked}
                  onChange={() => toggle(i)}
                  className="w-4 h-4 accent-teal-600 shrink-0"
                />
                <input
                  className="flex-1 text-sm border border-gray-200 rounded-lg px-2 py-1.5 bg-white"
                  value={row.title}
                  onChange={e => setTitle(i, e.target.value)}
                />
                <select
                  className="text-xs border border-gray-200 rounded-lg px-2 py-1.5 bg-white"
                  value={row.priority}
                  onChange={e => setPrio(i, e.target.value)}
                >
                  {['alta', 'media', 'baixa'].map(p => (
                    <option key={p} value={p}>{PRIO_LABELS[p]}</option>
                  ))}
                </select>
                <span className={`text-xs px-2 py-1 rounded-full font-bold ${row.tab === 'profissional' ? 'bg-blue-100 text-blue-700' : 'bg-pink-100 text-pink-700'}`}>
                  {row.tab === 'profissional' ? 'Prof.' : 'Pessoal'}
                </span>
                <button
                  onClick={() => setShowDateFor(showDateFor === i ? null : i)}
                  className="text-xs px-2 py-1 rounded-lg border"
                  style={row.deadline
                    ? { background: '#e0f7fa', color: '#14B3CC', borderColor: '#14B3CC' }
                    : { background: '#f3f4f6', color: '#6b7280', borderColor: '#e5e7eb' }
                  }
                >
                  📅 {row.deadline ? fmtDate(row.deadline) : 'Prazo'}
                </button>
              </div>
              {row.notes && (
                <p className="text-xs text-gray-400 mt-1.5 ml-6">{row.notes}</p>
              )}
            </div>
          ))}
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between px-5 py-3 border-t bg-white">
          <span className="text-xs text-gray-400">
            {selected.length} de {rows.length} selecionada{selected.length !== 1 ? 's' : ''}
          </span>
          <div className="flex gap-2">
            <button onClick={onClose} className="text-sm px-4 py-2 rounded-lg bg-gray-100 text-gray-600">
              Cancelar
            </button>
            <button
              onClick={() => { onConfirm(selected); onClose() }}
              disabled={!selected.length}
              className="text-sm font-bold px-5 py-2 rounded-lg text-white disabled:opacity-40"
              style={{ background: '#14B3CC' }}
            >
              Salvar tarefas ✓
            </button>
          </div>
        </div>
      </div>

      {showDateFor !== null && (
        <DatePicker
          value={rows[showDateFor].deadline}
          onChange={v => setDeadline(showDateFor, v)}
          onClose={() => setShowDateFor(null)}
        />
      )}
    </div>
  )
}
