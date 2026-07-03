import { useState } from 'react'
import FileUpload from './components/FileUpload'
import Dashboard from './components/Dashboard'
import { analyzeFile } from './api'
import type { DashboardData } from './types'
import './App.css'

const defaultTitle = (fileName: string) => {
  const base = fileName.replace(/\.[^.]+$/, '').replace(/[_-]+/g, ' ').trim()
  const capitalized = base.replace(/\b\w/g, (c) => c.toUpperCase())
  return `Dashboard de ${capitalized}`
}

function App() {
  const [file, setFile] = useState<File | null>(null)
  const [data, setData] = useState<DashboardData | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [title, setTitle] = useState('')
  const [paletteIndex, setPaletteIndex] = useState(0)

  const run = async (selectedFile: File, sheetName?: string) => {
    setLoading(true)
    setError(null)
    try {
      const result = await analyzeFile(selectedFile, sheetName)
      setData(result)
      setFile((prevFile) => {
        if (!prevFile || prevFile.name !== selectedFile.name) {
          setTitle(defaultTitle(selectedFile.name))
        }
        return selectedFile
      })
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error desconocido')
    } finally {
      setLoading(false)
    }
  }

  const reset = () => {
    setData(null)
    setFile(null)
    setError(null)
    setPaletteIndex(0)
  }

  return (
    <div className="app">
      <header className="app-header">
        <h1>📊 Generador automático de dashboards</h1>
        <p className="muted">Subí un Excel y obtené un dashboard con KPIs y gráficos al instante.</p>
      </header>

      {!data && (
        <>
          <FileUpload onFileSelected={(f) => run(f)} disabled={loading} />
          {loading && <p className="status">Analizando archivo…</p>}
          {error && <p className="status error">{error}</p>}
        </>
      )}

      {data && file && (
        <Dashboard
          data={data}
          title={title}
          onTitleChange={setTitle}
          paletteIndex={paletteIndex}
          onPaletteChange={setPaletteIndex}
          onSheetChange={(sheet) => run(file, sheet)}
          onReset={reset}
        />
      )}
    </div>
  )
}

export default App
