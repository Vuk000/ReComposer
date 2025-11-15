import { useMemo } from 'react'
import { cn } from '@/lib/utils'

export interface ChartDataPoint {
  label?: string
  value: number
}

export interface ChartProps {
  data: ChartDataPoint[]
  type?: 'line' | 'bar'
  color?: string
  height?: number
  className?: string
}

const Chart = ({ data, type = 'line', color = '#8c5cff', height = 200, className }: ChartProps) => {
  const { normalizedData } = useMemo(() => {
    if (data.length === 0) return { normalizedData: [] }

    const values = data.map((d) => d.value)
    const max = Math.max(...values)
    const min = Math.min(...values)
    const range = max - min || 1

    return {
      normalizedData: data.map((d) => ({
        ...d,
        normalized: ((d.value - min) / range) * 100,
      })),
    }
  }, [data])

  if (data.length === 0) {
    return (
      <div className={cn('flex items-center justify-center', className)} style={{ height }}>
        <p className="text-sm text-muted-foreground">No data available</p>
      </div>
    )
  }

  const width = 100 / data.length

  return (
    <div className={cn('relative', className)} style={{ height }}>
      <svg width="100%" height="100%" className="overflow-visible">
        {type === 'line' ? (
          <polyline
            points={normalizedData
              .map(
                (d, i) =>
                  `${(i * 100) / (data.length - 1 || 1)},${100 - d.normalized}`
              )
              .join(' ')}
            fill="none"
            stroke={color}
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
        ) : (
          normalizedData.map((d, i) => (
            <rect
              key={i}
              x={`${i * width}%`}
              y={`${100 - d.normalized}%`}
              width={`${width * 0.8}%`}
              height={`${d.normalized}%`}
              fill={color}
              rx="2"
            />
          ))
        )}
        {normalizedData.map((d, i) => (
          <circle
            key={i}
            cx={`${(i * 100) / (data.length - 1 || 1)}%`}
            cy={`${100 - d.normalized}%`}
            r="4"
            fill={color}
            className="transition-all hover:r-6"
          />
        ))}
      </svg>
    </div>
  )
}

export default Chart

