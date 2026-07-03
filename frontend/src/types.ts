export interface Kpi {
  label: string
  sum: number | null
  avg: number | null
  min: number | null
  max: number | null
  count: number
}

export interface ChartSpec {
  type: 'line' | 'bar' | 'pie'
  title: string
  xKey: string
  yKeys: string[]
  data: Record<string, unknown>[]
}

export interface Insight {
  severity: 'danger' | 'warning' | 'success' | 'info'
  title: string
  description: string
  suggestion: string
}

export interface DashboardData {
  sheets: string[]
  selectedSheet: string
  rowCount: number
  columns: {
    numeric: string[]
    datetime: string[]
    categorical: string[]
  }
  kpis: Kpi[]
  charts: ChartSpec[]
  insights: Insight[]
  preview: {
    columns: string[]
    rows: Record<string, unknown>[]
  }
}
