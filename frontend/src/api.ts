import axios from 'axios'
import type { DashboardData } from './types'

const API_BASE = import.meta.env.VITE_API_BASE ?? 'http://localhost:8000'

export async function analyzeFile(file: File, sheetName?: string): Promise<DashboardData> {
  const form = new FormData()
  form.append('file', file)
  if (sheetName) form.append('sheet_name', sheetName)

  try {
    const { data } = await axios.post<DashboardData>(`${API_BASE}/api/analyze`, form)
    return data
  } catch (err) {
    if (axios.isAxiosError(err) && err.response?.data?.detail) {
      throw new Error(err.response.data.detail as string)
    }
    throw new Error('No se pudo conectar con el servidor. ¿Está corriendo el backend?')
  }
}
