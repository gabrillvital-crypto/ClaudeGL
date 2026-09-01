import { useState, useEffect, useRef } from 'react'
import {
  getTask, updateTask, deleteTask, setTaskStatus,
  fetchChecklist, addChecklistItem, toggleChecklistItem, deleteChecklistItem,
  fetchClients,
} from '../lib/firebase'
import { PRIORITY, IN_PROGRESS_COLOR, fmtDate } from '../lib/utils'
import DatePicker from './DatePicker'

export default function TaskDetailModal({ taskId, onClose, onSaved, onDeleted }) {
  const [task, setTask] = useState(null)
  const [checklist, setChecklist] = useState([])
  const [clients, setClients] = useState([])
  const [showDatePicker, setShowDatePicker] = useState(false)
  const [newItem, setNewItem] = useState('')
  const [recording, setRecording] = useState(false)
  const [saving, setSaving] = useState(false)
  const [toast, setToast] = useState('')
  const recRef = useRef(null)

  useEffect(() => {
    load()
    fetchClients().then(setClients).catch(() => {})
  }, [taskId])

  async function load() {
    const [t, ck] = await Promise.all([getTask(taskId), fetchChecklist(taskId)])
    setTask(t)
    setChecklist(ck)
  }

  function setField(f, v) { setTask(t => ({ ...t, [f]: v })) }

  async function save() {
    setSaving(true)
    await updateTask(taskId, {
      title: task.title,
      description: task.description,
      notes: task.notes,
      priority: task.priority,
      deadline: task.deadline || null,
      client_id: task.client_id || null,
    })
    setSaving(false)
    showToast('âœ“ Salvo')
    onSaved?.()
  }

  async function handleComplete() {
    await setTaskStatus(taskId, 'done')
    onSaved?.()
    onClose()
  }

  async function handleDelete() {
    if (!confirm('Excluir esta tarefa?')) return
    await deleteTask(taskId)
    onDeleted?.()
    onClose()
  }

  async function handleToggleAndamento() {
    const next = task.status === 'in_progress' ? 'pending' : 'in_progress'
    await setTaskStatus(taskId, next)
    setField('status', next)
    onSaved?.()
  }

  async function addItem() {
    const text = newItem.trim()
    if (!text) return
    const item = await addChecklistItem(taskId, text)
    setChecklist(c => [...c, item])
    setNewItem('')
  }

  async function toggleItem(id, done) {
    await toggleChecklistItem(id, done)
    setChecklist(c => c.map(i => i.id === id ? { ...i, is_done: done } : i))
  }

  async function removeItem(id) {
    await deleteChecklistItem(id)
    setChecklist(c => c.filter(i => i.id !== id))
  }

  function showToast(msg) {
    setToast(msg)
    setTimeout(() => setToast(''), 2000)
  }

  function startVoice() {
    const SR = window.SpeechRecognition || window.webkitSpeechRecognition
    if (!SR) { alert('Voz nÃ£o suportada neste navegador. Use Chrome ou Edge.'); return }
    const rec = new SR()
    rec.lang = 'pt-BR'
    rec.continuous = true
    rec.interimResults = true
    rec.onresult = e => {
      let final = ''
      for (const r of e.results) {
        if (r.isFinal) final += r[0].transcript + ' '
      }
      if (final) setField('description', t => (t.description || '') + final)
    }
    rec.onend = () => setRecording(false)
    rec.start()
    recRef.current = rec
    setRecording(true)
  }

  function stopVoice() {
    recRef.current?.stop()
    setRecording(false)
  }

  if (!task) return (
    <div className="fixed inset-0 z-40 flex items-center justify-center bg-black/30">
      <div className="bg-white rounded-2xl p-8 text-gray-400">Carregandoâ€¦</div>
    </div>
  )

  const isIP = task.status === 'in_progress'

  return (
    <div className="fixed inset-0 z-40 flex items-end sm:items-center justify-center bg-black/40">
      <div className="bg-white rounded-t-3xl sm:rounded-2xl w-full sm:max-w-3xl sm:mx-6 max-h-[95vh] flex flex-col shadow-2xl">

        {/* Action bar */}
        <div className="flex items-center gap-2 px-4 py-3 rounded-t-3xl sm:rounded-t-2xl" style={{ background: '#14B3CC' }}>
          <button
            onClick={handleDelete}
            className="bg-red-600 hover:bg-red-700 text-white text-xs font-bold px-3 py-2 rounded-lg"
          >ðŸ—‘ Excluir</button>
          <div className="flex-1" />
          <button onClick={onClose} className="text-white/80 hover:text-white text-xs px-3 py-2 rounded-lg border border-white/30">
            Cancelar
          </button>
          <button onClick={save} disabled={saving} className="bg-white text-sm font-bold px-4 py-2 rounded-lg" style={{ color: '#14B3CC' }}>
            {saving ? 'â€¦' : 'Salvar'}
          </button>
          <button
            onClick={handleToggleAndamento}
            className="text-xs font-bold px-3 py-2 rounded-lg text-white"
            style={{ background: isIP ? 'rgba(255,255,255,0.2)' : IN_PROGRESS_COLOR }}
          >
            {isIP ? 'â†© Voltar' : 'â–¶ Andamento'}
          </button>
          <button onClick={handleComplete} className="bg-green-600 hover:bg-green-700 text-white text-xs font-bold px-3 py-2 rounded-lg">
            Concluir âœ“
          </button>
        </div>

        {/* Scrollable body */}
        <div className="overflow-y-auto flex-1 px-5 py-4 space-y-4">

          {/* TÃ­tulo */}
          <div>
            <label className="text-xs font-bold text-gray-500 uppercase tracking-wide">TÃ­tulo</label>
            <input
              className="w-full mt-1 text-sm border border-gray-200 rounded-lg px-3 py-2 focus:outline-none focus:ring-2"
              style={{ '--tw-ring-color': '#14B3CC' }}
              value={task.title}
              onChange={e => setField('title', e.target.value)}
            />
          </div>

          {/* Prioridade */}
          <div>
            <label className="text-xs font-bold text-gray-500 uppercase tracking-wide">Prioridade</label>
            <div className="flex gap-2 mt-1">
              {['alta', 'media', 'baixa'].map(p => {
                const pr = PRIORITY[p]
                const active = task.priority === p
                return (
                  <button
                    key={p}
                    onClick={() => setField('priority', p)}
                    className="text-xs font-bold px-4 py-2 rounded-lg border-2 transition-all"
                    style={active
                      ? { background: pr.color, color: '#fff', borderColor: pr.color }
                      : { background: pr.bg, color: pr.color, borderColor: pr.bg }
                    }
                  >{pr.label}</button>
                )
              })}
            </div>
          </div>

          {/* Prazo + Cliente */}
          <div className="flex gap-3 flex-wrap">
            <div>
              <label className="text-xs font-bold text-gray-500 uppercase tracking-wide block mb-1">Prazo</label>
              <button
                onClick={() => setShowDatePicker(true)}
                className="text-xs px-3 py-2 rounded-lg border"
                style={task.deadline
                  ? { background: '#e0f7fa', color: '#14B3CC', borderColor: '#14B3CC' }
                  : { background: '#f3f4f6', color: '#6b7280', borderColor: '#e5e7eb' }
                }
              >
                ðŸ“… {task.deadline ? fmtDate(task.deadline) : 'Selecionar data'}
              </button>
            </div>

            <div className="flex-1 min-w-[160px]">
              <label className="text-xs font-bold text-gray-500 uppercase tracking-wide block mb-1">Cliente</label>
              <select
                className="w-full text-xs border border-gray-200 rounded-lg px-2 py-2 bg-white"
                value={task.client_id || ''}
                onChange={e => setField('client_id', e.target.value ? Number(e.target.value) : null)}
              >
                <option value="">â€” Sem cliente â€”</option>
                {clients.map(c => (
                  <option key={c.id} value={c.id}>{c.name} ({c.tier})</option>
                ))}
              </select>
            </div>
          </div>

          {/* DescriÃ§Ã£o / Notas */}
          <div>
            <div className="flex items-center gap-2 mb-1">
              <label className="text-xs font-bold text-gray-500 uppercase tracking-wide">DescriÃ§Ã£o / Notas</label>
              <button
                onClick={recording ? stopVoice : startVoice}
                className={`text-xs px-2 py-1 rounded-lg font-bold transition-colors ${recording ? 'bg-red-100 text-red-600 animate-pulse' : 'bg-gray-100 text-gray-500 hover:bg-gray-200'}`}
              >
                {recording ? 'â¹ Parar' : 'ðŸŽ¤ Voz'}
              </button>
              {toast && <span className="text-xs text-green-600 font-medium">{toast}</span>}
            </div>
            <textarea
              className="w-full text-sm border border-gray-200 rounded-lg px-3 py-2 resize-none focus:outline-none focus:ring-2 min-h-[80px]"
              value={task.description || ''}
              onChange={e => setField('description', e.target.value)}
              placeholder="Contexto, links, referÃªnciasâ€¦"
            />
            <button
              onClick={save}
              className="mt-1 text-xs font-bold px-3 py-1 rounded-lg"
              style={{ background: '#e0f7fa', color: '#14B3CC' }}
            >âœ“ Salvar nota</button>
          </div>

          {/* Notas curtas */}
          <div>
            <label className="text-xs font-bold text-gray-500 uppercase tracking-wide">Notas rÃ¡pidas</label>
            <input
              className="w-full mt-1 text-sm border border-gray-200 rounded-lg px-3 py-2 focus:outline-none"
              value={task.notes || ''}
              onChange={e => setField('notes', e.target.value)}
              placeholder="Cliente, horÃ¡rio, contextoâ€¦"
            />
          </div>

          {/* Checklist */}
          <div>
            <label className="text-xs font-bold text-gray-500 uppercase tracking-wide">Checklist</label>
            <div className="mt-2 space-y-1">
              {checklist.map(item => (
                <div key={item.id} className="flex items-center gap-2 group">
                  <input
                    type="checkbox"
                    checked={item.is_done}
                    onChange={e => toggleItem(item.id, e.target.checked)}
                    className="w-4 h-4 accent-teal-600 cursor-pointer"
                  />
                  <span className={`flex-1 text-sm ${item.is_done ? 'line-through text-gray-400' : 'text-gray-700'}`}>
                    {item.text}
                  </span>
                  <button
                    onClick={() => removeItem(item.id)}
                    className="opacity-0 group-hover:opacity-100 text-gray-300 hover:text-red-400 text-xs transition-opacity"
                  >âœ•</button>
                </div>
              ))}
            </div>
            <div className="flex gap-2 mt-2">
              <input
                className="flex-1 text-sm border border-gray-200 rounded-lg px-3 py-1.5 focus:outline-none"
                placeholder="Novo itemâ€¦"
                value={newItem}
                onChange={e => setNewItem(e.target.value)}
                onKeyDown={e => e.key === 'Enter' && addItem()}
              />
              <button
                onClick={addItem}
                className="text-xs font-bold px-3 py-1.5 rounded-lg text-white"
                style={{ background: '#14B3CC' }}
              >+ Add</button>
            </div>
          </div>

          <div className="h-2" />
        </div>
      </div>

      {showDatePicker && (
        <DatePicker
          value={task.deadline}
          onChange={v => setField('deadline', v)}
          onClose={() => setShowDatePicker(false)}
        />
      )}
    </div>
  )
}

