import type {
  PendRow, SitTerceiroRow, FornSitRow, TercKPIRow, SemExecRow,
  BarEntry, ConfEmpEntry, StatusEmpEntry, AreaEmpEntry, TrabEmpEntry,
  DrillDoc, DashboardData, StatusR3, StatusR4,
  TerceiroContratoItem, ContratoItem, FornContratoItem,
} from '../types'

function stripContratos(rows: Record<string, string>[]): Record<string, string>[] {
  if (!rows.length) return rows
  const contractCols = Object.keys(rows[0]).filter(k => /^contrato\b/i.test(k.trim()))
  if (!contractCols.length) return rows
  return rows.map(row => {
    const clean = { ...row }
    contractCols.forEach(c => delete clean[c])
    return clean
  })
}

const MONTHS_PT = ['Janeiro','Fevereiro','Março','Abril','Maio','Junho','Julho','Agosto','Setembro','Outubro','Novembro','Dezembro']

// Normaliza qualquer formato de competência para "MM/YY - Mês AAAA"
// Aceita: "01/2026", "01/26", "01/26 - Janeiro 2026" (já no formato correto)
function normalizeCompetencia(comp: string): string {
  const s = (comp ?? '').trim()
  if (!s || s === 'nan' || s === 'A classificar' || s === 'Não possui competência') return s
  // Já está no formato longo — retorna como está
  if (/^\d{2}\/\d{2}\s*-\s*.+\d{4}/.test(s)) return s
  // MM/AAAA ou MM/AA
  const m = s.match(/^(0[1-9]|1[0-2])\/(20\d{2}|\d{2})$/)
  if (m) {
    const mm = m[1]
    const rawY = m[2]
    const yyyy = rawY.length === 4 ? parseInt(rawY) : 2000 + parseInt(rawY)
    const yy = String(yyyy).slice(2)
    return `${mm}/${yy} - ${MONTHS_PT[parseInt(mm, 10) - 1]} ${yyyy}`
  }
  return s
}

export function abbrev(name: string, n = 40): string {
  const s = String(name || '').trim()
  const short = s.replace(/\s+(LTDA|LTDA\.|S\/A|SA|EIRELI|ME|EPP).*/i, '')
  return short.length > n ? short.slice(0, n) + '...' : short
}

function findCol(cols: string[], ...terms: string[]): string | null {
  return cols.find(c => terms.every(t => c.toLowerCase().includes(t.toLowerCase()))) ?? null
}

function fmtDate(v: unknown): string {
  const s = String(v ?? '').trim()
  if (!s || s === 'nan' || s === 'None') return ''
  const d = new Date(s)
  return isNaN(d.getTime()) ? s : d.toLocaleDateString('pt-BR')
}

function extractDoc(row: Record<string, string>, area = ''): string {
  const doc = String(row['Documento'] ?? '').trim()
  if (doc && doc !== 'nan') return doc.toUpperCase().slice(0, 80)
  const pend = String(row['Pendencia'] || row['Pendência'] || '')
  // Apenas a primeira linha contém o nome do documento; o restante é descrição
  const firstLine = pend.split(/\r?\n/)[0].trim()
  if (area === 'TERCEIROS') {
    // Formato: "NOME TERCEIRO - NOME DOCUMENTO, descrição..." ou "... - NOME DOC. descrição..."
    const dashIdx = firstLine.indexOf(' - ')
    if (dashIdx >= 0) {
      const afterDash = firstLine.slice(dashIdx + 3)
      // Separador pode ser vírgula ou ponto (ambos são usados na base)
      const m = afterDash.match(/^([^,.]+)/)
      if (m) return m[1].trim().toUpperCase().slice(0, 80)
      return afterDash.trim().toUpperCase().slice(0, 80)
    }
    return firstLine.toUpperCase().slice(0, 80) || 'OUTROS'
  }
  // DOCUMENTOS: formato "NOME DOC, descrição..." (o nome pode conter " - ", ex: "GRRF - GUIA DO FGTS")
  const commaIdx = firstLine.indexOf(',')
  return (commaIdx >= 0 ? firstLine.slice(0, commaIdx) : firstLine).trim().toUpperCase().slice(0, 80) || 'OUTROS'
}

function normCNPJ(v: unknown): string {
  const s = String(v ?? '').trim()
  if (!s || s === 'nan' || s === 'None' || s === '0') return ''
  // Remover ".0" do formato pandas ANTES de processar (ex: "20845454000170.0")
  const withoutFloat = s.endsWith('.0') ? s.slice(0, -2) : s
  const digits = withoutFloat.replace(/[.\-/]/g, '')
  if (/^\d+$/.test(digits)) {
    if (digits.length <= 11) return digits        // CPF — não padeia para tamanho de CNPJ
    return digits.padStart(14, '0')              // CNPJ — normaliza para 14 dígitos
  }
  return withoutFloat
}

// Normaliza qualquer variante de código de aeroporto para CAIF/VIX/MEA/CAIN (ou '')
// Espelha _norm_aero() do relatorio_fornecedores_zurich.py
export function normAeroporto(raw: string): string {
  const s = (raw ?? '').toUpperCase().trim().replace(/^nan$/i, '').replace(/^none$/i, '')
  if (!s || s === '000') return ''
  const ALIASES: Record<string, string> = { FLN: 'CAIF', NAT: 'CAIN' }
  const CODES = ['CAIF', 'VIX', 'MEA', 'CAIN']
  if (ALIASES[s]) return ALIASES[s]
  for (const code of CODES)
    if (s === code || s.startsWith(code + ' ') || s.startsWith(code + '-') || s.startsWith(code + '_')) return code
  for (const code of CODES)
    if (s.includes(code)) return code
  if (s.includes('FLORIAN')) return 'CAIF'
  if (/VIT.?RIA/.test(s)) return 'VIX'
  if (s.includes('EURICO') || s.includes('AGUIAR')) return 'VIX'
  if (s.includes('MACA')) return 'MEA'
  if (s.includes('BENEDITO') && s.includes('LACERDA')) return 'MEA'
  if (s.includes('NATAL')) return 'CAIN'
  return ''
}

