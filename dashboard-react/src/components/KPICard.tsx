interface KPICardProps {
  value: number | string
  label: string
  color?: 'teal' | 'green' | 'red' | 'yellow' | 'orange' | 'gray'
  tooltip?: string
  id?: string
}

const colorMap: Record<string, { border: string; value: string }> = {
  teal:   { border: 'border-t-[#0E8FA3]', value: 'text-[#0E8FA3]' },
  green:  { border: 'border-t-[#28A745]', value: 'text-[#28A745]' },
  red:    { border: 'border-t-[#DC3545]', value: 'text-[#DC3545]' },
  yellow: { border: 'border-t-[#FFC107]', value: 'text-[#b38600]' },
  orange: { border: 'border-t-[#F4793B]', value: 'text-[#F4793B]' },
  gray:   { border: 'border-t-[#6C757D]', value: 'text-[#6C757D]' },
}

export function KPICard({ value, label, color = 'teal', tooltip, id }: KPICardProps) {
  const { border, value: valColor } = colorMap[color] ?? colorMap.teal

  return (
    <div
      id={id}
      className={`bg-white rounded-xl p-4 shadow-sm border-t-4 ${border} text-center relative group`}
    >
      <div className={`text-3xl font-bold leading-none ${valColor}`}>{value}</div>
      <div className="text-xs text-gray-500 mt-1.5 font-semibold uppercase tracking-wide leading-snug">
        {label.split('<br>').map((l, i) => (
          <span key={i}>{i > 0 && <br />}{l}</span>
        ))}
      </div>
      {tooltip && (
        <div className="absolute bottom-[calc(100%+8px)] left-1/2 -translate-x-1/2 w-56 bg-[#1a2a35] text-white text-xs rounded-lg px-3 py-2 text-left opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all z-50 shadow-xl pointer-events-none whitespace-normal leading-snug">
          {tooltip}
          <div className="absolute top-full left-1/2 -translate-x-1/2 border-4 border-transparent border-t-[#1a2a35]" />
        </div>
      )}
    </div>
  )
}
