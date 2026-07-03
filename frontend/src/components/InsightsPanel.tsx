import type { Insight } from '../types'

const SEVERITY_META: Record<Insight['severity'], { icon: string; className: string }> = {
  danger: { icon: '📉', className: 'insight-danger' },
  warning: { icon: '⚠️', className: 'insight-warning' },
  success: { icon: '📈', className: 'insight-success' },
  info: { icon: 'ℹ️', className: 'insight-info' },
}

export default function InsightsPanel({ insights }: { insights: Insight[] }) {
  if (insights.length === 0) return null

  return (
    <div className="insights-section">
      <h3>Insights y posibles soluciones</h3>
      <div className="insights-grid">
        {insights.map((insight, i) => {
          const meta = SEVERITY_META[insight.severity]
          return (
            <div key={i} className={`insight-card ${meta.className}`}>
              <div className="insight-title">
                <span>{meta.icon}</span> {insight.title}
              </div>
              <p className="insight-description">{insight.description}</p>
              <p className="insight-suggestion">💡 {insight.suggestion}</p>
            </div>
          )
        })}
      </div>
    </div>
  )
}
