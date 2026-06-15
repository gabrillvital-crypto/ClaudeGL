import { ClienteInput, ClienteScore, DimensionScore, MetricaScore, StatusHS } from '../types'

// Pontua uma métrica nas 3 faixas padrão: verde=100, amarelo=70, vermelho=40
function pts3(val: number, limGreen: number, limYellow: number, moreIsBetter = true): number {
  if (moreIsBetter) {
    if (val >= limGreen) return 100
    if (val >= limYellow) return 70
    return 40
  } else {
    if (val <= limGreen) return 100
    if (val <= limYellow) return 70
    return 40
  }
}

function statusFromPts(pts: number): StatusHS {
  if (pts >= 85) return 'verde'
  if (pts >= 60) return 'amarelo'
  return 'vermelho'
}

// Calcula score ponderado ignorando métricas nulas (redistribuição proporcional)
function weightedScore(items: { pts: number | null; peso: number }[]): number {
  const active = items.filter(i => i.pts !== null)
  if (active.length === 0) return 0
  const totalPeso = active.reduce((s, i) => s + i.peso, 0)
  const sum = active.reduce((s, i) => s + i.pts! * i.peso, 0)
  return Math.round(sum / totalPeso)
}

function pct(num: number, den: number): number {
  if (den === 0) return 0
  return Math.min(Math.round((num / den) * 100), 100)
}

// ─── DIMENSÃO 1: Adoção (30%) ────────────────────────────────────────────────
function calcAdocao(c: ClienteInput): DimensionScore {
  const metricas: MetricaScore[] = []
  const weights: { pts: number | null; peso: number }[] = []

  // Último login (35%)
  if (c.dias_ultimo_login !== null) {
    const p = pts3(c.dias_ultimo_login, 15, 45, false)
    metricas.push({ nome: 'Último login', valor: `${c.dias_ultimo_login} dias`, pts: p, status: statusFromPts(p) })
    weights.push({ pts: p, peso: 35 })
  } else {
    metricas.push({ nome: 'Último login', valor: 'A verificar', pts: 0, status: 'nd' })
    weights.push({ pts: null, peso: 35 })
  }

  // Usuários ativos / contratados (30%)
  const uPct = pct(c.usuario_ativo, c.usuario_contratado)
  const uPts = pts3(uPct, 80, 50)
  metricas.push({ nome: 'Usuários ativos', valor: `${c.usuario_ativo}/${c.usuario_contratado} (${uPct}%)`, pts: uPts, status: statusFromPts(uPts) })
  weights.push({ pts: uPts, peso: 30 })

  // Módulos em uso / contratados (20%)
  const mPct = pct(c.modulos_uso, c.modulos_contratado)
  const mPts = pts3(mPct, 80, 50)
  metricas.push({ nome: 'Módulos em uso', valor: `${c.modulos_uso}/${c.modulos_contratado} (${mPct}%)`, pts: mPts, status: statusFromPts(mPts) })
  weights.push({ pts: mPts, peso: 20 })

  // Buscas automáticas (15%)
  const bPts = [40, 70, 100][c.buscas_status]
  const bLabel = ['Nunca executou', 'Config. ok, sem execução', 'Executando ativamente'][c.buscas_status]
  metricas.push({ nome: 'Buscas automáticas', valor: bLabel, pts: bPts, status: statusFromPts(bPts) })
  weights.push({ pts: bPts, peso: 15 })

  const score = weightedScore(weights)
  return { nome: 'Adoção', score, peso: 30, metricas }
}

