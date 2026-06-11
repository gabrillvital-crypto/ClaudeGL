import { useState, type ReactNode } from 'react'

interface SectionWrapperProps {
  title: ReactNode
  badge?: string | number
  children: ReactNode
  defaultCollapsed?: boolean
}

export function SectionWrapper({ title, badge, children, defaultCollapsed = true }: SectionWrapperProps) {
  const [collapsed, setCollapsed] = useState(defaultCollapsed)

  return (
    <div className="mb-6">
      <div
        className="flex items-center justify-between border-b-2 border-[#0E8FA3] pb-2 mb-4 cursor-pointer select-none"
        onClick={() => setCollapsed(c => !c)}
      >
        <h2 className="text-base font-bold text-[#0E8FA3] tracking-tight flex items-center gap-2">
          {title}
          {badge !== undefined && (
            <span className="bg-gray-500 text-white text-xs px-2 py-0.5 rounded-full font-semibold">
              {badge}
            </span>
          )}
        </h2>
        <span className="text-xs bg-[#0E8FA3]/10 border border-[#0E8FA3]/30 text-[#0E8FA3] px-2 py-0.5 rounded font-bold select-none">
          {collapsed ? '▼ Expandir' : '▲ Recolher'}
        </span>
      </div>
      {!collapsed && children}
    </div>
  )
}
