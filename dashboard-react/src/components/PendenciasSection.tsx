import { useState, useMemo, useEffect, useCallback } from 'react'
import type { PendRow } from '../types'
import { exportCSV, exportPendPDFGrouped, exportPendXLSXGrouped } from '../utils/exportUtils'

// ── Constantes ─────────────────────────────────────────────────────────────

const PAGE_SIZE = 150

interface Props {
  data: PendRow[]
  aClassificar?: PendRow[]
  geradoEm?: string
  isFornFiltered?: boolean
}

// ── Helpers de formatação ──────────────────────────────────────────────────

function fmtCNPJ(d: string): string {
  const n = d.replace(/\D/g, '')
  if (n.length === 11) return n.replace(/(\d{3})(\d{3})(\d{3})(\d{2})/, '$1.$2.$3-$4')
  if (n.length === 14) return n.replace(/(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})/, '$1.$2.$3/$4-$5')
  return d
}

function areaBadge(a: string) {
  const m: Record<string, string> = {
    TERCEIROS: 'bg-[#e8f0fe] text-[#1a73e8]',
    DOCUMENTOS: 'bg-[#fce8d5] text-[#c05000]',
  }
  const label: Record<string, string> = { TERCEIROS: 'Terceiros', DOCUMENTOS: 'Fornecedor' }
  return (
    <span className={`inline-block px-2 py-0.5 rounded-full text-[11px] font-bold ${m[a] ?? 'bg-gray-100 text-gray-600'}`}>
      {label[a] ?? a}
    </span>
  )
}

function StatusRealBadge({ s }: { s: string }) {
  if (s === 'Ativa')         return <span className="inline-block px-2 py-0.5 rounded-full text-[11px] font-bold bg-[#fff3cd] text-[#856404]">Ativa</span>
  if (s === 'Não resolvida') return <span className="inline-block px-2 py-0.5 rounded-full text-[11px] font-bold bg-[#fde8e8] text-[#b91c1c]">Não resolvida</span>
  if (s === 'Resolvida')     return <span className="inline-block px-2 py-0.5 rounded-full text-[11px] font-bold bg-[#d4edda] text-[#155724]">Resolvida</span>
  return null
}

function CompBadge({ c }: { c: string }) {
  if (c === 'Não possui competência')
    return <span className="bg-[#f0f0f0] text-[#999] text-[11px] px-2 py-0.5 rounded italic">{c}</span>
  if (c === 'A classificar')
    return <span className="bg-[#fff3cd] text-[#856404] text-[11px] px-2 py-0.5 rounded italic" title="Campo estruturado vazio ou data anterior ao contrato (nov/2025)">A classificar</span>
  if (c)
    return <span className="bg-[#e8f7fa] text-[#0E8FA3] text-[11px] px-2 py-0.5 rounded">{c}</span>
  return <span className="text-[#ccc]">—</span>
}

// ── Lógica de agrupamento e ordenação ─────────────────────────────────────

function parseCompDate(comp: string): Date | null {
  const m = comp.match(/^(\d{2})\/(20\d{2}|\d{2})/)
  if (!m) return null
  const mm = parseInt(m[1], 10)
  const rawY = m[2]
  const yyyy = rawY.length === 4 ? parseInt(rawY) : 2000 + parseInt(rawY)
  return new Date(yyyy, mm - 1, 1)
}

function hasDateComp(comp: string): boolean {
  return comp !== 'A classificar' && comp !== 'Não possui competência' && !!parseCompDate(comp)
}

/**
 * Ordem: A classificar primeiro → competências com data ASC (Jan → Fev → ...) → Sem competência
 */
function sortCompKeys(keys: string[]): string[] {
  const withDate: [string, Date][] = []
  const aClass: string[] = []
  const semComp: string[] = []
  const outros: string[] = []
  for (const k of keys) {
    if (k === 'A classificar')          { aClass.push(k); continue }
    if (k === 'Não possui competência') { semComp.push(k); continue }
    const d = parseCompDate(k)
    if (d) withDate.push([k, d])
    else   outros.push(k)
  }
  withDate.sort(([, a], [, b]) => a.getTime() - b.getTime()) // crescente: Jan → Fev → ...
  return [...aClass, ...withDate.map(([k]) => k), ...outros, ...semComp]
}

function groupByComp(rows: PendRow[]): Map<string, PendRow[]> {
  const map = new Map<string, PendRow[]>()
  for (const r of rows) {
    const key = r.Competencia || 'A classificar'
    if (!map.has(key)) map.set(key, [])
    map.get(key)!.push(r)
  }
  return map
}

