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
    <div className="h-screen flex bg-gray-100">

      {/* Sidebar */}
      <aside className="w-52 flex flex-col bg-white border-r border-gray-200 shadow-sm shrink-0">
        {/* Logo */}
        <div className="px-5 py-5" style={{ background: '#0E8FA3' }}>
          <h1 className="text-white font-bold text-sm leading-tight tracking-wide">Gestão Efcaz</h1>
          <p className="text-white/60 text-xs mt-0.5">CS Task Manager</p>
        </div>

        {/* Nav */}
        <nav className="flex-1 py-3 overflow-y-auto">
          {TABS.map(t => {
            const active = activeTab === t.id
            const color = t.color || '#0E8FA3'
            return (
              <button
                key={t.id}
                onClick={() => setActiveTab(t.id)}
                className={`w-full flex items-center gap-3 px-4 py-2.5 text-sm font-medium transition-all text-left ${
                  active
                    ? 'text-white rounded-none'
                    : 'text-gray-500 hover:bg-gray-50 hover:text-gray-700'
                }`}
                style={active ? { background: color } : {}}
              >
                <span className="text-base">{t.emoji}</span>
                <span>{t.label}</span>
              </button>
            )
          })}
        </nav>

        {/* Report */}
        <div className="p-3 border-t border-gray-100">
          <button
            onClick={() => setShowReport(true)}
            className="w-full flex items-center gap-2 px-3 py-2 text-xs font-semibold rounded-lg text-gray-600 bg-gray-50 hover:bg-gray-100 transition-colors"
          >
            <span>📊</span>
            <span>Relatório</span>
          </button>
        </div>
      </aside>

      {/* Content */}
      <main className="flex-1 flex flex-col overflow-hidden">

        {/* Content header */}
        <div className="flex items-center px-6 py-3 bg-white border-b border-gray-200 shrink-0">
          <span className="text-lg mr-2">{tab.emoji}</span>
          <h2 className="font-semibold text-gray-800">{tab.label}</h2>
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
      </main>

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
