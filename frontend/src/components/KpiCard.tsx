import type { Kpi } from '../types'

const fmt = (n: number | null) => (n === null ? '-' : n.toLocaleString('es-AR', { maximumFractionDigits: 2 }))

export default function KpiCard({ kpi }: { kpi: Kpi }) {
  return (
    <div className="kpi-card">
      <h3>{kpi.label}</h3>
      <div className="kpi-main">{fmt(kpi.sum)}</div>
      <div className="kpi-details">
        <span>Prom: {fmt(kpi.avg)}</span>
        <span>Min: {fmt(kpi.min)}</span>
        <span>Max: {fmt(kpi.max)}</span>
      </div>
    </div>
  )
}