/** Achata os dados na ordem dos grupos (para paginação correta) */
function flattenInOrder(rows: PendRow[]): PendRow[] {
  const grouped = groupByComp(rows)
  const keys = sortCompKeys([...grouped.keys()])
  const result: PendRow[] = []
  for (const key of keys) result.push(...(grouped.get(key) ?? []))
  return result
}

// ── Componente de navegação ────────────────────────────────────────────────

function NavBtn({ label, disabled, onClick }: { label: string; disabled: boolean; onClick: () => void }) {
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className={`px-2.5 py-1.5 text-[12px] font-semibold rounded border transition-colors select-none
        ${disabled
          ? 'border-[#ddd] text-[#bbb] cursor-not-allowed'
          : 'border-[#0E8FA3] text-[#0E8FA3] hover:bg-[#0E8FA3] hover:text-white'
        }`}
    >
      {label}
    </button>
  )
}

interface PaginationBarProps {
  currentPage: number
  totalPages: number
  pageStart: number   // 1-indexed, exibição
  pageEnd: number     // 1-indexed, exibição
  totalItems: number
  onFirst: () => void
  onPrev: () => void
  onNext: () => void
  onLast: () => void
}

function PaginationBar({ currentPage, totalPages, pageStart, pageEnd, totalItems, onFirst, onPrev, onNext, onLast }: PaginationBarProps) {
  if (totalPages <= 1) return null
  return (
    <div className="flex flex-wrap items-center justify-between gap-3 py-3 px-1">
      <p className="text-[12px] text-[#6C757D]">
        Exibindo{' '}
        <strong className="text-[#333]">{pageStart.toLocaleString('pt-BR')}–{pageEnd.toLocaleString('pt-BR')}</strong>
        {' '}de{' '}
        <strong className="text-[#333]">{totalItems.toLocaleString('pt-BR')}</strong> registros
      </p>
      <div className="flex items-center gap-1.5">
        <NavBtn label="« Primeira"  disabled={currentPage === 1}          onClick={onFirst} />
        <NavBtn label="‹ Anterior"  disabled={currentPage === 1}          onClick={onPrev}  />
        <span className="px-3 py-1.5 text-[12px] font-bold text-[#0E8FA3] bg-[#e8f7fa] rounded border border-[#b2dce6] min-w-[120px] text-center">
          Página {currentPage} de {totalPages}
        </span>
        <NavBtn label="Próxima ›"   disabled={currentPage === totalPages} onClick={onNext}  />
        <NavBtn label="Última »"    disabled={currentPage === totalPages} onClick={onLast}  />
      </div>
    </div>
  )
}

// ── Linha da tabela ────────────────────────────────────────────────────────

const TABLE_HEADERS = ['Situação Real', 'Fornecedor', 'Área', 'Documento', 'Competência', 'Detalhe']

function PendRowItem({ r, i }: { r: PendRow; i: number }) {
  return (
    <tr className={`border-b border-[#e5eef1] hover:bg-[#d4eef3] ${i % 2 === 1 ? 'bg-[#f0f8fa]' : ''}`}>
      <td className="px-3 py-2 whitespace-nowrap"><StatusRealBadge s={r.StatusReal} /></td>
      <td className="px-3 py-2">
        <div className="font-medium">{r.Fornecedor}</div>
        {r.CNPJ_Forn && <div className="text-[11px] text-[#999] font-mono mt-0.5">{fmtCNPJ(r.CNPJ_Forn)}</div>}
      </td>
      <td className="px-3 py-2">{areaBadge(r.Area)}</td>
      <td className="px-3 py-2 font-semibold">{r.Documento}</td>
      <td className="px-3 py-2"><CompBadge c={r.Competencia} /></td>
      <td className="px-3 py-2 text-[12px] text-[#666] break-words" style={{ minWidth: '240px', maxWidth: '420px' }}>{r.Detalhe}</td>
    </tr>
  )
}

// ── Bloco de grupo de competência ──────────────────────────────────────────

interface GroupBlockProps {
  compKey: string
  rows: PendRow[]
  /** Nota de contexto de página — exibida no header quando grupo está parcial */
  pageNote?: string
  initExpanded?: boolean
}