// ─── DIMENSÃO 2: Maturidade (25%) ────────────────────────────────────────────
function calcMaturidade(c: ClienteInput): DimensionScore {
  const metricas: MetricaScore[] = []
  const weights: { pts: number | null; peso: number }[] = []

  // Fornecedores cadastrados (40%)
  const fPct = pct(c.forn_cadastrado, c.forn_meta)
  const fPts = pts3(fPct, 75, 50)
  metricas.push({ nome: 'Fornecedores cadastrados', valor: `${c.forn_cadastrado}/${c.forn_meta} (${fPct}%)`, pts: fPts, status: statusFromPts(fPts) })
  weights.push({ pts: fPts, peso: 40 })

  // Documentos vencidos (35%)
  const dvPct = pct(c.docs_vencidos, c.docs_total)
  const dvPts = pts3(dvPct, 10, 30, false)
  metricas.push({ nome: 'Documentos vencidos', valor: `${c.docs_vencidos}/${c.docs_total} (${dvPct}%)`, pts: dvPts, status: statusFromPts(dvPts) })
  weights.push({ pts: dvPts, peso: 35 })

  // Configuração do sistema (25%)
  if (c.config_sistema_pct !== null) {
    const cPts = pts3(c.config_sistema_pct, 90, 70)
    metricas.push({ nome: 'Config. do sistema', valor: `${c.config_sistema_pct}%`, pts: cPts, status: statusFromPts(cPts) })
    weights.push({ pts: cPts, peso: 25 })
  } else {
    metricas.push({ nome: 'Config. do sistema', valor: 'A verificar', pts: 0, status: 'nd' })
    weights.push({ pts: null, peso: 25 })
  }

  const score = weightedScore(weights)
  return { nome: 'Maturidade', score, peso: 25, metricas }
}

// ─── DIMENSÃO 3: Valor Gerado (20%) ──────────────────────────────────────────
function calcValor(c: ClienteInput): DimensionScore {
  const metricas: MetricaScore[] = []
  const weights: { pts: number | null; peso: number }[] = []

  // Conformidade documental (50%)
  const cPct = pct(c.conformidade_aprovados, c.conformidade_total)
  const cPts = pts3(cPct, 80, 60)
  metricas.push({ nome: 'Conformidade documental', valor: `${c.conformidade_aprovados}/${c.conformidade_total} (${cPct}%)`, pts: cPts, status: statusFromPts(cPts) })
  weights.push({ pts: cPts, peso: 50 })

  // Certidões automáticas (30%)
  const certPts = [40, 70, 100][c.certidoes_status]
  const certLabel = ['Nunca executou', 'Execução irregular (>90d)', 'Ativas regularmente'][c.certidoes_status]
  metricas.push({ nome: 'Certidões automáticas', valor: certLabel, pts: certPts, status: statusFromPts(certPts) })
  weights.push({ pts: certPts, peso: 30 })

  // RFI realizados (20%) — null = módulo não contratado
  if (c.rfi_trimestre !== null) {
    const rPts = c.rfi_trimestre >= 1 ? 100 : 40
    metricas.push({ nome: 'RFI no trimestre', valor: `${c.rfi_trimestre} realizado(s)`, pts: rPts, status: statusFromPts(rPts) })
    weights.push({ pts: rPts, peso: 20 })
  } else {
    metricas.push({ nome: 'RFI no trimestre', valor: 'Módulo não contratado', pts: 0, status: 'nd' })
    weights.push({ pts: null, peso: 20 })
  }

  const score = weightedScore(weights)
  return { nome: 'Valor Gerado', score, peso: 20, metricas }
}

// ─── DIMENSÃO 4: Relacionamento (15%) ────────────────────────────────────────
function calcRelacionamento(c: ClienteInput): DimensionScore {
  const metricas: MetricaScore[] = []
  const weights: { pts: number | null; peso: number }[] = []

  // NPS (40%)
  if (c.nps !== null) {
    const nPts = c.nps >= 8 ? 100 : c.nps >= 6 ? 70 : 40
    metricas.push({ nome: 'NPS', valor: `${c.nps}`, pts: nPts, status: statusFromPts(nPts) })
    weights.push({ pts: nPts, peso: 40 })
  } else {
    metricas.push({ nome: 'NPS', valor: 'Não coletado', pts: 0, status: 'nd' })
    weights.push({ pts: null, peso: 40 })
  }

  // Última interação (35%)
  const iPts = pts3(c.dias_ultima_interacao, 15, 30, false)
  metricas.push({ nome: 'Última interação', valor: `${c.dias_ultima_interacao} dias`, pts: iPts, status: statusFromPts(iPts) })
  weights.push({ pts: iPts, peso: 35 })

  // Tickets críticos (25%)
  const tPts = c.tickets_criticos === 0 ? 100 : c.tickets_criticos === 1 ? 70 : 40
  metricas.push({ nome: 'Tickets em aberto >5d', valor: `${c.tickets_criticos}`, pts: tPts, status: statusFromPts(tPts) })
  weights.push({ pts: tPts, peso: 25 })

  const score = weightedScore(weights)
  return { nome: 'Relacionamento', score, peso: 15, metricas }
}

