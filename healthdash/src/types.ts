export type Tier = 'A' | 'B+' | 'B' | 'C'
export type StatusHS = 'verde' | 'amarelo' | 'vermelho'

// 0=nunca executou, 1=configurado sem exec ativa, 2=executando
export type BuscaStatus = 0 | 1 | 2
// 0=sem resposta, 1=contato feito, 2=reunião feita/agendada
export type EngagementRenovacao = 0 | 1 | 2

export interface ClienteInput {
  cliente: string
  tier: Tier
  mrr: number

  // Adoção
  dias_ultimo_login: number | null
  usuario_ativo: number
  usuario_contratado: number
  modulos_uso: number
  modulos_contratado: number
  buscas_status: BuscaStatus

  // Maturidade
  forn_cadastrado: number
  forn_meta: number
  docs_vencidos: number
  docs_total: number
  config_sistema_pct: number | null

  // Valor Gerado
  conformidade_aprovados: number
  conformidade_total: number
  certidoes_status: BuscaStatus
  rfi_trimestre: number | null  // null = módulo não contratado

  // Relacionamento
  nps: number | null
  dias_ultima_interacao: number
  tickets_criticos: number

  // Risco Comercial
  dias_renovacao: number
  engagement_renovacao: EngagementRenovacao
}

export interface MetricaScore {
  nome: string
  valor: string
  pts: number
  status: StatusHS | 'nd'
}

export interface DimensionScore {
  nome: string
  score: number
  peso: number
  metricas: MetricaScore[]
}

export interface ClienteScore {
  input: ClienteInput
  score: number
  status: StatusHS
  dimensoes: DimensionScore[]
  alertas: string[]
}
