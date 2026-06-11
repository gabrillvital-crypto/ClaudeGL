interface BadgeStatusProps {
  status: string
  type?: 'sit' | 'area' | 'pend'
}

const sitStyles: Record<string, string> = {
  'Aprovado':              'bg-green-100 text-green-800',
  'Reprovado':             'bg-red-100 text-red-700',
  'Não anexado':           'bg-yellow-100 text-yellow-800',
  'Aguardando Submissão':  'bg-amber-100 text-amber-700',
  'Em Análise':            'bg-cyan-100 text-[#0E8FA3]',
  'Aguardando análise':    'bg-orange-100 text-orange-700',
  'Em análise':            'bg-cyan-100 text-[#0E8FA3]',
  'Vencido':               'bg-red-100 text-red-700',
  'Não Analisado':         'bg-orange-100 text-orange-700',
  'A vencer':              'bg-green-100 text-green-700',
  'Não Anexado':           'bg-yellow-100 text-yellow-800',
  'Conforme':              'bg-green-100 text-green-700',
}

const areaStyles: Record<string, string> = {
  'TERCEIROS':   'bg-cyan-100 text-[#0E8FA3]',
  'DOCUMENTOS':  'bg-orange-100 text-orange-700',
}

const pendStyles: Record<string, string> = {
  'EM_ELABORACAO': 'bg-red-100 text-red-700',
  'APROVADO':      'bg-yellow-50 text-yellow-700',
}

const areaLabels: Record<string, string> = {
  'TERCEIROS':  'Terceiros',
  'DOCUMENTOS': 'Fornecedor',
}

const pendLabels: Record<string, string> = {
  'EM_ELABORACAO': 'Pendente (não enviado)',
  'APROVADO':      'Em Análise',
}

export function BadgeStatus({ status, type = 'sit' }: BadgeStatusProps) {
  const styles = type === 'area' ? areaStyles : type === 'pend' ? pendStyles : sitStyles
  const labels = type === 'area' ? areaLabels : type === 'pend' ? pendLabels : undefined
  const cls = styles[status] ?? 'bg-gray-100 text-gray-600'
  const label = labels?.[status] ?? status

  return (
    <span className={`inline-block px-2 py-0.5 rounded-full text-xs font-bold whitespace-nowrap ${cls}`}>
      {label}
    </span>
  )
}
