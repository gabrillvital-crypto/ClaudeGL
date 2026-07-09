import { useState } from 'react'
import TabList from './tabs/TabList'
import TabHoje from './tabs/TabHoje'
import TabAtividades from './tabs/TabAtividades'
import TabEmAndamento from './tabs/TabEmAndamento'
import TabEntrada from './tabs/TabEntrada'
import TaskDetailModal from './components/TaskDetailModal'
import ReportModal from './components/ReportModal'

const TABS = [
  { id: 'pessoal',      label: 'Pessoal',      emoji: '👤' },
  { id: 'profissional', label: 'Profissional',  emoji: '💼' },
  { id: 'hoje',         label: 'Hoje',          emoji: '📅', color: '#ea580c' },
  { id: 'atividades',   label: 'Atividades',    emoji: '✅', color: '#059669' },
  { id: 'andamento',    label: 'Andamento',     emoji: '▶',  color: '#b45309' },
  { id: 'entrada',      label: 'Entrada',       emoji: '📥', color: '#7c3aed' },
]

export default function App() {
  const [activeTab, setActiveTab] = useState('profissional')
  const [openTaskId, setOpenTaskId] = useState(null)
  const [showReport, setShowReport] = useState(false)
  const [refreshKey, setRefreshKey] = useState(0)

  function refresh() { setRefreshKey(k => k + 1) }

  const tab = TABS.find(t => t.id === activeTab)

  return (
    <div className="h-screen flex flex-col bg-gray-50 max-w-3xl mx-auto">

      {/* Header */}
      <div className="flex items-center gap-2 px-4 py-3 shadow-sm" style={{ background: '#0E8FA3' }}>
        <div className="flex-1">
          <h1 className="text-white font-bold text-base leading-tight">Gestão Efcaz</h1>
          <p className="text-white/70 text-xs">CS Task Manager</p>
        </div>
        <button
          onClick={() => setShowReport(true)}
          className="text-xs font-bold px-3 py-1.5 rounded-lg bg-white/20 text-white hover:bg-white/30"
        >📊 Relatório</button>
      </div>

      {/* Tab nav */}
      <div className="flex overflow-x-auto border-b border-gray-200 bg-white">
        {TABS.map(t => {
          const active = activeTab === t.id
          const color = t.color || '#0E8FA3'
          return (
            <button
              key={t.id}
              onClick={() => setActiveTab(t.id)}
              className={`flex items-center gap-1.5 px-4 py-2.5 text-xs font-semibold whitespace-nowrap border-b-2 transition-colors ${
                active ? 'border-current' : 'border-transparent text-gray-400 hover:text-gray-600'
              }`}
              style={active ? { color, borderColor: color } : {}}
            >
              <span>{t.emoji}</span>
              <span className="hidden sm:inline">{t.label}</span>
            </button>
          )
        })}
      </div>

      {/* Tab content */}
      <div className="flex-1 overflow-hidden">
        {activeTab === 'pessoal' && (
          <TabList key={`pessoal-${refreshKey}`} tab="pessoal" onOpenTask={setOpenTaskId} />
        )}
        {activeTab === 'profissional' && (
          <TabList key={`profissional-${refreshKey}`} tab="profissional" onOpenTask={setOpenTaskId} />
        )}
        {activeTab === 'hoje' && (
          <TabHoje onOpenTask={setOpenTaskId} refresh={refreshKey} />
        )}
        {activeTab === 'atividades' && (
          <TabAtividades refresh={refreshKey} />
        )}
        {activeTab === 'andamento' && (
          <TabEmAndamento onOpenTask={setOpenTaskId} refresh={refreshKey} />
        )}
        {activeTab === 'entrada' && (
          <TabEntrada onSaved={() => { refresh(); setActiveTab('profissional') }} />
        )}
      </div>

      {/* Modals */}
      {openTaskId && (
        <TaskDetailModal
          taskId={openTaskId}
          onClose={() => setOpenTaskId(null)}
          onSaved={() => { setOpenTaskId(null); refresh() }}
          onDeleted={() => { setOpenTaskId(null); refresh() }}
        />
      )}

      {showReport && <ReportModal onClose={() => setShowReport(false)} />}
    </div>
  )
}
