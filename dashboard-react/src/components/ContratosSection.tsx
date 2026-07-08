import { useState, useMemo } from 'react'
import type { FornContratoItem, ContratoItem } from '../types'
import { exportCSV, exportXLSX } from '../utils/exportUtils'
import jsPDF from 'jspdf'
import autoTable from 'jspdf-autotable'

interface Props {
  data: FornContratoItem[]
  selectedAeroporto?: Set<string>
  selectedStatusTerc?: 'all' | 'Ativo' | 'Inativo'
}

function normalizeAeroporto(code: string): string {
  const c = (code ?? '').toUpperCase().trim()
  return c === 'FLN' ? 'CAIF' : c
}

function fmtDoc(v: string): string {
  const d = v.replace(/\D/g, '')
  if (d.length === 11) return d.replace(/(\d{3})(\d{3})(\d{3})(\d{2})/, '$1.$2.$3-$4')
  if (d.length === 14) return d.replace(/(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})/, '$1.$2.$3/$4-$5')
  return v
}

function StatusBadge({ status }: { status: string }) {
  const isAtivo = status === 'Ativo'
  return (
    <span className={`text-[11px] font-bold px-2 py-0.5 rounded-full ${isAtivo ? 'bg-[#d4edda] text-[#28A745]' : 'bg-[#f0f0f0] text-[#888]'}`}>
      {status || '—'}
    </span>
  )
}

function buildRows(terceiros: ContratoItem['terceiros']) {
  return terceiros.map(t => ({
    'Nome': t.nome,
    'CPF/CNPJ': fmtDoc(t.cpf),
    'Cargo': t.cargo,
    'Aeroporto': t.aeroporto,
    'Status': t.status,
  }))
}

function buildRowsForn(contratos: ContratoItem[]) {
  return contratos.flatMap(c =>
    c.terceiros.map(t => ({
      'Contrato': c.codigo,
      'Aeroporto Contrato': c.aeroporto,
      'Nome': t.nome,
      'CPF/CNPJ': fmtDoc(t.cpf),
      'Cargo': t.cargo,
      'Aeroporto': t.aeroporto,
      'Status': t.status,
    }))
  )
}

function exportPDF(title: string, subtitle: string, terceiros: ContratoItem['terceiros']) {
  const doc = new jsPDF({ orientation: 'landscape', unit: 'mm', format: 'a4' })
  const pageW = doc.internal.pageSize.getWidth()
  doc.setFillColor(10, 106, 122)
  doc.rect(0, 0, pageW, 16, 'F')
  doc.setTextColor(255, 255, 255)
  doc.setFontSize(11)
  doc.setFont('helvetica', 'bold')
  doc.text(title, 10, 10)
  doc.setFont('helvetica', 'normal')
  doc.setFontSize(9)
  doc.text(subtitle, pageW - 10, 10, { align: 'right' })
  autoTable(doc, {
    startY: 20,
    head: [['Nome', 'CPF/CNPJ', 'Cargo', 'Aeroporto', 'Status']],
    body: terceiros.map(t => [t.nome, fmtDoc(t.cpf), t.cargo, t.aeroporto, t.status]),
    styles: { fontSize: 9, cellPadding: 3 },
    headStyles: { fillColor: [14, 143, 163], textColor: 255, fontStyle: 'bold' },
    alternateRowStyles: { fillColor: [240, 248, 250] },
  })
  doc.save(`${title.replace(/[^a-zA-Z0-9]/g, '_')}.pdf`)
}

function exportFornPDF(nome: string, contratos: ContratoItem[]) {
  const totalTerc = contratos.reduce((s, c) => s + c.totalTerceiros, 0)
  const doc = new jsPDF({ orientation: 'landscape', unit: 'mm', format: 'a4' })
  const pageW = doc.internal.pageSize.getWidth()
  doc.setFillColor(10, 106, 122)
  doc.rect(0, 0, pageW, 16, 'F')
  doc.setTextColor(255, 255, 255)
  doc.setFontSize(11)
  doc.setFont('helvetica', 'bold')
  doc.text(`Terceiros — ${nome}`, 10, 10)
  doc.setFont('helvetica', 'normal')
  doc.setFontSize(9)
  doc.text(`${contratos.length} contrato${contratos.length !== 1 ? 's' : ''} · ${totalTerc} terceiro${totalTerc !== 1 ? 's' : ''}`, pageW - 10, 10, { align: 'right' })
  autoTable(doc, {
    startY: 20,
    head: [['Contrato', 'Aeroporto', 'Nome', 'CPF/CNPJ', 'Cargo', 'Status']],
    body: contratos.flatMap(c =>
      c.terceiros.map(t => [c.codigo, c.aeroporto, t.nome, fmtDoc(t.cpf), t.cargo, t.status])
    ),
    styles: { fontSize: 9, cellPadding: 3 },
    headStyles: { fillColor: [14, 143, 163], textColor: 255, fontStyle: 'bold' },
    alternateRowStyles: { fillColor: [240, 248, 250] },
  })
  doc.save(`terceiros_${nome.replace(/[^a-zA-Z0-9]/g, '_')}.pdf`)
}

