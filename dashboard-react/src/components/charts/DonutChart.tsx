import { PieChart, Pie, Cell, Legend, Tooltip, ResponsiveContainer } from 'recharts'

interface Props {
  data: { name: string; value: number }[]
  colors: string[]
  title: string
}

export function DonutChart({ data, colors, title }: Props) {
  return (
    <div>
      <p className="text-[15px] font-bold text-[#0E8FA3] mb-3">{title}</p>
      <ResponsiveContainer width="100%" height={280}>
        <PieChart>
          <Pie
            data={data}
            dataKey="value"
            nameKey="name"
            innerRadius="45%"
            outerRadius="68%"
            paddingAngle={2}
          >
            {data.map((_, i) => (
              <Cell key={i} fill={colors[i % colors.length]} />
            ))}
          </Pie>
          <Tooltip
            formatter={(v: number, name: string) => [v, name]}
            contentStyle={{ fontSize: 12, borderRadius: 6 }}
          />
          <Legend
            formatter={(value, entry) => {
              const pct = data.reduce((s, d) => s + d.value, 0)
              const item = data.find(d => d.name === value)
              const p = pct > 0 && item ? ((item.value / pct) * 100).toFixed(1) : '0'
              return `${value} ${p}%`
            }}
            wrapperStyle={{ fontSize: 12 }}
          />
        </PieChart>
      </ResponsiveContainer>
    </div>
  )
}
