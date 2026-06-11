import { useState, type ReactNode } from 'react'

interface Props {
  title: string
  children: ReactNode
  defaultOpen?: boolean
}

export function Section({ title, children, defaultOpen = false }: Props) {
  const [open, setOpen] = useState(defaultOpen)

  return (
    <div className="mb-1">
      <div
        className="flex items-center justify-between border-b-2 border-[#0E8FA3] pb-2 mt-7 mb-0 cursor-pointer select-none"
        onClick={() => setOpen(o => !o)}
      >
        <span className="text-[16px] font-bold text-[#0E8FA3] tracking-wide">{title}</span>
        <button className="text-xs bg-[rgba(14,143,163,0.1)] border border-[rgba(14,143,163,0.3)] text-[#0E8FA3] rounded px-3 py-0.5 font-bold hover:bg-[rgba(14,143,163,0.2)] transition-colors">
          {open ? '▲ Recolher' : '▼ Expandir'}
        </button>
      </div>
      {open && <div className="pt-3">{children}</div>}
    </div>
  )
}