function ExportBar({ rows, slug, onPDF }: { rows: Record<string, unknown>[]; slug: string; onPDF: () => void }) {
  if (rows.length === 0) return null
  return (
    <div className="flex items-center gap-2">
      <span className="text-[11px] font-bold text-[#888] uppercase tracking-wide">Exportar:</span>
      <button onClick={() => exportXLSX(rows, slug)}
        className="text-[11px] font-bold px-3 py-1.5 rounded bg-[#28A745] text-white hover:bg-[#218838] transition-colors border-0 cursor-pointer">
        Excel
      </button>
      <button onClick={() => exportCSV(rows, slug)}
        className="text-[11px] font-bold px-3 py-1.5 rounded bg-[#6c757d] text-white hover:bg-[#5a6268] transition-colors border-0 cursor-pointer">
        CSV
      </button>
      <button onClick={onPDF}
        className="text-[11px] font-bold px-3 py-1.5 rounded bg-[#DC3545] text-white hover:bg-[#c82333] transition-colors border-0 cursor-pointer">
        ↓ PDF
      </button>
    </div>
  )
}

function Level3({ forn, contrato, onBack, selectedAeroporto = new Set(), selectedStatusTerc = 'all' }: { forn: FornContratoItem; contrato: ContratoItem; onBack: () => void; selectedAeroporto?: Set<string>; selectedStatusTerc?: 'all' | 'Ativo' | 'Inativo' }) {
  let terceirosVisiveis = selectedAeroporto.size > 0
    ? contrato.terceiros.filter(t => selectedAeroporto.has(normalizeAeroporto(t.aeroporto ?? '')))
    : contrato.terceiros
  if (selectedStatusTerc !== 'all')
    terceirosVisiveis = terceirosVisiveis.filter(t => t.status === selectedStatusTerc)
  const rows = buildRows(terceirosVisiveis)
  const slug = `terceiros_${contrato.codigo.replace(/[^a-zA-Z0-9]/g, '_')}`
  return (
    <div>
      <div className="flex items-center justify-between flex-wrap gap-3 mb-4">
        <div className="flex items-center gap-2 flex-wrap">
          <button onClick={onBack}
            className="bg-[#e8f7fa] text-[#0E8FA3] font-bold text-sm px-2.5 py-1 rounded hover:bg-[#d0eff5] border-0 cursor-pointer">
            ← {contrato.codigo}
          </button>
        </div>
        <ExportBar rows={rows} slug={slug}
          onPDF={() => exportPDF(contrato.codigo, forn.nome, terceirosVisiveis)} />
      </div>
      <div className="text-[12px] text-[#888] mb-3">
        {terceirosVisiveis.length} terceiro{terceirosVisiveis.length !== 1 ? 's' : ''} vinculado{terceirosVisiveis.length !== 1 ? 's' : ''}
        {contrato.aeroporto && (
          <span className="ml-2 bg-[#e8f7fa] text-[#0E8FA3] px-2 py-0.5 rounded font-semibold">{contrato.aeroporto}</span>
        )}
      </div>
      {terceirosVisiveis.length === 0 ? (
        <p className="text-[#999] text-[13px] text-center py-8">Nenhum terceiro vinculado a este contrato{selectedAeroporto.size > 0 ? ' para o aeroporto selecionado' : ''}</p>
      ) : (
        <div className="rounded-lg overflow-hidden border border-[#e5eef1]">
          <table className="w-full text-[13px] border-collapse">
            <thead>
              <tr className="bg-[#0E8FA3] text-white">
                <th className="px-3 py-2.5 text-left font-bold">Nome</th>
                <th className="px-3 py-2.5 text-left font-bold">CPF/CNPJ</th>
                <th className="px-3 py-2.5 text-left font-bold">Cargo</th>
                <th className="px-3 py-2.5 text-left font-bold">Aeroporto</th>
                <th className="px-3 py-2.5 text-left font-bold">Status</th>
              </tr>
            </thead>
            <tbody>
              {terceirosVisiveis.map((t, i) => (
                <tr key={i} className={`border-b border-[#e5eef1] hover:bg-[#f0f8fa] ${i % 2 === 1 ? 'bg-[#f8fafb]' : ''}`}>
                  <td className="px-3 py-2 font-medium text-[#222]">{t.nome || '—'}</td>
                  <td className="px-3 py-2 font-mono text-[12px] text-[#555]">{fmtDoc(t.cpf) || '—'}</td>
                  <td className="px-3 py-2 text-[#555]">{t.cargo || '—'}</td>
                  <td className="px-3 py-2 text-[#555]">{t.aeroporto || '—'}</td>
                  <td className="px-3 py-2"><StatusBadge status={t.status} /></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}

function Level2({ forn, onBack, selectedAeroporto = new Set(), selectedStatusTerc = 'all' }: { forn: FornContratoItem; onBack: () => void; selectedAeroporto?: Set<string>; selectedStatusTerc?: 'all' | 'Ativo' | 'Inativo' }) {
  const [selContrato, setSelContrato] = useState<ContratoItem | null>(null)
  const [contratoFilter, setContratoFilter] = useState<Set<string>>(new Set())

  const contratosFiltrados = useMemo(() => {
    let res = contratoFilter.size === 0 ? forn.contratos : forn.contratos.filter(c => contratoFilter.has(c.codigo))
    if (selectedAeroporto.size > 0)
      res = res.filter(c => c.terceiros.some(t => selectedAeroporto.has(normalizeAeroporto(t.aeroporto ?? ''))))
    return res
  }, [forn.contratos, contratoFilter, selectedAeroporto])

  // Versão para export: terceiros filtrados por aeroporto e status
  const contratosParaExport = useMemo(() => {
    return contratosFiltrados.map(c => {
      let tercs = c.terceiros
      if (selectedAeroporto.size > 0)
        tercs = tercs.filter(t => selectedAeroporto.has(normalizeAeroporto(t.aeroporto ?? '')))
      if (selectedStatusTerc !== 'all')
        tercs = tercs.filter(t => t.status === selectedStatusTerc)
      return { ...c, terceiros: tercs, totalTerceiros: tercs.length }
    })
  }, [contratosFiltrados, selectedAeroporto, selectedStatusTerc])

  const fornRows = useMemo(() => buildRowsForn(contratosParaExport), [contratosParaExport])
  const slug = `contratos_${forn.nome.replace(/[^a-zA-Z0-9]/g, '_')}`

  function toggleContrato(cod: string) {
    setContratoFilter(prev => {
      const next = new Set(prev)
      next.has(cod) ? next.delete(cod) : next.add(cod)
      return next
    })
  }

  if (selContrato) {
    return (
      <div>
        <div className="flex items-center gap-2 mb-4 flex-wrap">
          <button onClick={onBack}
            className="bg-[#e8f7fa] text-[#0E8FA3] font-bold text-sm px-2.5 py-1 rounded hover:bg-[#d0eff5] border-0 cursor-pointer">
            ← Fornecedores
          </button>
          <span className="text-[#bbb] text-lg">›</span>
          <button onClick={() => setSelContrato(null)}
            className="bg-[#e8f7fa] text-[#0E8FA3] font-bold text-sm px-2.5 py-1 rounded hover:bg-[#d0eff5] border-0 cursor-pointer">
            {forn.nome}
          </button>
          <span className="text-[#bbb] text-lg">›</span>
          <span className="font-bold text-sm text-[#333]">{selContrato.codigo}</span>
        </div>
        <Level3 forn={forn} contrato={selContrato} onBack={() => setSelContrato(null)} selectedAeroporto={selectedAeroporto} selectedStatusTerc={selectedStatusTerc} />
      </div>
    )
  }

  return (
    <div>
      <div className="flex items-center justify-between flex-wrap gap-3 mb-3">
        <div className="flex items-center gap-2 flex-wrap">
          <button onClick={onBack}
            className="bg-[#e8f7fa] text-[#0E8FA3] font-bold text-sm px-2.5 py-1 rounded hover:bg-[#d0eff5] border-0 cursor-pointer">
            ← Fornecedores
          </button>
          <span className="text-[#bbb] text-lg">›</span>
          <span className="font-bold text-sm text-[#333]">{forn.nome}</span>
        </div>
        <ExportBar rows={fornRows} slug={slug} onPDF={() => exportFornPDF(forn.nome, contratosParaExport)} />
      </div>

      <div className="text-[12px] text-[#888] mb-3">
        {forn.totalContratos} contrato{forn.totalContratos !== 1 ? 's' : ''} · {forn.totalTerceiros} terceiro{forn.totalTerceiros !== 1 ? 's' : ''}
      </div>

      {/* Filtro por contrato — aparece sempre que houver mais de 1 contrato */}
      {forn.contratos.length > 1 && (
        <div className="flex gap-2 flex-wrap mb-4 items-center">
          <span className="text-[11px] text-[#888] font-semibold">Filtrar:</span>
          {forn.contratos.map(c => {
            const ativo = contratoFilter.has(c.codigo)
            return (
              <button key={c.codigo} onClick={() => toggleContrato(c.codigo)}
                className={`text-[11px] font-bold px-2.5 py-1 rounded-full border transition-colors cursor-pointer ${
                  ativo
                    ? 'bg-[#0E8FA3] text-white border-[#0E8FA3]'
                    : 'bg-white text-[#0E8FA3] border-[#0E8FA3] hover:bg-[#e8f7fa]'
                }`}>
                {c.codigo}
                {c.aeroporto && <span className="ml-1 opacity-70">({c.aeroporto})</span>}
              </button>
            )
          })}
          {contratoFilter.size > 0 && (
            <button onClick={() => setContratoFilter(new Set())}
              className="text-[11px] text-[#888] hover:text-[#333] cursor-pointer border-0 bg-transparent underline">
              Limpar
            </button>
          )}
        </div>
      )}

      <div className="flex flex-col gap-2">
        {contratosFiltrados.map(c => (
          <div key={c.codigo} onClick={() => setSelContrato(c)}
            className="flex items-center gap-4 px-4 py-3 cursor-pointer rounded-lg border border-[#e5eef1] hover:border-[#0E8FA3] hover:bg-[#f0f8fa] transition-all select-none">
            <div className="flex-1">
              <div className="font-bold text-sm text-[#222]">{c.codigo}</div>
              {c.aeroporto && (
                <div className="mt-0.5">
                  <span className="text-[11px] bg-[#e8f7fa] text-[#0E8FA3] px-2 py-0.5 rounded font-semibold">{c.aeroporto}</span>
                </div>
              )}
            </div>
            <div className="text-[13px] text-[#666] whitespace-nowrap">
              {c.totalTerceiros > 0
                ? `${c.totalTerceiros} terceiro${c.totalTerceiros !== 1 ? 's' : ''}`
                : <span className="text-[#bbb] italic">sem terceiros</span>
              }
            </div>
            <span className="text-2xl text-[#bbb] font-light">›</span>
          </div>
        ))}
      </div>
    </div>
  )
}

export function ContratosSection({ data, selectedAeroporto = new Set(), selectedStatusTerc = 'all' }: Props) {
  const [selForn, setSelForn] = useState<FornContratoItem | null>(null)
  const [busca, setBusca] = useState('')
  const [buscaCont, setBuscaCont] = useState('')

  const dataFiltrada = useMemo(() => {
    const q = busca.trim().toLowerCase()
    const qc = buscaCont.trim().toLowerCase()
    let res = data
    if (q) {
      const qDigits = q.replace(/\D/g, '')
      res = res.filter(f =>
        f.nome.toLowerCase().includes(q) ||
        (qDigits && f.cnpj && f.cnpj.includes(qDigits))
      )
    }
    if (qc) {
      res = res.filter(f =>
        f.contratos.some(c => c.codigo.toLowerCase().includes(qc))
      )
    }
    return res
  }, [data, busca, buscaCont])

  function clearAll() { setBusca(''); setBuscaCont('') }

  if (selForn) {
    return (
      <div className="bg-white rounded-xl shadow-sm p-5">
        <Level2 forn={selForn} onBack={() => setSelForn(null)} selectedAeroporto={selectedAeroporto} selectedStatusTerc={selectedStatusTerc} />
      </div>
    )
  }

  return (
    <div className="bg-white rounded-xl shadow-sm p-5">
      <p className="text-[13px] text-[#666] mb-3">
        Clique num fornecedor para ver os contratos. Clique num contrato para ver os terceiros vinculados.
      </p>
      <div className="flex items-end gap-3 mb-4 flex-wrap">
        <div className="flex flex-col gap-1">
          <label className="text-[11px] font-bold text-[#0E8FA3] uppercase tracking-wide">Buscar Fornecedor</label>
          <input
            type="text"
            value={busca}
            onChange={e => setBusca(e.target.value)}
            placeholder="Nome ou CNPJ..."
            className="border border-[#cde] rounded-lg px-3 py-1.5 text-[13px] text-[#333] outline-none focus:border-[#0E8FA3] w-56"
          />
        </div>
        <div className="flex flex-col gap-1">
          <label className="text-[11px] font-bold text-[#0E8FA3] uppercase tracking-wide">Buscar Contrato</label>
          <input
            type="text"
            value={buscaCont}
            onChange={e => setBuscaCont(e.target.value)}
            placeholder="Código do contrato..."
            className="border border-[#cde] rounded-lg px-3 py-1.5 text-[13px] text-[#333] outline-none focus:border-[#0E8FA3] w-56"
          />
        </div>
        <button onClick={clearAll}
          className="bg-[#0E8FA3] text-white font-bold text-[13px] px-4 py-1.5 rounded-lg hover:bg-[#0a7a8d] border-0 cursor-pointer h-[34px]">
          Limpar
        </button>
        <span className="text-[12px] text-[#999] self-center">
          {dataFiltrada.length} fornecedor{dataFiltrada.length !== 1 ? 'es' : ''}
        </span>
      </div>

      <div className="grid gap-3" style={{ gridTemplateColumns: 'repeat(auto-fill, minmax(220px, 1fr))' }}>
        {dataFiltrada.map(f => (
          <div key={f.cnpj} onClick={() => setSelForn(f)}
            className="bg-[#f8f9fa] rounded-xl p-4 cursor-pointer border-2 border-[#e0e0e0] hover:border-[#0E8FA3] hover:shadow-md hover:-translate-y-0.5 transition-all select-none">
            <div className="text-[28px] font-black leading-none text-[#0E8FA3]">
              {f.totalContratos}
            </div>
            <div className="text-[10px] text-[#888] font-semibold uppercase mt-0.5">
              contrato{f.totalContratos !== 1 ? 's' : ''}
            </div>
            <div className="text-[12px] font-bold text-[#333] mt-1.5 leading-snug min-h-[32px]">{f.nome}</div>
            {f.cnpj && <div className="text-[11px] text-[#999] font-mono mt-0.5">{fmtDoc(f.cnpj)}</div>}
            <div className="text-[11px] text-[#888] mt-1">
              {f.totalTerceiros > 0
                ? `${f.totalTerceiros} terceiro${f.totalTerceiros !== 1 ? 's' : ''} vinculado${f.totalTerceiros !== 1 ? 's' : ''}`
                : <span className="italic">sem terceiros vinculados</span>
              }
            </div>
            <div className="mt-2.5 flex gap-1 flex-wrap">
              {f.contratos.slice(0, 3).map(c => (
                <span key={c.codigo}
                  className="text-[10px] bg-[#e8f7fa] text-[#0E8FA3] px-1.5 py-0.5 rounded font-medium truncate max-w-[120px]"
                  title={c.codigo}>
                  {c.codigo}
                </span>
              ))}
              {f.contratos.length > 3 && (
                <span className="text-[10px] text-[#aaa]">+{f.contratos.length - 3}</span>
              )}
            </div>
          </div>
        ))}
        {dataFiltrada.length === 0 && (
          <p className="text-[#999] text-[13px] text-center py-6 col-span-full">
            {busca || buscaCont ? 'Nenhum fornecedor encontrado para os filtros aplicados' : 'Nenhum dado disponível'}
          </p>
        )}
      </div>
    </div>
  )
}
