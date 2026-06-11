import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip,
  LabelList, Cell, ResponsiveContainer,
} from 'recharts'

interface Props {
  data: { name: string; value: number }[]
  color?: string
  colorFn?: (value: number) => string
  suffix?: string
  title: string
}

const TICK_STYLE = { fontSize: 11, fill: '#555' }

export function HorizBarChart({ data, color = '#0E8FA3', colorFn, suffix = '', title }: Props) {
  const barHeight = 36
  const height = Math.max(300, data.length * barHeight + 80)
  const yWidth = Math.min(220, Math.max(120, Math.max(...data.map(d => d.name.length)) * 6.5))

  return (
    <div>
      <p className="text-[15px] font-bold text-[#0E8FA3] mb-3">{title}</p>
      <ResponsiveContainer width="100%" height={height}>
        <BarChart data={data} layout="vertical" margin={{ top: 5, right: 60, left: 10, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="#eee" />
          <XAxis type="number" tick={TICK_STYLE} tickLine={false} axisLine={false} />
          <YAxis
            type="category" dataKey="name" width={yWidth}
            tick={TICK_STYLE} tickLine={false} axisLine={false}
          />
          <Tooltip
            formatter={(v: number) => [`${v}${suffix}`, '']}
            contentStyle={{ fontSize: 12, borderRadius: 6 }}
          />
          <Bar dataKey="value" radius={[0, 3, 3, 0]} maxBarSize={22}>
            {colorFn
              ? data.map((entry, i) => <Cell key={i} fill={colorFn(entry.value)} />)
              : <Cell fill={color} />
            }
            <LabelList
              dataKey="value"
              position="right"
              formatter={(v: number) => `${v}${suffix}`}
              style={{ fontSize: 11, fill: '#555' }}
            />
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}
