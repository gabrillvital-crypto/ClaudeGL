import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip,
  Legend, ResponsiveContainer,
} from 'recharts'

export interface StackedSeries {
  key: string
  label: string
  color: string
}

interface Props {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  data: any[]
  nameKey: string
  series: StackedSeries[]
  title: string
  grouped?: boolean
}

const TICK_STYLE = { fontSize: 11, fill: '#555' }

export function StackedHorizBarChart({ data, nameKey, series, title, grouped = false }: Props) {
  const barHeight = grouped ? 50 : 40
  const height = Math.max(300, data.length * barHeight + 80)
  const maxLen = Math.max(...data.map(d => String(d[nameKey] || '').length))
  const yWidth = Math.min(220, Math.max(120, maxLen * 6.5))

  return (
    <div>
      <p className="text-[15px] font-bold text-[#0E8FA3] mb-3">{title}</p>
      <ResponsiveContainer width="100%" height={height}>
        <BarChart
          data={data} layout="vertical"
          margin={{ top: 5, right: 30, left: 10, bottom: 30 }}
          barCategoryGap={grouped ? '20%' : '30%'}
        >
          <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="#eee" />
          <XAxis type="number" tick={TICK_STYLE} tickLine={false} axisLine={false} />
          <YAxis
            type="category" dataKey={nameKey} width={yWidth}
            tick={TICK_STYLE} tickLine={false} axisLine={false}
          />
          <Tooltip contentStyle={{ fontSize: 12, borderRadius: 6 }} />
          <Legend
            wrapperStyle={{ fontSize: 12, paddingTop: 8 }}
            verticalAlign="bottom"
          />
          {series.map(s => (
            <Bar
              key={s.key}
              dataKey={s.key}
              name={s.label}
              fill={s.color}
              stackId={grouped ? undefined : 'a'}
              radius={[0, 2, 2, 0]}
              maxBarSize={20}
            />
          ))}
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}
