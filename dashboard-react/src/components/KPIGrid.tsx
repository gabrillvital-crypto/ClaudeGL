interface KPI {
  value: string | number
  label: string
  color?: 'default' | 'orange' | 'red' | 'yellow' | 'green' | 'gray'
  tooltip?: string
  kpiKey?: string
}

function KPICard({
  value, label, color = 'default', tooltip, kpiKey, isActive, onKpiClick,
}: KPI & { isActive?: boolean; onKpiClick?: (key: string) => void }) {
  const borderColors = {
    default: 'border-t-[#0E8FA3]',
    orange:  'border-t-[#F4793B]',
    red:     'border-t-[#DC3545]',
    yellow:  'border-t-[#FFC107]',
    green:   'border-t-[#28A745]',
    gray:    'border-t-[#6C757D]',
  }
  const valueColors = {
    default: 'text-[#0E8FA3]',
    orange:  'text-[#F4793B]',
    red:     'text-[#DC3545]',
    yellow:  'text-[#a07800]',
    green:   'text-[#28A745]',
    gray:    'text-[#6C757D]',
  }
  const ringColors = {
    default: 'ring-[#0E8FA3]',
    orange:  'ring-[#F4793B]',
    red:     'ring-[#DC3545]',
    yellow:  'ring-[#FFC107]',
    green:   'ring-[#28A745]',
    gray:    'ring-[#6C757D]',
  }

  const isClickable = !!kpiKey

  return (
    <div
      onClick={isClickable ? () => onKpiClick?.(kpiKey!) : undefined}
      className={[
        'bg-white rounded-xl p-4 shadow-sm border-t-4 text-center relative group',
        borderColors[color],
        isClickable ? 'cursor-pointer hover:shadow-md transition-all select-none' : '',
        isActive ? `ring-2 ring-offset-1 ${ringColors[color]} shadow-md` : '',
      ].filter(Boolean).join(' ')}
    >
      {isActive && (
        <div className="absolute top-1.5 right-1.5 text-[9px] font-bold text-white bg-[#0E8FA3] rounded-full px-1.5 py-0.5 leading-none">
          ativo
        </div>
      )}
      <div className={`text-3xl font-bold leading-tight ${valueColors[color]}`}>{value}</div>
      <div
        className="text-[11px] text-[#666] mt-1.5 font-semibold uppercase tracking-wide leading-tight"
        dangerouslySetInnerHTML={{ __html: label }}
      />
      {tooltip && (
        <div className="absolute bottom-[calc(100%+8px)] left-1/2 -translate-x-1/2 w-56 bg-[#1a2a35] text-white text-[11px] rounded-lg px-3 py-2 leading-relaxed opacity-0 group-hover:opacity-100 transition-opacity duration-200 pointer-events-none z-50 shadow-xl text-left">
          {tooltip}
          <div className="absolute top-full left-1/2 -translate-x-1/2 border-[6px] border-transparent border-t-[#1a2a35]" />
        </div>
      )}
    </div>
  )
}

interface Props {
  total_forn_geral: number
  total_forn_com_execucao: number
  r4_total: number
  total_docs_sit: number
  docs_aprovados: number
  docs_reprovados: number
  docs_nao_enviados: number
  docs_aguard_sub: number
  docs_em_analise: number
  docs_vencidos: number
  hideGlobal?: boolean
  activeKpi?: string | null
  onKpiClick?: (key: string) => void
}

export function KPIGrid(props: Props) {
  const { activeKpi, onKpiClick } = props

  const globalKpis: KPI[] = [
    {
      value: props.total_forn_geral,
      label: 'Total de<br>Fornecedores',
      color: 'default',
      tooltip: 'Número total de empresas fornecedoras cadastradas na base da plataforma.',
    },
    {
      value: props.total_forn_com_execucao,
      label: 'Fornecedores com<br>Execução na Plataforma',
      color: 'default',
      tooltip: 'Fornecedores que possuem documentação ativa em R3 (terceiros) ou R4 (corporativo) — estão operando na plataforma.',
    },
  ]

  const activeKpis: KPI[] = [
    {
      value: props.r4_total,
      label: 'Docs Esperados<br>Fornecedor',
      color: 'default',
      tooltip: 'Total de documentos corporativos que o fornecedor precisa enviar (R4). Inclui todos os status.',
    },
    {
      value: props.total_docs_sit,
      label: 'Docs Esperados<br>Terceiros',
      color: 'default',
      tooltip: 'Total de documentos exigidos dos funcionários ou prestadores vinculados ao fornecedor (R3). Inclui todos os status.',
    },
    {
      value: props.docs_aprovados,
      label: 'Documentos<br>Aprovados',
      color: 'green',
      kpiKey: 'docs_aprovados',
      tooltip: 'Documentos que foram analisados e validados pela equipe de conformidade. Estão em dia. Clique para filtrar as tabelas.',
    },
    {
      value: props.docs_reprovados,
      label: 'Documentos<br>Não Aprovados',
      color: 'red',
      kpiKey: 'docs_reprovados',
      tooltip: 'Total de documentos em situação de não conformidade: Reprovado, Irregular ou Alerta — em R3 (terceiros) e R4 (corporativo). Clique para filtrar as tabelas.',
    },
    {
      value: props.docs_nao_enviados,
      label: 'Documentos<br>Não Enviados',
      color: 'yellow',
      kpiKey: 'docs_nao_enviados',
      tooltip: 'Documentos obrigatórios ainda pendentes de envio pelo fornecedor ou terceiro. Clique para filtrar as tabelas.',
    },
    {
      value: props.docs_aguard_sub,
      label: 'Aguardando<br>Submissão',
      color: 'yellow',
      kpiKey: 'docs_aguard_sub',
      tooltip: 'Documentos inseridos na plataforma pelo fornecedor, mas ainda não submetidos para análise. Clique para filtrar as tabelas.',
    },
    {
      value: props.docs_em_analise,
      label: 'Documentos<br>Em Análise',
      color: 'orange',
      kpiKey: 'docs_em_analise',
      tooltip: 'Documentos já submetidos pelos fornecedores aguardando validação da equipe de conformidade. Clique para filtrar as tabelas.',
    },
    {
      value: props.docs_vencidos,
      label: 'Documentos<br>Vencidos',
      color: 'red',
      kpiKey: 'docs_vencidos',
      tooltip: 'Documentos de fornecedores (R4) com prazo vencido — exigem renovação ou substituição imediata. Clique para filtrar as tabelas.',
    },
  ]

  const visibleKpis = props.hideGlobal ? activeKpis : [...globalKpis, ...activeKpis]
  const cols = visibleKpis.length <= 8 ? 'repeat(4, 1fr)' : 'repeat(5, 1fr)'

  return (
    <div className="grid gap-3 mb-7" style={{ gridTemplateColumns: cols }}>
      {visibleKpis.map((k, i) => (
        <KPICard
          key={i}
          {...k}
          isActive={!!k.kpiKey && activeKpi === k.kpiKey}
          onKpiClick={onKpiClick}
        />
      ))}
    </div>
  )
}
