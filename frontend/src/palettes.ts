export interface Palette {
  name: string
  colors: string[]
}

export const PALETTES: Palette[] = [
  {
    name: 'Índigo',
    colors: ['#6366f1', '#22c55e', '#f97316', '#ec4899', '#06b6d4', '#eab308', '#8b5cf6', '#ef4444'],
  },
  {
    name: 'Corporativo',
    colors: ['#2563eb', '#0891b2', '#0d9488', '#4338ca', '#7c3aed', '#0369a1', '#155e75', '#1e3a8a'],
  },
  {
    name: 'Atardecer',
    colors: ['#f97316', '#ef4444', '#eab308', '#ec4899', '#f59e0b', '#dc2626', '#fb923c', '#facc15'],
  },
  {
    name: 'Pastel',
    colors: ['#a5b4fc', '#86efac', '#fdba74', '#f9a8d4', '#67e8f9', '#fde047', '#c4b5fd', '#fca5a5'],
  },
]
