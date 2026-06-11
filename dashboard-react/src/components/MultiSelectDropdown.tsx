import { useState, useRef, useEffect, useCallback } from 'react'

export function parseFornVal(val: string): { nome: string; cnpj: string } {
  if (!val) return { nome: '', cnpj: '' }
  const idx = val.indexOf('|||')
  return idx === -1
    ? { nome: val, cnpj: '' }
    : { nome: val.slice(0, idx), cnpj: val.slice(idx + 3) }
}

interface Option {
  key: string
  label: string
}

interface Props {
  options: Option[]
  selected: Set<string>
  onToggle: (key: string) => void
  onClear: () => void
  placeholder?: string
  minWidth?: string
}

export function MultiSelectDropdown({
  options, selected, onToggle, onClear,
  placeholder = 'Todos', minWidth = '220px',
}: Props) {
  const [open, setOpen] = useState(false)
  const [search, setSearch] = useState('')
  const wrapRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (wrapRef.current && !wrapRef.current.contains(e.target as Node)) setOpen(false)
    }
    document.addEventListener('mousedown', handler)
    return () => document.removeEventListener('mousedown', handler)
  }, [])

  const filtered = search
    ? options.filter(o => o.label.toLowerCase().includes(search.toLowerCase()))
    : options

  const label =
    selected.size === 0
      ? placeholder
      : selected.size === 1
      ? (options.find(o => o.key === [...selected][0])?.label ?? [...selected][0])
      : `${selected.size} selecionados`

  const handleToggle = useCallback((key: string, e: React.MouseEvent) => {
    e.stopPropagation()
    onToggle(key)
  }, [onToggle])

  return (
    <div ref={wrapRef} className="relative inline-block" style={{ minWidth }}>
      <button
        type="button"
        onClick={() => setOpen(o => !o)}
        className="w-full flex justify-between items-center gap-2 rounded-md px-3 py-1.5 text-[13px] bg-white text-[#333] cursor-pointer hover:bg-gray-50 transition-colors"
      >
        <span className="truncate">{label}</span>
        <span className="text-gray-500 shrink-0 text-xs">{open ? '▲' : '▼'}</span>
      </button>

      {open && (
        <div className="absolute top-[calc(100%+3px)] left-0 z-50 bg-white border border-gray-300 rounded-md shadow-xl overflow-hidden"
             style={{ minWidth: 'max(100%, 300px)' }}>
          <input
            type="text"
            className="w-full px-3 py-2 border-b border-gray-200 text-[13px] outline-none text-[#333]"
            placeholder="Buscar fornecedor..."
            value={search}
            onChange={e => setSearch(e.target.value)}
            onClick={e => e.stopPropagation()}
            autoFocus
          />
          <div className="max-h-64 overflow-y-auto">
            {filtered.map(opt => (
              <div
                key={opt.key}
                className={`flex items-center gap-2.5 px-3 py-2 cursor-pointer text-[13px] border-b border-gray-50 hover:bg-[#e8f7fa] transition-colors ${selected.has(opt.key) ? 'bg-[#d4eef3] font-semibold' : ''}`}
                onClick={e => handleToggle(opt.key, e)}
              >
                <input
                  type="checkbox"
                  checked={selected.has(opt.key)}
                  readOnly
                  className="cursor-pointer accent-[#0E8FA3] w-3.5 h-3.5 shrink-0"
                />
                <span className="cursor-pointer flex-1 leading-tight">{opt.label}</span>
              </div>
            ))}
            {filtered.length === 0 && (
              <div className="px-3 py-4 text-xs text-gray-400 text-center">Nenhum resultado</div>
            )}
          </div>
          {selected.size > 0 && (
            <div
              className="px-3 py-2 text-right text-xs text-[#0E8FA3] font-bold cursor-pointer border-t border-gray-200 hover:bg-[#e8f7fa]"
              onClick={() => { onClear(); setSearch('') }}
            >
              ✕ Limpar seleção ({selected.size})
            </div>
          )}
        </div>
      )}
    </div>
  )
}
