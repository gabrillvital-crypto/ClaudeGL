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
  { id: 'hoje',         label: 'Hoje',          emoji: '📅' },
  { id: 'andamento',    label: 'Andamento',     emoji: '▶' },
  { id: 'atividades',   label: 'Concluídas',    emoji: '✅' },
  { id: 'entrada',      label: 'Entrada IA',    emoji: '✨' },
]

const TAB_GROUPS = [
  { label: 'Áreas',       ids: ['pessoal', 'profissional'] },
  { label: 'Focado',      ids: ['hoje', 'andamento'] },
  { label: 'Ferramentas', ids: ['atividades', 'entrada'] },
]

export default function App() {
  const [activeTab, setActiveTab] = useState('profissional')
  const [openTaskId, setOpenTaskId] = useState(null)
  const [showReport, setShowReport] = useState(false)
  const [refreshKey, setRefreshKey] = useState(0)

  function refresh() { setRefreshKey(k => k + 1) }

  const tab = TABS.find(t => t.id === activeTab)

  return (
    <div className="h-screen flex" style={{ background: '#F8FAFC' }}>

      {/* Sidebar */}
      <aside className="w-56 flex flex-col shrink-0" style={{ background: '#153C5C' }}>

        {/* Logo */}
        <div className="px-4 py-5" style={{ borderBottom: '1px solid rgba(255,255,255,0.08)' }}>
          <div className="flex items-center gap-2.5">
            <div
              className="w-8 h-8 rounded-lg flex items-center justify-center shrink-0"
              style={{ background: '#14B3CC' }}
            >
              <span className="text-white text-xs font-bold tracking-tight">GE</span>
            </div>
            <div>
              <p className="text-white font-semibold text-sm leading-tight">Gestão Efcaz</p>
              <p className="text-xs leading-tight" style={{ color: '#6B7280' }}>CS Task Manager</p>
            </div>
          </div>
        </div>

        {/* Nav agrupada */}
        <nav className="flex-1 py-4 px-2 overflow-y-auto">
          {TAB_GROUPS.map((group, gi) => (
            <div key={group.label} className={gi > 0 ? 'mt-5' : ''}>
              <p
                className="px-3 mb-1.5 font-semibold tracking-widest uppercase"
                style={{ fontSize: '9px', color: '#4B5563' }}
              >
                {group.label}
              </p>
              {group.ids.map(id => {
                const t = TABS.find(x => x.id === id)
                const active = activeTab === id
                return (
                  <button
                    key={id}
                    onClick={() => setActiveTab(id)}
                    className={`w-full flex items-center gap-2.5 px-3 py-2 text-sm rounded-lg mb-0.5 transition-colors text-left font-medium ${
                      active
                        ? 'text-white'
                        : 'text-gray-400 hover:bg-white/5 hover:text-gray-200'
                    }`}
                    style={active ? { background: '#14B3CC' } : {}}
                  >
                    <span className="text-sm leading-none">{t.emoji}</span>
                    <span>{t.label}</span>
                  </button>
                )
              })}
            </div>
          ))}
        </nav>

        {/* Rodapé sidebar */}
        <div className="p-3" style={{ borderTop: '1px solid rgba(255,255,255,0.08)' }}>
          <button
            onClick={() => setShowReport(true)}
            className="w-full flex items-center gap-2.5 px-3 py-2 text-sm rounded-lg text-gray-400 hover:bg-white/5 hover:text-gray-200 transition-colors"
          >
            <span>📊</span>
            <span>Relatório</span>
          </button>
        </div>
      </aside>

      {/* Área de conteúdo */}
      <main className="flex-1 flex flex-col overflow-hidden">

        {/* Header da aba */}
        <div className="flex items-center gap-3 px-6 py-4 bg-white shrink-0" style={{ borderBottom: '1px solid #E8EEF4' }}>
          <span className="text-lg leading-none">{tab.emoji}</span>
          <h2 className="font-semibold text-gray-900">{tab.label}</h2>
        </div>

        {/* Conteúdo */}
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

      {/* Modais */}
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
