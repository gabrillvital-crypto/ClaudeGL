import { useState } from 'react'
import { fetchDoneRange } from '../lib/firebase'
import { generateReportHTML, isoToday } from '../lib/utils'

function addDays(iso, n) {
  const d = new Date(iso)
  d.setDate(d.getDate() + n)
  return d.toISOString().split('T')[0]
}

function mondayOfWeek(iso) {
  const d = new Date(iso)
  const day = d.getDay() || 7
  d.setDate(d.getDate() - day + 1)
  return d.toISOString().split('T')[0]
}

function firstOfMonth(iso) {
  return iso.slice(0, 7) + '-01'
}

export default function ReportModal({ onClose }) {
  const today = isoToday()
  const [dateFrom, setDateFrom] = useState(mondayOfWeek(today))
  const [dateTo, setDateTo] = useState(today)
  const [tabFilter, setTabFilter] = useState('todas')
  const [loading, setLoading] = useState(false)

  function setWeek() { setDateFrom(mondayOfWeek(today)); setDateTo(today) }
  function set15()   { setDateFrom(addDays(today, -14)); setDateTo(today) }
  function setMonth(){ setDateFrom(firstOfMonth(today)); setDateTo(today) }

  async function generate() {
    setLoading(true)
    const from = dateFrom + 'T00:00:00'
    const to   = dateTo   + 'T23:59:59'
    const tasks = await fetchDoneRange(tabFilter, from, to)
    const html = generateReportHTML(tasks, tabFilter, dateFrom, dateTo)
    const blob = new Blob([html], { type: 'text/html;charset=utf-8' })
    const url = URL.createObjectURL(blob)
    window.open(url, '_blank')
    setLoading(false)
    onClose()
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-sm">
        <div className="px-5 pt-5 pb-2">
          <p className="font-bold text-gray-800 text-base mb-4">ðŸ“Š Gerar RelatÃ³rio</p>

          {/* Atalhos */}
          <p className="text-xs font-bold text-gray-500 uppercase tracking-wide mb-2">Atalhos rÃ¡pidos</p>
          <div className="flex gap-2 mb-4 flex-wrap">
            {[['Esta semana', setWeek], ['Ãšltimos 15 dias', set15], ['Este mÃªs', setMonth]].map(([lbl, fn]) => (
              <button key={lbl} onClick={fn} className="text-xs px-3 py-1.5 rounded-lg font-medium" style={{ background: '#e0f7fa', color: '#14B3CC' }}>
                {lbl}
              </button>
            ))}
          </div>

          {/* Datas */}
          <p className="text-xs font-bold text-gray-500 uppercase tracking-wide mb-2">PerÃ­odo</p>
          <div className="flex gap-3 items-center mb-4">
            <div className="flex-1">
              <label className="text-xs text-gray-400 block mb-1">De</label>
              <input type="date" className="w-full text-sm border border-gray-200 rounded-lg px-2 py-1.5" value={dateFrom} onChange={e => setDateFrom(e.target.value)} />
            </div>
            <div className="flex-1">
              <label className="text-xs text-gray-400 block mb-1">AtÃ©</label>
              <input type="date" className="w-full text-sm border border-gray-200 rounded-lg px-2 py-1.5" value={dateTo} onChange={e => setDateTo(e.target.value)} />
            </div>
          </div>

          {/* Aba */}
          <p className="text-xs font-bold text-gray-500 uppercase tracking-wide mb-2">Aba</p>
          <div className="flex gap-2 mb-5">
            {[['todas', 'Todas'], ['pessoal', 'Pessoal'], ['profissional', 'Profissional']].map(([v, l]) => (
              <button
                key={v}
                onClick={() => setTabFilter(v)}
                className={`text-xs px-3 py-1.5 rounded-full font-medium transition-colors ${tabFilter === v ? 'text-white' : 'bg-gray-100 text-gray-500'}`}
                style={tabFilter === v ? { background: '#14B3CC' } : {}}
              >{l}</button>
            ))}
          </div>
        </div>

        <div className="flex gap-2 px-5 pb-5">
          <button onClick={onClose} className="flex-1 text-sm py-2 rounded-xl bg-gray-100 text-gray-600">
            Cancelar
          </button>
          <button onClick={generate} disabled={loading} className="flex-1 text-sm font-bold py-2 rounded-xl text-white disabled:opacity-40" style={{ background: '#14B3CC' }}>
            {loading ? 'Gerandoâ€¦' : 'Abrir no navegador'}
          </button>
        </div>
      </div>
    </div>
  )
}