// ─── DIMENSÃO 5: Risco Comercial (10%) ───────────────────────────────────────
function calcRisco(c: ClienteInput): DimensionScore {
  const metricas: MetricaScore[] = []

  // Dias para renovação (60%)
  const dPts = pts3(c.dias_renovacao, 90, 30)
  const dLabel = c.dias_renovacao > 365 ? 'Contrato vigente' : `${c.dias_renovacao} dias`
  metricas.push({ nome: 'Renovação em', valor: dLabel, pts: dPts, status: statusFromPts(dPts) })

  // Engagement na renovação (40%)
  const ePts = [40, 70, 100][c.engagement_renovacao]
  const eLabel = ['Sem resposta', 'Contato feito', 'Reunião agendada/realizada'][c.engagement_renovacao]
  metricas.push({ nome: 'Engajamento renovação', valor: eLabel, pts: ePts, status: statusFromPts(ePts) })

  const score = Math.round(dPts * 0.6 + ePts * 0.4)
  return { nome: 'Risco Comercial', score, peso: 10, metricas }
}

// ─── ALERTAS ─────────────────────────────────────────────────────────────────
function calcAlertas(c: ClienteInput, dimensoes: DimensionScore[]): string[] {
  const alertas: string[] = []

  if (c.dias_ultimo_login !== null && c.dias_ultimo_login > 30) alertas.push(`Último login há ${c.dias_ultimo_login} dias`)
  if (c.tickets_criticos > 0) alertas.push(`${c.tickets_criticos} ticket(s) aberto(s) sem resolução >5 dias`)
  if (c.dias_renovacao <= 30) alertas.push(`Renovação em ${c.dias_renovacao} dias`)
  if (c.dias_renovacao <= 90 && c.engagement_renovacao === 0) alertas.push('Renovação próxima sem resposta do cliente')
  if (c.docs_total > 0 && pct(c.docs_vencidos, c.docs_total) > 20) alertas.push(`${pct(c.docs_vencidos, c.docs_total)}% de documentos vencidos`)
  if (c.nps !== null && c.nps <= 6) alertas.push(`NPS baixo: ${c.nps}`)
  if (c.rfi_trimestre === 0) alertas.push('Módulo de Avaliações (RFI) sem uso no trimestre')
  if (c.buscas_status === 0) alertas.push('Buscas automáticas nunca executadas')
  if (c.certidoes_status === 0) alertas.push('Certidões automáticas nunca executadas')

  const _dim = dimensoes // just to avoid lint warning
  void _dim

  return alertas
}

// ─── MAIN ─────────────────────────────────────────────────────────────────────
export function calcScore(c: ClienteInput): ClienteScore {
  const d1 = calcAdocao(c)
  const d2 = calcMaturidade(c)
  const d3 = calcValor(c)
  const d4 = calcRelacionamento(c)
  const d5 = calcRisco(c)
  const dimensoes = [d1, d2, d3, d4, d5]

  const score = Math.round(
    d1.score * 0.30 +
    d2.score * 0.25 +
    d3.score * 0.20 +
    d4.score * 0.15 +
    d5.score * 0.10
  )

  const status: StatusHS = score >= 80 ? 'verde' : score >= 60 ? 'amarelo' : 'vermelho'
  const alertas = calcAlertas(c, dimensoes)

  return { input: c, score, status, dimensoes, alertas }
}