function GroupBlock({ compKey, rows, pageNote, initExpanded = true }: GroupBlockProps) {
  const [expanded, setExpanded] = useState(initExpanded)
  const isAClass  = compKey === 'A classificar'
  const isSemComp = compKey === 'Não possui competência'
  const hasDate   = hasDateComp(compKey)

  const borderColor = isAClass ? '#f59e0b' : isSemComp ? '#ccc' : '#0E8FA3'
  const headerBg    = isAClass ? 'bg-[#fff3cd]' : isSemComp ? 'bg-[#f5f5f5]' : 'bg-[#e8f7fa]'
  const headerText  = isAClass ? 'text-[#92400e]' : isSemComp ? 'text-[#555]' : 'text-[#0c7a8c]'
  const countText   = isAClass ? 'text-[#a16207]' : isSemComp ? 'text-[#777]' : 'text-[#0c7a8c]'
  const icon        = isAClass ? '⚠️' : isSemComp ? '—' : '📅'

  return (
    <div className="mb-3 rounded-lg overflow-hidden" style={{ border: `1.5px solid ${borderColor}` }}>
      <div
        className={`flex items-center justify-between px-4 py-2.5 cursor-pointer select-none ${headerBg} border-b`}
        style={{ borderBottomColor: borderColor }}
        onClick={() => setExpanded(e => !e)}
      >
        <div className={`flex items-center gap-2 font-bold text-[13px] ${headerText}`}>
          <span>{icon}</span>
          <span>{isAClass ? 'A classificar' : isSemComp ? 'Sem competência / Eventualidades' : compKey}</span>
          {hasDate && (
            <span className="text-[10px] font-normal px-1.5 py-0.5 rounded bg-white/60 text-[#0E8FA3] border border-[#b2dce6]">
              mensal
            </span>
          )}
          <span className={`font-normal text-[12px] ${countText}`}>
            ({rows.length} pendência{rows.length !== 1 ? 's' : ''}{pageNote ? ` ${pageNote}` : ''})
          </span>
        </div>
        <span className={`text-[12px] ${headerText}`}>{expanded ? '▲' : '▼'}</span>
      </div>

      {expanded && (
        <div className="overflow-x-auto">
          <table className="w-full text-[13px] border-collapse">
            <thead>
              <tr className="bg-[#0E8FA3] text-white">
                {TABLE_HEADERS.map(h => (
                  <th key={h} className="px-3 py-2 text-left font-bold">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {rows.map((r, i) => <PendRowItem key={i} r={r} i={i} />)}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}

// ── Divisor de seção (modo híbrido) ───────────────────────────────────────

function SectionDivider({ label, color }: { label: string; color: string }) {
  return (
    <div className="flex items-center gap-3 mb-3 mt-1">
      <div className="h-px flex-1 opacity-40" style={{ backgroundColor: color }} />
      <span className="text-[11px] font-bold uppercase tracking-widest px-2" style={{ color }}>
        {label}
      </span>
      <div className="h-px flex-1 opacity-40" style={{ backgroundColor: color }} />
    </div>
  )
}

// ── Componente principal ───────────────────────────────────────────────────

export function PendenciasSection({ data, aClassificar = [], geradoEm = '', isFornFiltered = false }: Props) {
  const [pdfLoading, setPdfLoading]   = useState(false)
  const [viewMode, setViewMode]       = useState<'grouped' | 'flat'>('grouped')
  const [currentPage, setCurrentPage] = useState(1)

  // Reset de página sempre que os dados mudarem (filtro aplicado)
  useEffect(() => { setCurrentPage(1) }, [data])
  // Reset de página ao mudar de view
  useEffect(() => { setCurrentPage(1) }, [viewMode])

  // ── Paginação ──────────────────────────────────────────────────────────

  /** Lista completa achata na ordem dos grupos (base para slice de página) */
  const flatOrdered = useMemo(() => flattenInOrder(data), [data])

  const totalItems  = flatOrdered.length
  const totalPages  = Math.max(1, Math.ceil(totalItems / PAGE_SIZE))

  // Clamp currentPage ao range válido
  const safePage    = Math.min(Math.max(1, currentPage), totalPages)
  const pageStartIdx = (safePage - 1) * PAGE_SIZE           // 0-indexed
  const pageEndIdx   = Math.min(safePage * PAGE_SIZE, totalItems)
  const pageStart    = totalItems === 0 ? 0 : pageStartIdx + 1 // 1-indexed para exibição
  const pageEnd      = pageEndIdx                               // 1-indexed para exibição

  const pagedData = useMemo(
    () => flatOrdered.slice(pageStartIdx, pageEndIdx),
    [flatOrdered, pageStartIdx, pageEndIdx],
  )

  // Agrupamentos do slice atual (para modo agrupado)
  const pagedGrouped    = useMemo(() => groupByComp(pagedData), [pagedData])
  const pagedKeys       = useMemo(() => sortCompKeys([...pagedGrouped.keys()]), [pagedGrouped])
  const pagedKeysComData = useMemo(() => pagedKeys.filter(k => hasDateComp(k)), [pagedKeys])
  const pagedKeysSemData = useMemo(() => pagedKeys.filter(k => !hasDateComp(k)), [pagedKeys])

  // Auto-expand: expande todos quando há poucos grupos na página
  const autoExpand = pagedKeys.length <= 4

  // Navegação
  const goFirst = useCallback(() => setCurrentPage(1),             [])
  const goPrev  = useCallback(() => setCurrentPage(p => p - 1),   [])
  const goNext  = useCallback(() => setCurrentPage(p => p + 1),   [])
  const goLast  = useCallback(() => setCurrentPage(totalPages),    [totalPages])

  // Flat rows para exportação (todos os dados, não só a página atual)
  const flatRows = useMemo(() => flatOrdered.map(r => ({
    Fornecedor: r.Fornecedor,
    CNPJ: fmtCNPJ(r.CNPJ_Forn),
    Area: r.Area,
    Documento: r.Documento,
    Competencia: r.Competencia,
    Detalhe: r.Detalhe,
    StatusReal: r.StatusReal,
  })), [flatOrdered])

  function handlePDF() {
    setPdfLoading(true)
    setTimeout(() => {
      exportPendPDFGrouped(data, geradoEm, 'pendencias_zurich')
      setPdfLoading(false)
    }, 50)
  }

  const paginationProps: PaginationBarProps = {
    currentPage: safePage,
    totalPages,
    pageStart,
    pageEnd,
    totalItems,
    onFirst: goFirst,
    onPrev:  goPrev,
    onNext:  goNext,
    onLast:  goLast,
  }

  // ── Render ────────────────────────────────────────────────────────────

  return (
    <div id="section-pendencias">

      {/* ── Alerta: registros "A classificar" ───────────────────────────── */}
      {aClassificar.length > 0 && (
        <div className="bg-[#fff8e1] border border-[#f59e0b] rounded-xl p-4 mb-4 flex items-start gap-3">
          <span className="text-[#f59e0b] text-xl mt-0.5">⚠️</span>
          <div className="w-full">
            <p className="text-[13px] font-bold text-[#92400e] mb-1">
              {aClassificar.length} pendência(s) classificadas como "A classificar"
            </p>
            <p className="text-[12px] text-[#78350f] mb-2">
              Estes registros exigem competência mas não possuem data válida no campo estruturado
              <strong> "Marcas e representações"</strong>. Motivo: campo vazio <em>ou</em> data
              anterior ao início do contrato Zurich (novembro/2025). Verifique e preencha
              o campo na plataforma para que a competência seja registrada corretamente.
            </p>
            <div className="overflow-x-auto">
              <table className="text-[12px] border-collapse w-full">
                <thead>
                  <tr className="bg-[#fef3c7]">
                    {['Fornecedor', 'Documento', 'Área', 'Status Real'].map(h => (
                      <th key={h} className="px-3 py-1.5 text-left font-semibold text-[#92400e] border border-[#fde68a]">{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {aClassificar.map((r, i) => (
                    <tr key={i} className="border-b border-[#fde68a]">
                      <td className="px-3 py-1.5 text-[#78350f]">{r.Fornecedor}</td>
                      <td className="px-3 py-1.5 font-semibold text-[#78350f]">{r.Documento}</td>
                      <td className="px-3 py-1.5">{r.Area === 'TERCEIROS' ? 'Terceiros' : 'Fornecedor'}</td>
                      <td className="px-3 py-1.5"><StatusRealBadge s={r.StatusReal} /></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* ── Barra de controles ──────────────────────────────────────────── */}
      <div className="bg-white rounded-xl shadow-sm p-4 mb-3 flex flex-wrap gap-3 items-center justify-between">
        {/* Toggle de visualização */}
        <div className="flex items-center gap-1 bg-[#f0f8fa] rounded-lg p-1">
          <button
            onClick={() => setViewMode('grouped')}
            className={`px-3 py-1.5 rounded text-[12px] font-semibold transition-colors ${
              viewMode === 'grouped' ? 'bg-[#0E8FA3] text-white shadow-sm' : 'text-[#0E8FA3] hover:bg-[#d4eef3]'
            }`}
          >
            📅 Por Competência
          </button>
          <button
            onClick={() => setViewMode('flat')}
            className={`px-3 py-1.5 rounded text-[12px] font-semibold transition-colors ${
              viewMode === 'flat' ? 'bg-[#0E8FA3] text-white shadow-sm' : 'text-[#0E8FA3] hover:bg-[#d4eef3]'
            }`}
          >
            ☰ Lista Simples
          </button>
        </div>

        {/* Exportações — sempre sobre todos os dados (não só a página) */}
        <div className="flex items-center gap-2">
          <span className="text-[11px] text-[#999] font-semibold uppercase mr-1">Exportar:</span>
          <button
            onClick={() => exportPendXLSXGrouped(data, 'pendencias_zurich')}
            className="bg-[#28A745] text-white rounded px-3 py-1.5 text-[13px] font-semibold hover:bg-[#1e7e34]"
          >
            Excel
          </button>
          <button
            onClick={() => exportCSV(flatRows, 'pendencias_zurich')}
            className="bg-[#6C757D] text-white rounded px-3 py-1.5 text-[13px] font-semibold hover:bg-[#545b62]"
          >
            CSV
          </button>
          <button
            onClick={handlePDF}
            disabled={pdfLoading}
            className="bg-[#DC3545] text-white rounded px-3 py-1.5 text-[13px] font-semibold hover:bg-[#b02a37] disabled:opacity-60 disabled:cursor-wait flex items-center gap-1"
          >
            {pdfLoading ? '⏳' : '⬇'} PDF
          </button>
        </div>
      </div>

      {/* ── Indicador geral ─────────────────────────────────────────────── */}
      <div className="flex items-center justify-between mb-2 px-1">
        <p className="text-[13px] text-[#6C757D]">
          {totalItems.toLocaleString('pt-BR')} pendência{totalItems !== 1 ? 's' : ''}
          {viewMode === 'grouped' && pagedKeys.length > 0 && (
            <span className="ml-2 text-[#0E8FA3]">
              · {pagedKeys.length} competência{pagedKeys.length !== 1 ? 's' : ''} nesta página
            </span>
          )}
        </p>
      </div>

      {/* ── Paginação TOPO ──────────────────────────────────────────────── */}
      <PaginationBar {...paginationProps} />

      {/* ── VIEW: Agrupado por Competência ────────────────────────────── */}
      {viewMode === 'grouped' && (
        <>
          {totalItems === 0 && (
            <div className="bg-white rounded-xl p-8 text-center text-[#999]">
              Nenhuma pendência encontrada
            </div>
          )}

          {isFornFiltered ? (
            /* Modo híbrido: fornecedor filtrado → duas seções */
            <>
              {pagedKeysComData.length > 0 && (
                <div className="mb-2">
                  <SectionDivider label="Documentos com Competência" color="#0E8FA3" />
                  {pagedKeysComData.map(key => (
                    <GroupBlock key={key} compKey={key} rows={pagedGrouped.get(key)!} initExpanded={true} />
                  ))}
                </div>
              )}
              {pagedKeysSemData.length > 0 && (
                <div className="mb-2">
                  <SectionDivider label="Sem Competência / Eventuais" color="#6C757D" />
                  {pagedKeysSemData.map(key => (
                    <GroupBlock key={key} compKey={key} rows={pagedGrouped.get(key)!} initExpanded={true} />
                  ))}
                </div>
              )}
            </>
          ) : (
            /* Modo geral: todos os grupos em sequência */
            pagedKeys.map(key => (
              <GroupBlock
                key={key}
                compKey={key}
                rows={pagedGrouped.get(key)!}
                initExpanded={autoExpand}
              />
            ))
          )}
        </>
      )}

      {/* ── VIEW: Lista simples ────────────────────────────────────────── */}
      {viewMode === 'flat' && (
        <div className="bg-white rounded-xl shadow-sm p-4">
          <div className="overflow-x-auto">
            <table className="w-full text-[13px] border-collapse">
              <thead>
                <tr className="bg-[#0E8FA3] text-white">
                  {TABLE_HEADERS.map(h => (
                    <th key={h} className="px-3 py-2.5 text-left font-bold">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {pagedData.map((r, i) => <PendRowItem key={i} r={r} i={i} />)}
                {totalItems === 0 && (
                  <tr>
                    <td colSpan={6} className="px-3 py-6 text-center text-[#999]">Nenhuma pendência encontrada</td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* ── Paginação FUNDO ─────────────────────────────────────────────── */}
      <PaginationBar {...paginationProps} />

    </div>
  )
}
