import { PieChart, Pie, Cell, Legend, Tooltip, ResponsiveContainer } from 'recharts'
import type { SitTerceiroRow, FornSitRow } from '../types'

const COR_CONF = '#10B981'
const COR_NAO_CONF = '#EF4444'

function PizzaCard({
  title,
  conforme,
  naoConforme,
  size = 'sm',
}: {
  title: string
  conforme: number
  naoConforme: number
  size?: 'sm' | 'lg'
}) {
  const total = conforme + naoConforme
  const pct = total > 0 ? (conforme / total * 100).toFixed(1) : '0.0'
  const naoConf = total > 0 ? (100 - parseFloat(pct)).toFixed(1) : '0.0'
  const data = [
    { name: `Conforme ${pct}%`, value: conforme },
    { name: `Não Conforme ${naoConf}%`, value: naoConforme },
  ]

  const height = size === 'lg' ? 280 : 210
  const ir = size === 'lg' ? '40%' : '45%'
  const or = size === 'lg' ? '70%' : '66%'

  return (
    <div
      className={`bg-white rounded-xl shadow-sm p-4 text-center flex flex-col justify-between ${
        size === 'lg'
          ? 'ring-2 ring-[#0E8FA3]/60 ring-offset-2 shadow-lg'
          : ''
      }`}
    >
      <div
        className={`font-bold uppercase tracking-wide mb-1 ${
          size === 'lg'
            ? 'text-[13px] text-[#0E8FA3]'
            : 'text-[11px] text-[#0E8FA3]'
        }`}
      >
        {title}
      </div>

      <div className="relative" style={{ height }}>
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={data}
              dataKey="value"
              innerRadius={ir}
              outerRadius={or}
              paddingAngle={2}
            >
              <Cell fill={COR_CONF} />
              <Cell fill={COR_NAO_CONF} />
            </Pie>
            <Tooltip
              formatter={(v: number) => [`${v} docs`, '']}
              contentStyle={{ fontSize: 11, borderRadius: 6 }}
            />
            <Legend
              formatter={value => value}
              wrapperStyle={{ fontSize: 11 }}
              verticalAlign="bottom"
            />
          </PieChart>
        </ResponsiveContainer>

        {/* Porcentagem no centro */}
        <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
          <div className="text-center">
            <div
              className={`font-black leading-none ${
                size === 'lg' ? 'text-[24px]' : 'text-[18px]'
              }`}
              style={{ color: '#1a2a35' }}
            >
              {pct}%
            </div>
            <div className="text-[9px] text-[#888] mt-0.5">conforme</div>
          </div>
        </div>
      </div>
    </div>
  )
}

interface Props {
  sitData: SitTerceiroRow[]
  fornData: FornSitRow[]
}

export function ConformidadeCharts({ sitData, fornData }: Props) {
  const aprovR3 = sitData.filter(r => r.Status === 'Aprovado').length
  const naoConfR3 = sitData.length - aprovR3

  const aprovR4 = fornData.filter(r => r.Status === 'Aprovado').length
  const naoConfR4 = fornData.length - aprovR4

  const aprovGeral = aprovR3 + aprovR4
  const naoConfGeral = naoConfR3 + naoConfR4

  return (
    <div
      className="grid gap-5 mb-7 items-stretch"
      style={{ gridTemplateColumns: '1fr 1.5fr 1fr' }}
    >
      {/* Esquerdo — Fornecedores */}
      <PizzaCard
        title="Conformidade Fornecedores"
        conforme={aprovR4}
        naoConforme={naoConfR4}
        size="sm"
      />

      {/* Centro — Geral (destaque) */}
      <PizzaCard
        title="★ Conformidade Geral"
        conforme={aprovGeral}
        naoConforme={naoConfGeral}
        size="lg"
      />

      {/* Direito — Terceiros */}
      <PizzaCard
        title="Conformidade Terceiros"
        conforme={aprovR3}
        naoConforme={naoConfR3}
        size="sm"
      />
    </div>
  )
}