// ── R3: Lógica do relatorio_fornecedores_zurich.py ───────────────────────────
// Prioridade 1: "Situação Análise Documento" (APROVADO / REPROVADO)
// Prioridade 2: Status do documento
//   "Não anexado" → "Não anexado"
//   "A vencer" | "Vencido" | N/A → "Aguardando análise"
// Depois split "Aguardando análise" por "Situação última solicitação":
//   EM_ELABORACAO → "Aguardando Submissão"
//   else → "Em Análise"
function mapStatusR3(
  row: Record<string, string>,
  colAnalise: string | null,
  colSitSolic: string | null
): StatusR3 | null {
  if (colAnalise) {
    const analise = String(row[colAnalise] ?? '').trim().toUpperCase()
    if (analise === 'APROVADO') return 'Aprovado'
    if (analise === 'REPROVADO') return 'Reprovado'
  }
  const rawStatus = String(row['Status'] ?? '').trim()
  const isNA = !rawStatus || rawStatus.toUpperCase() === 'N/A' || rawStatus === 'nan'
  const s = rawStatus.toLowerCase()
  if (!isNA && s.includes('anexado')) return 'Não anexado'
  // A vencer, Vencido e N/A → Aguardando análise → split por solicitação
  const sitSolic = colSitSolic ? String(row[colSitSolic] ?? '').trim() : ''
  if (sitSolic === 'EM_ELABORACAO') return 'Aguardando Submissão'
  return 'Em Análise'
}

// ── R4: Lógica do relatorio_fornecedores_zurich.py ───────────────────────────
// Com coluna "Situação Análise Documento":
//   APROVADO → "Aprovado"
//   REPROVADO → "Reprovado"
//   NOT_ANALYZED + "A vencer" → "Aprovado"
//   NOT_ANALYZED + "Não anexado" → "Não Anexado"
//   NOT_ANALYZED + "Vencido" → "Vencido"
//   else → "Em análise"
// Sem coluna: legacy (vencer→Aprovado, vencido→Vencido, anexado→Não Anexado)
function mapStatusR4(
  row: Record<string, string>,
  colAnalise: string | null
): StatusR4 | null {
  if (colAnalise) {
    const analise = String(row[colAnalise] ?? '').trim().toUpperCase()
    if (analise === 'APROVADO') return 'Aprovado'
    if (analise === 'REPROVADO') return 'Reprovado'
    const status = String(row['Status'] ?? '').trim().toLowerCase()
    if (status.includes('vencer')) return 'Aprovado'
    if (status.includes('anexado')) return 'Não Anexado'
    if (status.includes('vencido')) return 'Vencido'
    return 'Em análise'
  }
  // Legacy
  const s = String(row['Status'] ?? '').toLowerCase()
  if (!s || s === 'nan') return null
  if (s.includes('aprovado') && !s.includes('ressalva')) return 'Aprovado'
  if (s.includes('reprovado')) return 'Reprovado'
  if (s.includes('vencer')) return 'Aprovado'
  if (s.includes('vencido')) return 'Vencido'
  if (s.includes('anexado')) return 'Não Anexado'
  return null
}

// ── Busca Automática: matrix das 4 regras ────────────────────────────────────
// NEUTRO = documento de input manual → retorna null para cair na lógica R4
// ALERTA = busca não executou → status próprio para sinalização
function mapStatusBuscaAuto(situacaoDoc: string, _situacaoAnalise: string): StatusR4 | null {
  const sd = situacaoDoc.trim().toUpperCase()
  if (sd === 'REGULAR')   return 'Aprovado'
  if (sd === 'IRREGULAR') return 'Irregular'
  if (sd === 'ALERTA')    return 'Alerta'
  if (sd === 'NEUTRO')    return null  // manual → cai no mapStatusR4
  return 'Em análise'
}

