import * as XLSX from 'xlsx'
import jsPDF from 'jspdf'
import autoTable from 'jspdf-autotable'
import type { SitTerceiroRow, FornSitRow, PendRow } from '../types'

// ── CSV / XLSX ─────────────────────────────────────────────────────────────

export function exportCSV(rows: Record<string, unknown>[], filename: string) {
  const headers = rows.length ? Object.keys(rows[0]) : []
  downloadCSV(rows, headers, `${filename}.csv`)
}

export function exportXLSX(rows: Record<string, unknown>[], filename: string) {
  const headers = rows.length ? Object.keys(rows[0]) : []
  downloadXLSX(rows, headers, `${filename}.xlsx`)
}

export function downloadCSV(rows: Record<string, unknown>[], headers: string[], filename: string) {
  const escape = (v: unknown) => {
    const s = String(v ?? '')
    return s.includes(',') || s.includes('"') || s.includes('\n')
      ? '"' + s.replace(/"/g, '""') + '"'
      : s
  }
  const lines = [
    headers.join(','),
    ...rows.map(r => headers.map(h => escape(r[h])).join(',')),
  ]
  const blob = new Blob([lines.join('\n')], { type: 'text/csv;charset=utf-8;' })
  triggerDownload(blob, filename)
}

export function downloadXLSX(rows: Record<string, unknown>[], headers: string[], filename: string) {
  const wsData = [headers, ...rows.map(r => headers.map(h => r[h] ?? ''))]
  const wb = XLSX.utils.book_new()
  const ws = XLSX.utils.aoa_to_sheet(wsData)
  ws['!cols'] = headers.map(() => ({ wch: 22 }))
  XLSX.utils.book_append_sheet(wb, ws, 'Dados')
  XLSX.writeFile(wb, filename)
}

// ── PDF com jsPDF AutoTable (gera tabela limpa, sem screenshot) ────────────

const TEAL        = [14, 143, 163] as [number, number, number]
const TEAL_DARK   = [10, 106, 122] as [number, number, number]
const TEAL_LIGHT  = [212, 238, 243] as [number, number, number]
const WHITE       = [255, 255, 255] as [number, number, number]
const TEXT_DARK   = [26, 42, 53] as [number, number, number]
const GRAY_LIGHT  = [240, 248, 250] as [number, number, number]

interface KPIBadge {
  label: string
  value: string
  color?: 'green' | 'red' | 'orange' | 'yellow' | 'default'
}

function addPDFHeader(doc: jsPDF, title: string, subtitle: string, geradoEm: string) {
  const pageW = doc.internal.pageSize.getWidth()

  // Barra de cabeçalho
  doc.setFillColor(...TEAL_DARK)
  doc.rect(0, 0, pageW, 16, 'F')

  // Logo-like text "efcaz"
  doc.setFontSize(11)
  doc.setFont('helvetica', 'bold')
  doc.setTextColor(...WHITE)
  doc.text('EFCAZ', 10, 10)

  // Título do relatório
  doc.setFontSize(10)
  doc.setFont('helvetica', 'normal')
  doc.text(title, pageW / 2, 10, { align: 'center' })

  // Data de geração
  doc.setFontSize(8)
  doc.text(`Emitido em: ${geradoEm}`, pageW - 10, 10, { align: 'right' })

  // Subtítulo
  doc.setFontSize(9)
  doc.setFont('helvetica', 'bold')
  doc.setTextColor(...TEAL)
  doc.text(subtitle, 10, 22)

  doc.setTextColor(...TEXT_DARK)
}

function addFooters(doc: jsPDF) {
  const total  = doc.getNumberOfPages()
  const pageW  = doc.internal.pageSize.getWidth()
  const pageH  = doc.internal.pageSize.getHeight()
  for (let i = 1; i <= total; i++) {
    doc.setPage(i)
    doc.setFontSize(7)
    doc.setFont('helvetica', 'normal')
    doc.setTextColor(150, 150, 150)
    doc.text(
      `Efcaz — Relatório Confidencial  ·  Página ${i} de ${total}`,
      pageW / 2, pageH - 5, { align: 'center' }
    )
  }
  doc.setTextColor(...TEXT_DARK)
}

function addKPIRow(doc: jsPDF, kpis: KPIBadge[], yStart: number): number {
  const pageW = doc.internal.pageSize.getWidth()
  const colW = (pageW - 20) / kpis.length
  const cardH = 14
  const y = yStart

  kpis.forEach((kpi, i) => {
    const x = 10 + i * colW
    const colorMap: Record<string, [number, number, number]> = {
      green:  [212, 237, 218],
      red:    [255, 234, 234],
      orange: [255, 236, 218],
      yellow: [255, 243, 205],
      default: TEAL_LIGHT,
    }
    const textColorMap: Record<string, [number, number, number]> = {
      green:  [40, 167, 69],
      red:    [220, 53, 69],
      orange: [244, 121, 59],
      yellow: [160, 120, 0],
      default: TEAL,
    }
    const bgColor = colorMap[kpi.color ?? 'default']
    const txtColor = textColorMap[kpi.color ?? 'default']

    doc.setFillColor(...bgColor)
    doc.roundedRect(x, y, colW - 2, cardH, 1.5, 1.5, 'F')

    // Borda topo colorida
    doc.setFillColor(...txtColor)
    doc.rect(x, y, colW - 2, 1.2, 'F')

    // Valor
    doc.setFontSize(11)
    doc.setFont('helvetica', 'bold')
    doc.setTextColor(...txtColor)
    doc.text(String(kpi.value), x + (colW - 2) / 2, y + 6.5, { align: 'center' })

    // Label
    doc.setFontSize(6)
    doc.setFont('helvetica', 'normal')
    doc.setTextColor(100, 100, 100)
    const labelLines = doc.splitTextToSize(kpi.label, colW - 4)
    doc.text(labelLines, x + (colW - 2) / 2, y + 10.5, { align: 'center' })
  })

  doc.setTextColor(...TEXT_DARK)
  return y + cardH + 4
}

// ── Relatório R4 — Situação da Empresa ─────────────────────────────────────

interface R4PDFOptions {
  rows: { Fornecedor: string; Documento: string; Status: string; Vencimento: string }[]
  kpis: { pct_nc: number; pct_c: number; aprovado: number; reprovado: number; nao_anex: number; em_analise: number; vencido: number; total: number; forn: number }
  geradoEm: string
  filename?: string
}

export function exportR4PDF({ rows, kpis, geradoEm, filename = 'situacao_empresa' }: R4PDFOptions) {
  const doc = new jsPDF({ orientation: 'landscape', unit: 'mm', format: 'a4' })

  addPDFHeader(doc, 'Relatório de Conformidade — Documentação Corporativa', 'Situação Documental da Empresa (R4)', geradoEm)

  const yAfterKpis = addKPIRow(doc, [
    { label: '% Não Conf.', value: `${kpis.pct_nc}%`, color: 'red' },
    { label: '% Conforme', value: `${kpis.pct_c}%`, color: 'green' },
    { label: 'Aprovados', value: String(kpis.aprovado), color: 'green' },
    { label: 'Reprovados', value: String(kpis.reprovado), color: 'red' },
    { label: 'Não Anexados', value: String(kpis.nao_anex), color: 'yellow' },
    { label: 'Em Análise', value: String(kpis.em_analise), color: 'orange' },
    { label: 'Vencidos', value: String(kpis.vencido), color: 'red' },
    { label: 'Total Docs', value: String(kpis.total) },
    { label: 'Fornec. c/ Docs', value: String(kpis.forn) },
  ], 26)

  const statusColor = (s: string): [number, number, number] => {
    if (s === 'Aprovado')      return [40, 167, 69]
    if (s === 'Regular')       return [21, 115, 71]   // busca auto OK
    if (s === 'Reprovado')     return [220, 53, 69]
    if (s === 'Irregular')     return [176, 92, 0]    // débito detectado
    if (s === 'Não Analisado') return [108, 117, 125] // aguardando BPO
    if (s === 'Não Anexado')   return [160, 120, 0]
    if (s === 'Em análise')    return [14, 143, 163]
    if (s === 'Vencido')       return [220, 53, 69]
    return [100, 100, 100]
  }

  autoTable(doc, {
    startY: yAfterKpis,
    head: [['Fornecedor', 'Documento', 'Status', 'Vencimento']],
    body: rows.map(r => [r.Fornecedor, r.Documento, r.Status, r.Vencimento || '—']),
    styles: { fontSize: 8, cellPadding: 2.5, textColor: TEXT_DARK, font: 'helvetica' },
    headStyles: { fillColor: TEAL, textColor: WHITE, fontStyle: 'bold', fontSize: 8.5 },
    alternateRowStyles: { fillColor: GRAY_LIGHT },
    columnStyles: {
      0: { cellWidth: 60 },
      1: { cellWidth: 'auto' },
      2: { cellWidth: 28 },
      3: { cellWidth: 24 },
    },
    didParseCell(data) {
      if (data.section === 'body' && data.column.index === 2) {
        data.cell.styles.textColor = statusColor(String(data.cell.raw))
        data.cell.styles.fontStyle = 'bold'
      }
    },
    margin: { left: 10, right: 10 },
    showHead: 'everyPage',
  })

  addFooters(doc)
  doc.save(`${filename}.pdf`)
}

// ── Relatório R3 — Situação de Terceiros ───────────────────────────────────

interface R3PDFOptions {
  rows: { Fornecedor: string; Aeroporto: string; Terceiro: string; CNPJ_Terceiro: string; Documento: string; Competencia: string; Status: string; Vencimento: string }[]
  geradoEm: string
  filename?: string
}

export function exportR3PDF({ rows, geradoEm, filename = 'situacao_terceiros' }: R3PDFOptions) {
  const doc = new jsPDF({ orientation: 'landscape', unit: 'mm', format: 'a4' })

  addPDFHeader(doc, 'Relatório de Conformidade — Terceiros', 'Situação Documental por Terceiro (R3)', geradoEm)

  const total    = rows.length
  const aprov    = rows.filter(r => r.Status === 'Aprovado').length
  const reprov   = rows.filter(r => r.Status === 'Reprovado').length
  const naoAnex  = rows.filter(r => r.Status === 'Não anexado').length
  const aguard   = rows.filter(r => r.Status === 'Aguardando Submissão').length
  const emAnal   = rows.filter(r => r.Status === 'Em Análise').length
  const pctC     = total > 0 ? (aprov / total * 100).toFixed(1) : '0.0'
  const pctNC    = total > 0 ? ((total - aprov) / total * 100).toFixed(1) : '0.0'

  const yAfterKpis = addKPIRow(doc, [
    { label: '% Não Conf.', value: `${pctNC}%`, color: 'red' },
    { label: '% Conforme', value: `${pctC}%`, color: 'green' },
    { label: 'Aprovados', value: String(aprov), color: 'green' },
    { label: 'Reprovados', value: String(reprov), color: 'red' },
    { label: 'Não Anexados', value: String(naoAnex), color: 'yellow' },
    { label: 'Aguard. Submissão', value: String(aguard), color: 'orange' },
    { label: 'Em Análise', value: String(emAnal), color: 'orange' },
    { label: 'Total Docs', value: String(total) },
  ], 26)

  const statusColor = (s: string): [number, number, number] => {
    if (s === 'Aprovado')              return [40, 167, 69]
    if (s === 'Reprovado')             return [220, 53, 69]
    if (s === 'Não anexado')           return [160, 120, 0]
    if (s === 'Aguardando Submissão')  return [244, 121, 59]
    if (s === 'Em Análise')            return [14, 143, 163]
    return [100, 100, 100]
  }

  autoTable(doc, {
    startY: yAfterKpis,
    head: [['Fornecedor', 'Aeroporto', 'Terceiro', 'CNPJ Terceiro', 'Documento', 'Status', 'Competência', 'Vencimento']],
    body: rows.map(r => [r.Fornecedor, r.Aeroporto || '—', r.Terceiro, r.CNPJ_Terceiro || '—', r.Documento, r.Status, r.Competencia || '—', r.Vencimento || '—']),
    styles: { fontSize: 7.5, cellPadding: 2, textColor: TEXT_DARK, font: 'helvetica' },
    headStyles: { fillColor: TEAL, textColor: WHITE, fontStyle: 'bold', fontSize: 8 },
    alternateRowStyles: { fillColor: GRAY_LIGHT },
    columnStyles: {
      0: { cellWidth: 40 },
      1: { cellWidth: 18 },
      2: { cellWidth: 40 },
      3: { cellWidth: 24 },
      4: { cellWidth: 'auto' },
      5: { cellWidth: 28 },
      6: { cellWidth: 26 },
      7: { cellWidth: 20 },
    },
    didParseCell(data) {
      if (data.section === 'body' && data.column.index === 5) {
        data.cell.styles.textColor = statusColor(String(data.cell.raw))
        data.cell.styles.fontStyle = 'bold'
      }
    },
    margin: { left: 10, right: 10 },
    showHead: 'everyPage',
  })

  addFooters(doc)
  doc.save(`${filename}.pdf`)
}

// ── Relatório de Pendências ────────────────────────────────────────────────

interface PendPDFOptions {
  rows: { Fornecedor: string; Area: string; Documento: string; Competencia: string; Detalhe: string }[]
  geradoEm: string
  filename?: string
}

export function exportPendPDF({ rows, geradoEm, filename = 'pendencias' }: PendPDFOptions) {
  const doc = new jsPDF({ orientation: 'landscape', unit: 'mm', format: 'a4' })

  addPDFHeader(doc, 'Relatório de Pendências', 'Detalhamento das Pendências por Fornecedor', geradoEm)

  const total     = rows.length
  const terceiros = rows.filter(r => r.Area === 'TERCEIROS').length
  const docs      = rows.filter(r => r.Area === 'DOCUMENTOS').length

  const yAfterKpis = addKPIRow(doc, [
    { label: 'Total Pendências', value: String(total) },
    { label: 'Área Terceiros',   value: String(terceiros) },
    { label: 'Área Documentos',  value: String(docs) },
  ], 26)

  autoTable(doc, {
    startY: yAfterKpis,
    head: [['Fornecedor', 'Área', 'Documento', 'Competência', 'Detalhe da Pendência']],
    body: rows.map(r => [
      r.Fornecedor,
      r.Area === 'TERCEIROS' ? 'Terceiros' : 'Fornecedor',
      r.Documento,
      r.Competencia || '—',
      r.Detalhe || '—',
    ]),
    styles: { fontSize: 7.5, cellPadding: 2.5, textColor: TEXT_DARK, font: 'helvetica' },
    headStyles: { fillColor: TEAL, textColor: WHITE, fontStyle: 'bold', fontSize: 8 },
    alternateRowStyles: { fillColor: GRAY_LIGHT },
    columnStyles: {
      0: { cellWidth: 50 },
      1: { cellWidth: 22 },
      2: { cellWidth: 45 },
      3: { cellWidth: 25 },
      4: { cellWidth: 'auto' },
    },
    margin: { left: 10, right: 10 },
    showHead: 'everyPage',
  })

  addFooters(doc)
  doc.save(`${filename}.pdf`)
}

// ── Exportação Global (R3 + R4 + Pendências) ─────────────────────────────

export function exportRelatorioXLSX(
  sitRows: SitTerceiroRow[],
  fornSitRows: FornSitRow[],
  pendRows: PendRow[],
  filename = 'relatorio_zurich',
) {
  const wb = XLSX.utils.book_new()

  const hdR3 = ['Fornecedor', 'Terceiro', 'Documento', 'Competencia', 'Status', 'Vencimento']
  const wsR3 = XLSX.utils.aoa_to_sheet([hdR3, ...sitRows.map(r => hdR3.map(h => (r as any)[h] ?? ''))])
  wsR3['!cols'] = hdR3.map(() => ({ wch: 22 }))
  XLSX.utils.book_append_sheet(wb, wsR3, 'R3 - Terceiros')

  const hdR4 = ['Fornecedor', 'Documento', 'Competencia', 'Status', 'Vencimento']
  const wsR4 = XLSX.utils.aoa_to_sheet([hdR4, ...fornSitRows.map(r => hdR4.map(h => (r as any)[h] ?? ''))])
  wsR4['!cols'] = hdR4.map(() => ({ wch: 22 }))
  XLSX.utils.book_append_sheet(wb, wsR4, 'R4 - Empresa')

  const hdPend = ['Fornecedor', 'Area', 'Documento', 'Competencia', 'Detalhe']
  const wsPend = XLSX.utils.aoa_to_sheet([hdPend, ...pendRows.map(r => hdPend.map(h => (r as any)[h] ?? ''))])
  wsPend['!cols'] = hdPend.map(() => ({ wch: 22 }))
  XLSX.utils.book_append_sheet(wb, wsPend, 'Pendencias')

  XLSX.writeFile(wb, `${filename}.xlsx`)
}

export function exportRelatorioPDF(
  sitRows: SitTerceiroRow[],
  fornSitRows: FornSitRow[],
  pendRows: PendRow[],
  geradoEm: string,
  filename = 'relatorio_zurich',
) {
  const doc = new jsPDF({ orientation: 'landscape', unit: 'mm', format: 'a4' })
  const pageW = doc.internal.pageSize.getWidth()
  let y = 0

  const drawSection = (title: string) => {
    if (y > 170) { doc.addPage(); y = 0 }
    doc.setFillColor(...TEAL_DARK)
    doc.rect(0, y, pageW, 12, 'F')
    doc.setFontSize(10); doc.setFont('helvetica', 'bold'); doc.setTextColor(...WHITE)
    doc.text('EFCAZ', 10, y + 8)
    doc.text(title, pageW / 2, y + 8, { align: 'center' })
    doc.setFontSize(7); doc.setFont('helvetica', 'normal')
    doc.text(geradoEm, pageW - 10, y + 8, { align: 'right' })
    doc.setTextColor(...TEXT_DARK)
    y += 16
  }

  drawSection('R3 — Situação Documental por Terceiro')
  autoTable(doc, {
    startY: y,
    head: [['Fornecedor', 'Terceiro', 'Documento', 'Competência', 'Status', 'Vencimento']],
    body: sitRows.map(r => [r.Fornecedor, r.Terceiro, r.Documento, r.Competencia || '—', r.Status, r.Vencimento || '—']),
    styles: { fontSize: 7, cellPadding: 2, font: 'helvetica' },
    headStyles: { fillColor: TEAL, textColor: WHITE, fontStyle: 'bold' },
    alternateRowStyles: { fillColor: GRAY_LIGHT },
    margin: { left: 10, right: 10 },
    showHead: 'everyPage',
  })
  y = (doc as any).lastAutoTable.finalY + 10

  drawSection('R4 — Situação Documental da Empresa')
  autoTable(doc, {
    startY: y,
    head: [['Fornecedor', 'Documento', 'Competência', 'Status', 'Vencimento']],
    body: fornSitRows.map(r => [r.Fornecedor, r.Documento, r.Competencia || '—', r.Status, r.Vencimento || '—']),
    styles: { fontSize: 7, cellPadding: 2, font: 'helvetica' },
    headStyles: { fillColor: TEAL, textColor: WHITE, fontStyle: 'bold' },
    alternateRowStyles: { fillColor: GRAY_LIGHT },
    margin: { left: 10, right: 10 },
    showHead: 'everyPage',
  })
  y = (doc as any).lastAutoTable.finalY + 10

  drawSection('Pendências')
  autoTable(doc, {
    startY: y,
    head: [['Fornecedor', 'Área', 'Documento', 'Competência', 'Detalhe']],
    body: pendRows.map(r => [r.Fornecedor, r.Area === 'TERCEIROS' ? 'Terceiros' : 'Fornecedor', r.Documento, r.Competencia || '—', r.Detalhe || '—']),
    styles: { fontSize: 7, cellPadding: 2, font: 'helvetica' },
    headStyles: { fillColor: TEAL, textColor: WHITE, fontStyle: 'bold' },
    alternateRowStyles: { fillColor: GRAY_LIGHT },
    margin: { left: 10, right: 10 },
    showHead: 'everyPage',
  })

  addFooters(doc)
  doc.save(`${filename}.pdf`)
}

export function exportRelatorioCSV(
  sitRows: SitTerceiroRow[],
  fornSitRows: FornSitRow[],
  pendRows: PendRow[],
  filename = 'relatorio_zurich',
) {
  const escape = (v: unknown) => {
    const s = String(v ?? '')
    return s.includes(',') || s.includes('"') || s.includes('\n') ? '"' + s.replace(/"/g, '""') + '"' : s
  }
  const hd = ['Secao', 'Fornecedor', 'Terceiro', 'Documento', 'Competencia', 'Status', 'Vencimento']
  const lines = [
    hd.join(','),
    ...sitRows.map(r => [
      'R3-Terceiros', r.Fornecedor, r.Terceiro || '', r.Documento, r.Competencia || '', r.Status, r.Vencimento || '',
    ].map(escape).join(',')),
    ...fornSitRows.map(r => [
      'R4-Empresa', r.Fornecedor, '', r.Documento, r.Competencia || '', r.Status, r.Vencimento || '',
    ].map(escape).join(',')),
    ...pendRows.map(r => [
      'Pendencias', r.Fornecedor, '', r.Documento, r.Competencia || '', r.Status || r.Area || '', r.Detalhe || '',
    ].map(escape).join(',')),
  ]
  const blob = new Blob([lines.join('\n')], { type: 'text/csv;charset=utf-8;' })
  triggerDownload(blob, `${filename}.csv`)
}

// ── Utilitários ───────────────────────────────────────────────────────────

function triggerDownload(blob: Blob, filename: string) {
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  a.click()
  URL.revokeObjectURL(url)
}
