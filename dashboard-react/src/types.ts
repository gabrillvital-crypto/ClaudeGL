// Status R3 (situação_terceiro_zurich.csv — inclui Situação Análise Documento)
export type StatusR3 = 'Aprovado' | 'Reprovado' | 'Não anexado' | 'Aguardando Submissão' | 'Em Análise'

// Status R4 (situacao_fornecedor_zurich.csv)
export type StatusR4 = 'Aprovado' | 'Reprovado' | 'Não Anexado' | 'Em análise' | 'Vencido'

export interface PendRow {
  Fornecedor: string
  CNPJ_Forn: string
  Status: string
  Area: string
  Documento: string
  Competencia: string
  Detalhe: string
}

export interface SitTerceiroRow {
  Fornecedor: string
  Terceiro: string
  CNPJ_Terceiro: string
  CNPJ_Forn: string
  Documento: string
  Status: StatusR3
  Vencimento: string
}

export interface FornSitRow {
  Fornecedor: string
  CNPJ_Forn: string
  Documento: string
  Status: StatusR4
  Vencimento: string
}

export interface TercKPIRow {
  Fornecedor: string
  Status: string
}

export interface SemExecRow {
  Razao_Social: string
  CPF_CNPJ: string
}

export interface BarEntry {
  name: string
  value: number
}

export interface ConfEmpEntry {
  emp: string
  aprovado: number
  reprovado: number
  nao_anexado: number
  aguardando: number
  pct_nc: number
  total: number
}

export interface StatusEmpEntry {
  emp: string
  elab: number
  apro: number
}

export interface AreaEmpEntry {
  emp: string
  terceiros: number
  documentos: number
}

export interface TrabEmpEntry {
  emp: string
  ativo: number
  inativo: number
}

export interface DrillDoc {
  doc: string
  status: string
  venc: string
}

export interface DashboardData {
  // KPIs principais
  total_forn_geral: number          // do cadastro fornecedores.csv
  total_forn_com_execucao: number   // CNPJ em R3 ou R4
  total_sem_execucao: number        // no cadastro mas sem docs

  // Docs esperados
  r4_total: number
  total_docs_sit: number

  // Status combinados R3+R4
  docs_aprovados: number            // aprovR3 + aprovR4
  docs_reprovados: number           // reprovR3 + reprovR4
  docs_nao_enviados: number         // naoAnexR3 + naoAnexR4
  docs_aguard_sub: number           // aguardR3_elab
  docs_em_analise: number           // aguardR3_real + r4_em_analise
  docs_vencidos: number             // r4_vencido

  // R4 sub-KPIs (para seção forn-sit)
  r4_aprovado: number
  r4_reprovado: number
  r4_nao_anex: number
  r4_em_analise: number
  r4_vencido: number
  r4_pct_nc: number
  r4_pct_c: number
  r4_fornecedores: number

  // Para gráficos
  pend_emp: BarEntry[]           // fig1
  tipo_doc: BarEntry[]           // fig2
  status_emp_data: StatusEmpEntry[]  // fig3
  area_emp_data: AreaEmpEntry[]  // fig4
  pend_donut: BarEntry[]         // fig5
  trab_emp_data: TrabEmpEntry[]  // fig6
  conf_emp_data: ConfEmpEntry[]  // fig7/8

  // Tabelas
  tabela: PendRow[]
  sit_tabela: SitTerceiroRow[]
  forn_sit: FornSitRow[]
  terc_kpi: TercKPIRow[]
  sem_execucao: SemExecRow[]

  // Drill-down: fornecedor → terceiro → docs
  drillData: Record<string, Record<string, DrillDoc[]>>

  // Mapa abbrev-name → lista de CNPJs (suporta matriz + filiais com mesmo nome)
  fornCNPJMap: Record<string, string[]>

  // Meta
  competencias: string[]
  fornecedores_list: string[]
  geradoEm: string
}