export function processAllData(
  rawPend: Record<string, string>[],
  rawTerc: Record<string, string>[],
  rawSit: Record<string, string>[],
  rawFornSit: Record<string, string>[],
  rawContratos: Record<string, string>[] = [],
  rawBuscaAuto: Record<string, string>[] = []
): DashboardData {
  // Montar lookup: "cnpj||doc_normalizado" → { situacaoDoc, situacaoAnalise, situacaoStatus }
  const buscaAutoLookup = new Map<string, { situacaoDoc: string; situacaoAnalise: string; situacaoStatus: string }>()
  rawBuscaAuto.forEach(row => {
    const cnpj = normCNPJ(row['CNPJ'] ?? '')
    const doc = String(row['Documento'] ?? '').trim().toUpperCase()
    if (!cnpj || !doc) return
    buscaAutoLookup.set(`${cnpj}||${doc}`, {
      situacaoDoc:    String(row['Situação Documento'] ?? '').trim(),
      situacaoAnalise: String(row['Situação Análise Documento'] ?? '').trim(),
      situacaoStatus: String(row['Status'] ?? '').trim(),
    })
  })
  const geradoEm = new Date().toLocaleString('pt-BR')

  // Capturar colunas Contrato 1..10 e dados brutos ANTES do strip (drill-down de contratos)
  const _contractCols = rawContratos[0]
    ? Object.keys(rawContratos[0]).filter(k => /^contrato\b/i.test(k.trim()))
    : []
  const _rawContratosForDrill = rawContratos

  // Strip colunas de contrato antes de processar (regex cobre "Contrato 1".."Contrato 10")
  rawPend      = stripContratos(rawPend)
  rawTerc      = stripContratos(rawTerc)
  rawSit       = stripContratos(rawSit)
  rawFornSit   = stripContratos(rawFornSit)
  rawContratos = stripContratos(rawContratos)

  // ── Descoberta de colunas ─────────────────────────────────────────────────
  const pendCols = rawPend[0] ? Object.keys(rawPend[0]) : []
  const colRsPend = findCol(pendCols, 'raz') ?? 'Razão Social'
  const colSitPend = findCol(pendCols, 'situa', 'solicit') ?? 'Situação da solicitação'
  const colAreaPend = findCol(pendCols, 'rea', 'pend') ?? 'Área da pendência'
  const colMarcasPend = findCol(pendCols, 'marcas') ?? 'Marcas e representações'
  // Busca específica para evitar retornar "Área da pendência" em vez de "Pendência"
  const colPendTxt = pendCols.find(c => /^pend[eê]ncia$/i.test(c.trim()))
    ?? pendCols.find(c => c.toLowerCase().includes('pend') && !c.toLowerCase().includes('rea') && !c.toLowerCase().includes('área'))
    ?? 'Pendência'

  const tercCols = rawTerc[0] ? Object.keys(rawTerc[0]) : []
  const colRsTerc = findCol(tercCols, 'raz') ?? 'Razão Social'
  const colStatusTerc = findCol(tercCols, 'status') ?? 'Status'

  const sitCols = rawSit[0] ? Object.keys(rawSit[0]) : []
  const colFornRS = findCol(sitCols, 'fornecedor', 'raz') ?? 'Fornecedor Razão Social'
  const colTercRS = findCol(sitCols, 'terceiro', 'raz') ?? 'Terceiro Razão Social'
  const colTercCNPJ = findCol(sitCols, 'terceiro', 'cpf') ?? 'Terceiro CPF/CNPJ'
  const colFornCNPJ = findCol(sitCols, 'fornecedor', 'cpf') ?? 'Fornecedor CPF/CNPJ'
  const colDatVenc = findCol(sitCols, 'data', 'venc') ?? 'Data de Vencimento'
  // Coluna "Situação Análise Documento" — busca por "lise" e "doc"
  const colAnaliseR3 = sitCols.find(c => c.toLowerCase().includes('lise') && c.toLowerCase().includes('doc')) ?? null
  // Coluna "Situação última solicitação"
  const colSitSolicR3 = sitCols.find(c => c.toLowerCase().includes('ltima') && c.toLowerCase().includes('solic')) ?? null
  // Coluna "Marcas e Representações" → Competência R3
  const colMarcasSit = sitCols.find(c => c.toLowerCase().includes('marcas')) ?? null

  // Lookup: normCNPJ(terceiro CPF) → aeroportos (do relatório de terceiros cadastrados)
  const _tercCols0 = rawTerc[0] ? Object.keys(rawTerc[0]) : []
  const _colCPFTerc0 = _tercCols0.find(c => c.toLowerCase().includes('terceiro') && c.toLowerCase().includes('cpf')) ?? 'CPF/CNPJ Terceiro'
  const _colAero0 = _tercCols0.find(c => c.toLowerCase().includes('aeroporto')) ?? 'Código do aeroporto'
  const tercAeroportoMap = new Map<string, Set<string>>()
  rawTerc.forEach(row => {
    const cpf = normCNPJ(row[_colCPFTerc0])
    const aero = normAeroporto(String(row[_colAero0] ?? ''))
    if (!cpf || !aero) return
    if (!tercAeroportoMap.has(cpf)) tercAeroportoMap.set(cpf, new Set())
    tercAeroportoMap.get(cpf)!.add(aero)
  })

  const colCNPJPend = pendCols.find(c => c.toLowerCase().includes('cpf') || c.toLowerCase().includes('cnpj')) ?? null

  const fornSitCols = rawFornSit[0] ? Object.keys(rawFornSit[0]) : []
  const colR4RS = fornSitCols[0] ?? 'Razão Social'
  // "Situação Análise Documento" contém "lise"; "Situação Documento" não — distingue os dois
  const colAnaliseR4 = fornSitCols.find(c => c.toLowerCase().includes('lise') && c.toLowerCase().includes('doc')) ?? null
  const colSitDocR4  = fornSitCols.find(c => {
    const lc = c.toLowerCase().trim()
    return lc.includes('situa') && lc.includes('doc') && !lc.includes('lise')
  }) ?? null
  const colCnpjR4   = fornSitCols.find(c => c.toLowerCase().includes('cpf') || c.toLowerCase().includes('cnpj')) ?? null
  const colMarcasR4 = fornSitCols.find(c => c.toLowerCase().includes('marcas')) ?? null

  // Documentos que exibem Competência mas não têm Vencimento relevante
  const DOCS_SEM_VENCIMENTO = new Set([
    'ficha de epi',
    'cartão ponto com total de horas extras ou noturnas',
  ])

  // Documentos R3 sem Competência — exibem só Vencimento (se houver)
  const DOCS_SEM_COMP_R3 = new Set(['aso', 'ordens de serviço', 'capacitação de acordo com a ordem de serviço'])

  // ── R3 — Situação por Terceiro ────────────────────────────────────────────
  const sitCalc: SitTerceiroRow[] = rawSit
    .map(row => {
      const status = mapStatusR3(row, colAnaliseR3, colSitSolicR3)
      if (!status) return null
      const comp = colMarcasSit ? String(row[colMarcasSit] ?? '').trim().replace(/^nan$/, '') : ''
      const docNome = String(row['Documento'] ?? '').trim()
      const docLower = docNome.toLowerCase()
      const venc = DOCS_SEM_VENCIMENTO.has(docLower)
        ? ''
        : fmtDate(row[colDatVenc] ?? row['Data de Vencimento'])
      const cpfTerceiro = normCNPJ(row[colTercCNPJ])
      const aeroSet = tercAeroportoMap.get(cpfTerceiro)
      return {
        Fornecedor: abbrev(String(row[colFornRS] || row['Fornecedor Razao Social'] || '')),
        Terceiro: String(row[colTercRS] || row['Terceiro Razao Social'] || '').trim(),
        CNPJ_Terceiro: cpfTerceiro,
        CNPJ_Forn: normCNPJ(row[colFornCNPJ]),
        Documento: docNome,
        Status: status,
        Vencimento: venc,
        Competencia: DOCS_SEM_COMP_R3.has(docLower) ? '' : (normalizeCompetencia(comp) || 'A classificar'),
        Aeroporto: aeroSet ? [...aeroSet].join(' / ') : '',
      }
    })
    .filter((r): r is SitTerceiroRow => r !== null)

  const total_docs_sit = sitCalc.length
  const aprovR3 = sitCalc.filter(r => r.Status === 'Aprovado').length
  const reprovR3 = sitCalc.filter(r => r.Status === 'Reprovado').length
  const naoAnexR3 = sitCalc.filter(r => r.Status === 'Não anexado').length
  const aguardR3Sub = sitCalc.filter(r => r.Status === 'Aguardando Submissão').length
  const aguardR3Real = sitCalc.filter(r => r.Status === 'Em Análise').length

  // ── Terceiros KPI ──────────────────────────────────────────────────────────
  const terc_kpi: TercKPIRow[] = rawTerc.map(row => ({
    Fornecedor: abbrev(String(row[colRsTerc] || '')),
    Status: String(row[colStatusTerc] || ''),
  }))
  const total_trab_ativo = terc_kpi.filter(r => r.Status === 'Ativo').length
  const total_trab_inativo = terc_kpi.filter(r => r.Status === 'Inativo').length

  // ── R4 — Situação por Fornecedor ─────────────────────────────────────────────
  // Prioridade: coluna "Situação Documento" da própria linha (adicionada 26/06/2026)
  //   REGULAR   → Aprovado  (robô confirmou válida; "A vencer" ainda é válida)
  //   IRREGULAR → Irregular
  //   ALERTA    → Alerta    (busca não executou — verificar manualmente)
  //   NEUTRO/vazio → usar "Situação Análise Documento": APROVADO→Aprovado, REPROVADO→Reprovado, else→Em análise
  //   Quando doc aparece em busca_auto: busca_auto tem prioridade (Situação Documento busca_auto + Status sitForn)

  // Apenas estes documentos exibem Competência no R4 — todos os demais ficam em branco
  const DOCS_COM_COMP_R4 = new Set([
    'GFD - GUIA DO FGTS DIGITAL MENSAL',
    'DCTFWEB',
    'FOPAG - (FOLHA DE PAGAMENTO + RESUMO)',
    'COMPROVANTE BANCÁRIO DE PAGAMENTO DOS SALÁRIOS',
    'KIT RESCISÃO',
    'RECIBO DE FÉRIAS + COMPROVANTE DE PAGAMENTO',
    'GRRF - GUIA DE RECOLHIMENTO RESCISÓRIO DO FGTS',
  ])

  const forn_sit: FornSitRow[] = rawFornSit
    .map(row => {
      const cnpj = colCnpjR4 ? normCNPJ(row[colCnpjR4]) : ''
      const doc = String(row['Documento'] ?? '').trim()
      const sitDoc  = colSitDocR4 ? String(row[colSitDocR4] ?? '').trim().toUpperCase() : ''
      const analise = colAnaliseR4 ? String(row[colAnaliseR4] ?? '').trim().toUpperCase() : ''
      const stRow   = String(row['Status'] ?? '').trim().toLowerCase()

      let status: StatusR4 | null = null

      const docKey   = `${cnpj}||${doc.toUpperCase()}`
      const autoEntry = buscaAutoLookup.get(docKey)

      if (autoEntry) {
        // busca_auto tem prioridade — Status vem do busca_auto (resultado da busca automática)
        const sdBA = autoEntry.situacaoDoc.trim().toUpperCase()
        const anBA = autoEntry.situacaoAnalise.trim().toUpperCase()
        const stBA = autoEntry.situacaoStatus.trim().toLowerCase()
        if (sdBA === 'REGULAR') {
          status = stBA.includes('vencido') ? 'Vencido' : 'Aprovado'
        } else if (sdBA === 'IRREGULAR') {
          status = 'Irregular'
        } else if (sdBA === 'ALERTA') {
          status = 'Em análise'
        } else if (sdBA === 'NEUTRO') {
          if (anBA === 'APROVADO')                         status = 'Aprovado'
          else if (anBA === 'REPROVADO')                   status = 'Reprovado'
          else if (stBA.includes('não anexado'))           status = 'Não Anexado'
          else                                             status = 'Em análise'
        } else {
          // vazio em busca_auto
          status = stBA.includes('não anexado') ? 'Não Anexado' : 'Em análise'
        }
      } else {
        // Não está em busca_auto → usa colunas da própria linha sitForn
        if (sitDoc === 'REGULAR') {
          if (stRow.includes('vencido')) {
            if (analise === 'APROVADO')        status = 'Aprovado'
            else if (analise === 'REPROVADO')  status = 'Reprovado'
            else                               status = 'Em análise'
          } else {
            status = 'Aprovado'
          }
        } else if (sitDoc === 'IRREGULAR') {
          status = 'Irregular'
        } else if (sitDoc === 'ALERTA') {
          status = 'Em análise'
        } else if (sitDoc === 'NEUTRO') {
          if (stRow.includes('não anexado')) status = 'Não Anexado'
          else if (analise === 'APROVADO')  status = 'Aprovado'
          else if (analise === 'REPROVADO') status = 'Reprovado'
          else                              status = 'Em análise'
        } else {
          // vazio → mesma regra do NEUTRO
          if (stRow.includes('não anexado')) status = 'Não Anexado'
          else if (analise === 'APROVADO')   status = 'Aprovado'
          else if (analise === 'REPROVADO')  status = 'Reprovado'
          else                               status = 'Em análise'
        }
      }
      if (!status) return null
      const rawComp = colMarcasR4 ? String(row[colMarcasR4] ?? '').trim() : ''
      const docAllowsComp = DOCS_COM_COMP_R4.has(doc.toUpperCase().trim())
      return {
        Fornecedor: abbrev(String(row[colR4RS] || '')),
        CNPJ_Forn: cnpj,
        Documento: doc,
        Status: status,
        Vencimento: fmtDate(row['Data de Vencimento']),
        // Competência só aparece para os 4 docs autorizados e nunca para busca_auto
        Competencia: (autoEntry || !docAllowsComp) ? '' : ((rawComp && rawComp !== 'nan') ? normalizeCompetencia(rawComp) : ''),
      }
    })
    .filter((r) => r !== null) as FornSitRow[]

  const r4_total      = forn_sit.length
  const r4_aprovado   = forn_sit.filter(r => r.Status === 'Aprovado').length
  const r4_reprovado  = forn_sit.filter(r => r.Status === 'Reprovado').length
  const r4_nao_anex   = forn_sit.filter(r => r.Status === 'Não Anexado').length
  const r4_em_analise = forn_sit.filter(r => r.Status === 'Em análise').length
  const r4_vencido    = forn_sit.filter(r => r.Status === 'Vencido').length
  const r4_irregular  = forn_sit.filter(r => r.Status === 'Irregular').length
  const r4_alerta     = forn_sit.filter(r => r.Status === 'Alerta').length
  const r4_nao_conf   = r4_reprovado + r4_nao_anex + r4_em_analise + r4_vencido + r4_irregular + r4_alerta
  const r4_pct_nc = r4_total > 0 ? Math.round(r4_nao_conf / r4_total * 1000) / 10 : 0
  const r4_pct_c  = r4_total > 0 ? Math.round(r4_aprovado / r4_total * 1000) / 10 : 0
  const r4_fornecedores = new Set(forn_sit.map(r => r.Fornecedor)).size

  // ── KPIs combinados R3+R4 ─────────────────────────────────────────────────
  const docs_aprovados    = aprovR3 + r4_aprovado
  const docs_reprovados   = reprovR3 + r4_reprovado + r4_irregular + r4_alerta
  const docs_nao_enviados = naoAnexR3 + r4_nao_anex
  const docs_aguard_sub   = aguardR3Sub
  const docs_em_analise   = aguardR3Real + r4_em_analise
  const docs_vencidos     = r4_vencido

  // ── CNPJs com execução (R3 + R4) ──────────────────────────────────────────
  const cnpjsR3 = new Set<string>()
  rawSit.forEach(row => {
    const c = normCNPJ(row[colFornCNPJ ?? ''])
    if (c) cnpjsR3.add(c)
  })
  const cnpjsR4 = new Set<string>()
  rawFornSit.forEach(row => {
    const c = colCnpjR4 ? normCNPJ(row[colCnpjR4]) : ''
    if (c) cnpjsR4.add(c)
  })
  const cnpjsExec = new Set([...cnpjsR3, ...cnpjsR4])

  // ── Fornecedores sem execução ─────────────────────────────────────────────
  let total_forn_geral = new Set([...sitCalc.map(r => r.Fornecedor), ...forn_sit.map(r => r.Fornecedor)]).size
  let sem_execucao: SemExecRow[] = []
  let total_sem_execucao = 0

  if (rawContratos.length > 0) {
    // Relatório de contratos é a fonte autoritativa da lista de fornecedores
    const allCNPJs = new Set(
      rawContratos.map(r => normCNPJ(r['Documento Fornecedor'])).filter(Boolean)
    )
    total_forn_geral = allCNPJs.size
    const seenSem = new Set<string>()
    sem_execucao = rawContratos
      .filter(row => {
        const cnpj = normCNPJ(row['Documento Fornecedor'])
        if (!cnpj || cnpjsExec.has(cnpj)) return false
        if (seenSem.has(cnpj)) return false
        seenSem.add(cnpj)
        return true
      })
      .map(row => ({
        Razao_Social: String(row['Fornecedor'] ?? '').trim(),
        CPF_CNPJ: normCNPJ(row['Documento Fornecedor']),
      }))
    total_sem_execucao = sem_execucao.length
  }

  const total_forn_com_execucao = total_forn_geral - total_sem_execucao

  // ── Lookups para StatusReal das pendências ────────────────────────────────
  // R4: cnpj|||doc → status atual
  const r4StatusLookup = new Map<string, StatusR4>()
  forn_sit.forEach(r => {
    r4StatusLookup.set(`${r.CNPJ_Forn}|||${r.Documento.toUpperCase()}`, r.Status)
  })

  // R3: cnpj_forn|||doc → 'Aprovado' se TODOS aprovados, 'NaoAprovado' se algum não
  const r3StatusLookup = new Map<string, 'Aprovado' | 'NaoAprovado'>()
  sitCalc.forEach(r => {
    const key = `${r.CNPJ_Forn}|||${r.Documento.toUpperCase()}`
    if (r3StatusLookup.get(key) === 'NaoAprovado') return
    r3StatusLookup.set(key, r.Status === 'Aprovado' ? 'Aprovado' : 'NaoAprovado')
  })

  // Regras de Competência para pendências
  const DOCS_COM_COMP_PEND = new Set([
    'GFD - GUIA DO FGTS DIGITAL MENSAL',
    'DCTFWEB',
    'FOPAG - (FOLHA DE PAGAMENTO + RESUMO)',
    'COMPROVANTE BANCÁRIO DE PAGAMENTO DOS SALÁRIOS',
    'KIT RESCISÃO',
    'RECIBO DE FÉRIAS + COMPROVANTE DE PAGAMENTO',
    'GRRF - GUIA DE RECOLHIMENTO RESCISÓRIO DO FGTS',
  ])
  const DOCS_SEM_COMP_PEND = new Set(['ASO', 'ORDENS DE SERVIÇO', 'CAPACITAÇÃO DE ACORDO COM A ORDEM DE SERVIÇO'])

  // REGRA VIGENTE: competência é lida EXCLUSIVAMENTE do campo estruturado
  // "Marcas e representações". Qualquer extração via texto livre (campo Pendência
  // ou nome do documento) é estritamente proibida.
  // Campo estruturado vazio → 'Sem competência preenchida' (sem fallback algum).

  // ── Tabela de pendências ───────────────────────────────────────────────────
  const tabela: PendRow[] = rawPend.map(row => {
    const comp = String(row[colMarcasPend] ?? '').trim().replace(/^nan$/, '')
    const area = String(row[colAreaPend] || '').trim()
    const docUpper = extractDoc(row, area)
    const isSemCompPend = DOCS_SEM_COMP_PEND.has(docUpper)
      || [...DOCS_SEM_COMP_PEND].some(base => docUpper.startsWith(base))
    let competencia: string
    if (isSemCompPend) {
      competencia = 'Não possui competência'
    } else if (area === 'DOCUMENTOS' && !DOCS_COM_COMP_PEND.has(docUpper)) {
      competencia = 'Não possui competência'
    } else {
      // Leitura exclusiva do campo estruturado "Marcas e representações".
      // Campo vazio = sem competência preenchida (sem extração de texto livre).
      competencia = normalizeCompetencia(comp) || 'Sem competência preenchida'
    }
    const cnpjPend = colCNPJPend ? normCNPJ(row[colCNPJPend]) : ''
    const statusPend = String(row[colSitPend] || '').trim()

    let statusReal: 'Ativa' | 'Não resolvida' | 'Resolvida'
    if (statusPend === 'EM_ELABORACAO') {
      statusReal = 'Ativa'
    } else {
      const key = `${cnpjPend}|||${docUpper}`
      if (area === 'DOCUMENTOS') {
        const r4St = r4StatusLookup.get(key)
        statusReal = (!r4St || r4St === 'Aprovado') ? 'Resolvida' : 'Não resolvida'
      } else {
        const r3St = r3StatusLookup.get(key)
        statusReal = (!r3St || r3St === 'Aprovado') ? 'Resolvida' : 'Não resolvida'
      }
    }

    return {
      Fornecedor: abbrev(String(row[colRsPend] || '')),
      CNPJ_Forn: cnpjPend,
      Status: statusPend,
      Area: area,
      Documento: docUpper,
      Competencia: competencia,
      Detalhe: String(row[colPendTxt] ?? '').trim(),
      StatusReal: statusReal,
    }
  })
  const competencias = [...new Set(tabela.map(r => r.Competencia).filter(c => c && c !== 'nan'))].sort()

  // Registros que exigem competência mas têm o campo estruturado vazio
  const pend_sem_competencia = tabela.filter(r => r.Competencia === 'Sem competência preenchida')

  // ── Chart data ────────────────────────────────────────────────────────────

  // fig1: pendências por fornecedor
  const pend_emp_map: Record<string, number> = {}
  rawPend.forEach(row => {
    const emp = abbrev(String(row[colRsPend] || ''))
    pend_emp_map[emp] = (pend_emp_map[emp] || 0) + 1
  })
  const pend_emp: BarEntry[] = Object.entries(pend_emp_map)
    .map(([name, value]) => ({ name, value }))
    .sort((a, b) => b.value - a.value)

  // fig2: top 15 tipo doc
  const tipo_doc_map: Record<string, number> = {}
  rawPend.forEach(row => {
    const doc = extractDoc(row, String(row[colAreaPend] || '').trim())
    tipo_doc_map[doc] = (tipo_doc_map[doc] || 0) + 1
  })
  const tipo_doc: BarEntry[] = Object.entries(tipo_doc_map)
    .map(([name, value]) => ({ name, value }))
    .sort((a, b) => b.value - a.value)
    .slice(0, 15)

  // fig3: status por empresa
  const empresas_ord = [...new Set(rawPend.map(r => abbrev(String(r[colRsPend] || ''))))]
    .map(emp => ({ emp, total: rawPend.filter(r => abbrev(String(r[colRsPend] || '')) === emp).length }))
    .sort((a, b) => b.total - a.total)
    .map(r => r.emp)

  const status_emp_data: StatusEmpEntry[] = empresas_ord.map(emp => {
    const rows = rawPend.filter(r => abbrev(String(r[colRsPend] || '')) === emp)
    return {
      emp,
      elab: rows.filter(r => String(r[colSitPend] || '').trim() === 'EM_ELABORACAO').length,
      apro: rows.filter(r => String(r[colSitPend] || '').trim() === 'APROVADO').length,
    }
  })

  // fig4: área por empresa
  const area_emp_data: AreaEmpEntry[] = empresas_ord.map(emp => {
    const rows = rawPend.filter(r => abbrev(String(r[colRsPend] || '')) === emp)
    return {
      emp,
      terceiros: rows.filter(r => String(r[colAreaPend] || '').trim() === 'TERCEIROS').length,
      documentos: rows.filter(r => String(r[colAreaPend] || '').trim() === 'DOCUMENTOS').length,
    }
  })

  // fig5: donut distribuição por área
  const pend_terceiros = rawPend.filter(r => String(r[colAreaPend] || '').trim() === 'TERCEIROS').length
  const pend_documentos = rawPend.filter(r => String(r[colAreaPend] || '').trim() === 'DOCUMENTOS').length
  const pend_donut: BarEntry[] = [
    { name: 'Terceiros', value: pend_terceiros },
    { name: 'Documentais', value: pend_documentos },
  ]

  // fig6: terceiros por empresa
  const trab_emp_map: Record<string, { ativo: number; inativo: number }> = {}
  rawTerc.forEach(row => {
    const emp = abbrev(String(row[colRsTerc] || ''))
    const st = String(row[colStatusTerc] || '')
    if (!trab_emp_map[emp]) trab_emp_map[emp] = { ativo: 0, inativo: 0 }
    if (st === 'Ativo') trab_emp_map[emp].ativo++
    else if (st === 'Inativo') trab_emp_map[emp].inativo++
  })
  const trab_emp_data: TrabEmpEntry[] = Object.entries(trab_emp_map)
    .map(([emp, v]) => ({ emp, ...v }))
    .sort((a, b) => (b.ativo + b.inativo) - (a.ativo + a.inativo))

  // fig7/8: conformidade por empresa — 4 categorias (Aprovado, Reprovado, Não anexado, Aguardando)
  const conf_emp_map: Record<string, { aprovado: number; reprovado: number; nao_anexado: number; aguardando: number }> = {}
  sitCalc.forEach(r => {
    if (!conf_emp_map[r.Fornecedor]) conf_emp_map[r.Fornecedor] = { aprovado: 0, reprovado: 0, nao_anexado: 0, aguardando: 0 }
    if (r.Status === 'Aprovado') conf_emp_map[r.Fornecedor].aprovado++
    else if (r.Status === 'Reprovado') conf_emp_map[r.Fornecedor].reprovado++
    else if (r.Status === 'Não anexado') conf_emp_map[r.Fornecedor].nao_anexado++
    else conf_emp_map[r.Fornecedor].aguardando++
  })
  const conf_emp_data: ConfEmpEntry[] = Object.entries(conf_emp_map)
    .map(([emp, v]) => {
      const total = v.aprovado + v.reprovado + v.nao_anexado + v.aguardando
      const pct_nc = total > 0 ? Math.round((v.reprovado + v.nao_anexado + v.aguardando) / total * 1000) / 10 : 0
      return { emp, ...v, total, pct_nc }
    })
    .sort((a, b) => b.pct_nc - a.pct_nc)

  // ── Drill-down ────────────────────────────────────────────────────────────
  const drillData: Record<string, Record<string, DrillDoc[]>> = {}
  sitCalc.forEach(r => {
    if (!drillData[r.Fornecedor]) drillData[r.Fornecedor] = {}
    if (!drillData[r.Fornecedor][r.Terceiro]) drillData[r.Fornecedor][r.Terceiro] = []
    drillData[r.Fornecedor][r.Terceiro].push({ doc: r.Documento, status: r.Status, venc: r.Vencimento, comp: r.Competencia })
  })

  // ── Drill-down de contratos ────────────────────────────────────────────────
  // Fonte primária: rawContratos (Contrato 1..10) → todos os contratos por fornecedor
  // Fonte secundária: rawTerc (Código do contrato vinculado) → terceiros por contrato
  // O campo "Código do contrato vinculado" pode ter múltiplos separados por "/"

  const tercCols2 = rawTerc[0] ? Object.keys(rawTerc[0]) : []
  const colRsTercForn   = findCol(tercCols2, 'raz') ?? 'Razão Social'
  const colCNPJTercForn = tercCols2.find(c => c.toLowerCase().includes('cpf') && !c.toLowerCase().includes('terceiro')) ?? 'CPF/CNPJ'
  const colRsTercNome   = tercCols2.find(c => c.toLowerCase().includes('terceiro') && c.toLowerCase().includes('raz')) ?? 'Razão Social Terceiro'
  const colCPFTerc      = tercCols2.find(c => c.toLowerCase().includes('terceiro') && c.toLowerCase().includes('cpf')) ?? 'CPF/CNPJ Terceiro'
  // Busca específica para evitar capturar "Quais códigos de contrato esse fornecedor possui atualmente?"
  const colCodContrato  = tercCols2.find(c => /^código do contrato\b/i.test(c.trim()))
    ?? tercCols2.find(c => c.toLowerCase().includes('vinculado'))
    ?? 'Código do contrato vinculado'
  const colAeroporto    = tercCols2.find(c => c.toLowerCase().includes('aeroporto')) ?? 'Código do aeroporto'
  const colCargo        = tercCols2.find(c => c.toLowerCase().includes('cargo')) ?? 'Cargo'
  const colStatusTerc2  = tercCols2.find(c => c.toLowerCase() === 'status') ?? 'Status'

  // 1. Mapa CNPJ → { nome, contratos: Set<string> } a partir do relatório de contratos
  const _fornContratosBase: Record<string, { nome: string; contratos: Set<string> }> = {}
  _rawContratosForDrill.forEach(row => {
    const cnpj = normCNPJ(row['Documento Fornecedor'])
    const nome = abbrev(String(row['Fornecedor'] ?? ''))
    if (!cnpj || !nome) return
    if (!_fornContratosBase[cnpj]) _fornContratosBase[cnpj] = { nome, contratos: new Set() }
    _contractCols.forEach(col => {
      const val = String(row[col] ?? '').trim()
      if (val && val !== 'nan') _fornContratosBase[cnpj].contratos.add(val)
    })
  })

  // 2. Mapa CNPJ → { [codContrato]: TerceiroContratoItem[] } a partir do cadastro de terceiros
  // Split por "/" para separar contratos concatenados no mesmo campo
  const _tercByContrato: Record<string, Record<string, TerceiroContratoItem[]>> = {}
  rawTerc.forEach(row => {
    const cnpj = normCNPJ(row[colCNPJTercForn])
    const nomeTerceiro = String(row[colRsTercNome] ?? '').trim()
    const cpfTerceiro = normCNPJ(row[colCPFTerc])
    const codContratosRaw = String(row[colCodContrato] ?? '').trim()
    const cargo = String(row[colCargo] ?? '').trim()
    const status = String(row[colStatusTerc2] ?? '').trim()
    const aeroporto = normAeroporto(String(row[colAeroporto] ?? ''))

    if (!cnpj || !nomeTerceiro || !codContratosRaw) return

    if (!_tercByContrato[cnpj]) _tercByContrato[cnpj] = {}
    if (!_tercByContrato[cnpj][codContratosRaw]) _tercByContrato[cnpj][codContratosRaw] = []
    _tercByContrato[cnpj][codContratosRaw].push({ nome: nomeTerceiro, cpf: cpfTerceiro, cargo, status, aeroporto })

    // Garantir que o fornecedor aparece no mapa base mesmo que não esteja no relatório de contratos
    const nomeForn = abbrev(String(row[colRsTercForn] ?? ''))
    if (cnpj && nomeForn && !_fornContratosBase[cnpj]) {
      _fornContratosBase[cnpj] = { nome: nomeForn, contratos: new Set() }
    }
    if (cnpj && _fornContratosBase[cnpj]) {
      _fornContratosBase[cnpj].contratos.add(codContratosRaw)
    }
  })

  // 3. Merge: fornecedor → lista de contratos (com ou sem terceiros)
  const contratosData: FornContratoItem[] = Object.entries(_fornContratosBase)
    .filter(([, f]) => f.contratos.size > 0)
    .map(([cnpj, f]) => {
      const contratos: ContratoItem[] = [...f.contratos]
        .map(codigo => {
          const terceiros = _tercByContrato[cnpj]?.[codigo] ?? []
          return {
            codigo,
            aeroporto: terceiros[0]?.aeroporto ?? '',
            totalTerceiros: terceiros.length,
            terceiros,
          }
        })
        .sort((a, b) => a.codigo.localeCompare(b.codigo, 'pt-BR', { sensitivity: 'base' }))
      return {
        nome: f.nome,
        cnpj,
        totalContratos: contratos.length,
        totalTerceiros: contratos.reduce((s, c) => s + c.totalTerceiros, 0),
        contratos,
      }
    })
    .sort((a, b) => a.nome.localeCompare(b.nome, 'pt-BR', { sensitivity: 'base' }))

  const fornecedores_list = [...new Set(tabela.map(r => r.Fornecedor))].sort()

  // Mapa name → [CNPJ, ...] para o dropdown — suporta matriz + filiais com mesmo nome
  const fornCNPJMap: Record<string, string[]> = {}
  const _addCNPJ = (name: string, cnpj: string) => {
    if (!name || !cnpj) return
    if (!fornCNPJMap[name]) fornCNPJMap[name] = []
    if (!fornCNPJMap[name].includes(cnpj)) fornCNPJMap[name].push(cnpj)
  }
  // Relatório de contratos: fonte autoritativa para o dropdown (inclui todos os fornecedores)
  rawContratos.forEach(row => {
    _addCNPJ(abbrev(String(row['Fornecedor'] ?? '')), normCNPJ(row['Documento Fornecedor']))
  })
  // Complementa com R3/R4/pendências (cobre empresas ausentes do relatório de contratos)
  sitCalc.forEach(r => _addCNPJ(r.Fornecedor, r.CNPJ_Forn))
  forn_sit.forEach(r => _addCNPJ(r.Fornecedor, r.CNPJ_Forn))
  tabela.forEach(r => _addCNPJ(r.Fornecedor, r.CNPJ_Forn))

  return {
    total_forn_geral,
    total_forn_com_execucao,
    total_sem_execucao,
    r4_total,
    total_docs_sit,
    docs_aprovados,
    docs_reprovados,
    docs_nao_enviados,
    docs_aguard_sub,
    docs_em_analise,
    docs_vencidos,
    r4_aprovado,
    r4_reprovado,
    r4_nao_anex,
    r4_em_analise,
    r4_vencido,
    r4_irregular,
    r4_alerta,
    r4_pct_nc,
    r4_pct_c,
    r4_fornecedores,
    pend_emp,
    tipo_doc,
    status_emp_data,
    area_emp_data,
    pend_donut,
    trab_emp_data,
    conf_emp_data,
    tabela,
    sit_tabela: sitCalc,
    forn_sit,
    terc_kpi,
    sem_execucao,
    drillData,
    contratosData,
    fornCNPJMap,
    competencias,
    pend_sem_competencia,
    fornecedores_list,
    geradoEm,
  }
}
