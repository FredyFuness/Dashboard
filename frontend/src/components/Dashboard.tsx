import type { DashboardData } from '../types'
import { PALETTES } from '../palettes'
import KpiCard from './KpiCard'
import ChartCard from './ChartCard'
import InsightsPanel from './InsightsPanel'

interface Props {
  data: DashboardData
  title: string
  onTitleChange: (title: string) => void
  paletteIndex: number
  onPaletteChange: (index: number) => void
  onSheetChange: (sheet: string) => void
  onReset: () => void
}

export default function Dashboard({
  data,
  title,
  onTitleChange,
  paletteIndex,
  onPaletteChange,
  onSheetChange,
  onReset,
}: Props) {
  const colors = PALETTES[paletteIndex].colors

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <div className="title-block">
          <input
            className="title-input"
            value={title}
            onChange={(e) => onTitleChange(e.target.value)}
            aria-label="Nombre del dashboard"
          />
          <p className="muted">
            {data.rowCount} filas · Hoja: {data.selectedSheet}
          </p>
        </div>
        <div className="dashboard-actions">
          {data.sheets.length > 1 && (
            <select value={data.selectedSheet} onChange={(e) => onSheetChange(e.target.value)}>
              {data.sheets.map((s) => (
                <option key={s} value={s}>
                  {s}
                </option>
              ))}
            </select>
          )}
          <button className="secondary" onClick={onReset}>
            Subir otro archivo
          </button>
        </div>
      </div>

      <div className="design-panel">
        <span className="design-label">Paleta de colores:</span>
        <div className="palette-options">
          {PALETTES.map((palette, i) => (
            <button
              key={palette.name}
              className={`palette-swatch${i === paletteIndex ? ' active' : ''}`}
              title={palette.name}
              onClick={() => onPaletteChange(i)}
            >
              {palette.colors.slice(0, 4).map((c) => (
                <span key={c} style={{ background: c }} />
              ))}
            </button>
          ))}
        </div>
      </div>

      {data.kpis.length > 0 && (
        <div className="kpi-grid">
          {data.kpis.map((kpi) => (
            <KpiCard key={kpi.label} kpi={kpi} />
          ))}
        </div>
      )}

      <InsightsPanel insights={data.insights} />

      {data.charts.length > 0 ? (
        <div className="chart-grid">
          {data.charts.map((chart, i) => (
            <ChartCard key={i} chart={chart} colors={colors} />
          ))}
        </div>
      ) : (
        <p className="muted">No se detectaron columnas suficientes para generar gráficos automáticamente.</p>
      )}

      <div className="table-section">
        <h3>Vista previa de datos</h3>
        <div className="table-wrapper">
          <table>
            <thead>
              <tr>
                {data.preview.columns.map((c) => (
                  <th key={c}>{c}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {data.preview.rows.map((row, i) => (
                <tr key={i}>
                  {data.preview.columns.map((c) => (
                    <td key={c}>{String(row[c] ?? '')}</td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
