import { useRef, useState } from 'react'
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
  const latestRequest = useRef(0)

  const run = async (selectedFile: File, sheetName?: string) => {
    const requestId = ++latestRequest.current
    setLoading(true)
    setError(null)
    try {
      const result = await analyzeFile(selectedFile, sheetName)
      if (requestId !== latestRequest.current) return
      if (!file || file !== selectedFile) {
        setTitle(defaultTitle(selectedFile.name))
      }
      setData(result)
      setFile(selectedFile)
    } catch (err) {
      if (requestId !== latestRequest.current) return
      setError(err instanceof Error ? err.message : 'Error desconocido')
    } finally {
      if (requestId === latestRequest.current) setLoading(false)
    }
  }

  const reset = () => {
    ++latestRequest.current // Ignore any response from an earlier request.
    setData(null)
    setFile(null)
    setError(null)
    setTitle('')
    setLoading(false)
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

      {data && error && <p className="status error" role="alert">{error}</p>}
      {data && loading && <p className="status" role="status">Actualizando hoja…</p>}
      {data && file && (
        <Dashboard
          data={data}
          title={title}
          onTitleChange={setTitle}
          paletteIndex={paletteIndex}
          onPaletteChange={setPaletteIndex}
          onSheetChange={(sheet) => run(file, sheet)}
          onReset={reset}
          loading={loading}
        />
      )}
    </div>
  )
}

export default App
