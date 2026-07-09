import { useState } from 'react'

const MONTHS = ['Janeiro','Fevereiro','Março','Abril','Maio','Junho',
                 'Julho','Agosto','Setembro','Outubro','Novembro','Dezembro']
const DAYS = ['Seg','Ter','Qua','Qui','Sex','Sáb','Dom']

export default function DatePicker({ value, onChange, onClose }) {
  const today = new Date()
  const initial = value ? new Date(value + 'T12:00:00') : today

  const [year, setYear] = useState(initial.getFullYear())
  const [month, setMonth] = useState(initial.getMonth())

  const todayStr = today.toISOString().split('T')[0]

  function daysInMonth(y, m) {
    return new Date(y, m + 1, 0).getDate()
  }

  function firstDayOfWeek(y, m) {
    const d = new Date(y, m, 1).getDay()
    return d === 0 ? 6 : d - 1
  }

  function prevMonth() {
    if (month === 0) { setMonth(11); setYear(y => y - 1) }
    else setMonth(m => m - 1)
  }

  function nextMonth() {
    if (month === 11) { setMonth(0); setYear(y => y + 1) }
    else setMonth(m => m + 1)
  }

  function pick(day) {
    const iso = `${year}-${String(month + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`
    onChange(iso)
    onClose()
  }

  const total = daysInMonth(year, month)
  const offset = firstDayOfWeek(year, month)
  const cells = Array(offset).fill(null).concat(Array.from({ length: total }, (_, i) => i + 1))
  while (cells.length % 7 !== 0) cells.push(null)

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/30"
      onClick={onClose}
    >
      <div
        className="bg-white rounded-2xl shadow-2xl overflow-hidden w-80"
        onClick={e => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-center justify-between px-4 py-3" style={{ background: '#0E8FA3' }}>
          <button
            onClick={prevMonth}
            className="text-white font-bold text-xl w-8 h-8 flex items-center justify-center rounded hover:bg-white/20"
          >‹</button>
          <span className="text-white font-semibold text-sm">
            {MONTHS[month]} {year}
          </span>
          <button
            onClick={nextMonth}
            className="text-white font-bold text-xl w-8 h-8 flex items-center justify-center rounded hover:bg-white/20"
          >›</button>
        </div>

        {/* Weekdays */}
        <div className="grid grid-cols-7 bg-teal-light px-2 pt-2">
          {DAYS.map(d => (
            <div key={d} className="text-center text-xs font-bold text-gray-500 py-1">{d}</div>
          ))}
        </div>

        {/* Grid */}
        <div className="grid grid-cols-7 px-2 pb-2">
          {cells.map((day, i) => {
            if (!day) return <div key={i} />
            const iso = `${year}-${String(month + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`
            const isToday = iso === todayStr
            const isSel = iso === value
            return (
              <button
                key={i}
                onClick={() => pick(day)}
                className={`h-9 w-full rounded text-sm font-medium transition-colors
                  ${isSel ? 'text-white' : isToday ? 'font-bold' : 'text-gray-700 hover:bg-teal-light'}
                `}
                style={isSel ? { background: '#0E8FA3' } : isToday ? { border: '2px solid #0E8FA3', color: '#0E8FA3' } : {}}
              >
                {day}
              </button>
            )
          })}
        </div>

        {/* Footer */}
        <div className="flex justify-between px-4 pb-3 border-t pt-2">
          <button
            onClick={() => { onChange(null); onClose() }}
            className="text-xs text-red-500 hover:underline px-2 py-1"
          >
            Sem prazo
          </button>
          <button
            onClick={() => { onChange(todayStr); onClose() }}
            className="text-xs font-semibold px-3 py-1 rounded-full"
            style={{ background: '#e0f7fa', color: '#0E8FA3' }}
          >
            Hoje
          </button>
        </div>
      </div>
    </div>
  )
}
