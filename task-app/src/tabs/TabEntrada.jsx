import { useState, useRef } from 'react'
import { extractTasks, refineText } from '../lib/claude'
import { addTask } from '../lib/supabase'
import ReviewModal from '../components/ReviewModal'

export default function TabEntrada({ onSaved }) {
  const [text, setText] = useState('')
  const [defaultTab, setDefaultTab] = useState('profissional')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [extracted, setExtracted] = useState(null)
  const [recording, setRecording] = useState(false)
  const recRef = useRef(null)

  async function handleExtract() {
    if (!text.trim()) return
    setLoading(true)
    setError('')
    try {
      const tasks = await extractTasks(text, defaultTab)
      if (!tasks.length) {
        setError('Nenhuma tarefa identificada no texto.')
      } else {
        setExtracted(tasks)
      }
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  async function handleRefine() {
    if (!text.trim()) return
    setLoading(true)
    setError('')
    try {
      const refined = await refineText(text)
      setText(refined)
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  async function handleConfirm(tasks) {
    for (const t of tasks) {
      await addTask({
        tab: t.tab || defaultTab,
        title: t.title,
        notes: t.notes || '',
        priority: t.priority || 'media',
        deadline: t.deadline || null,
      })
    }
    setText('')
    setExtracted(null)
    onSaved?.()
  }

  function startVoice() {
    const SR = window.SpeechRecognition || window.webkitSpeechRecognition
    if (!SR) { setError('Voz não suportada neste navegador. Use Chrome ou Edge.'); return }
    const rec = new SR()
    rec.lang = 'pt-BR'
    rec.continuous = true
    rec.interimResults = true
    rec.onresult = e => {
      let final = ''
      for (const r of e.results) {
        if (r.isFinal) final += r[0].transcript + ' '
      }
      if (final) setText(t => t + final)
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

  return (
    <div className="flex flex-col h-full px-4 py-4 gap-3">
      {/* Header */}
      <div>
        <p className="text-sm font-bold text-gray-700 mb-1">Smart Ingestion</p>
        <p className="text-xs text-gray-400">Cole texto de reuniões, WhatsApp ou fale — a IA extrai as tarefas automaticamente.</p>
      </div>

      {/* Seletor de destino */}
      <div className="flex items-center gap-2">
        <span className="text-xs text-gray-500 font-medium">Destino padrão:</span>
        <button
          onClick={() => setDefaultTab('profissional')}
          className={`text-xs px-3 py-1 rounded-full font-bold transition-colors ${defaultTab === 'profissional' ? 'bg-blue-600 text-white' : 'bg-blue-50 text-blue-600'}`}
        >Profissional</button>
        <button
          onClick={() => setDefaultTab('pessoal')}
          className={`text-xs px-3 py-1 rounded-full font-bold transition-colors ${defaultTab === 'pessoal' ? 'bg-pink-600 text-white' : 'bg-pink-50 text-pink-600'}`}
        >Pessoal</button>
      </div>

      {/* Área de texto */}
      <div className="flex-1 flex flex-col gap-2">
        <textarea
          className="flex-1 min-h-[180px] text-sm border border-gray-200 rounded-xl px-4 py-3 resize-none focus:outline-none focus:ring-2 focus:ring-teal-DEFAULT"
          placeholder="Cole texto aqui ou use o microfone…"
          value={text}
          onChange={e => setText(e.target.value)}
        />

        {error && (
          <p className="text-xs text-red-500 px-1">{error}</p>
        )}

        {/* Ações */}
        <div className="flex gap-2 flex-wrap">
          <button
            onClick={recording ? stopVoice : startVoice}
            className={`text-xs font-bold px-4 py-2 rounded-xl transition-colors ${recording ? 'bg-red-100 text-red-600 animate-pulse' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'}`}
          >
            {recording ? '⏹ Parar gravação' : '🎤 Gravar voz'}
          </button>

          <button
            onClick={handleRefine}
            disabled={loading || !text.trim()}
            className="text-xs font-bold px-4 py-2 rounded-xl bg-purple-50 text-purple-600 hover:bg-purple-100 disabled:opacity-40"
          >
            ✨ Aprimorar texto
          </button>

          <button
            onClick={handleExtract}
            disabled={loading || !text.trim()}
            className="ml-auto text-sm font-bold px-6 py-2 rounded-xl text-white disabled:opacity-40"
            style={{ background: '#0E8FA3' }}
          >
            {loading ? 'Extraindo…' : '→ Extrair tarefas'}
          </button>
        </div>
      </div>

      {extracted && (
        <ReviewModal
          tasks={extracted}
          onConfirm={handleConfirm}
          onClose={() => setExtracted(null)}
        />
      )}
    </div>
  )
}
