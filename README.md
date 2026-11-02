# Dashboard automático desde Excel

Aplicación web que convierte una hoja de cálculo en un panel de indicadores y gráficos. Su objetivo es facilitar la exploración inicial de datos sin construir cada visualización manualmente.

## Funciones implementadas
- Carga de archivos Excel y selección de hoja.
- Detección de columnas numéricas, fechas y categorías.
- Indicadores de suma, promedio, mínimo, máximo y cantidad.
- Gráficos de evolución temporal y distribución por categorías.
- Vista previa de hasta 50 filas.
- Observaciones sobre tendencias, valores atípicos y datos incompletos.

Las observaciones se generan mediante reglas estadísticas en Python; no requieren un modelo de IA generativa. La API acepta extensiones `.xlsx`, `.xls` y `.xlsm`; la lectura de `.xls` requiere un motor adicional compatible que no está incluido en el archivo actual de dependencias. CSV no está implementado en el endpoint actual.

## Tecnologías y organización
- `frontend/`: React, TypeScript, Vite, Recharts y Axios.
- `backend/`: FastAPI, pandas, NumPy y openpyxl.
- `backend/analyzer.py`: clasificación de columnas, indicadores y gráficos.
- `backend/insights.py`: interpretación basada en reglas.
- `test_data.xlsx` y `test_data2.xlsx`: archivos para explorar la aplicación.
- `render.yaml` y `.github/workflows/`: configuración de despliegue.

## Ejecución local
Requiere Python y Node.js compatibles con las dependencias declaradas.

En una terminal, desde la raíz:
```bash
cd backend
python -m venv .venv
# Activar .venv: source .venv/bin/activate (Linux/macOS)
# En PowerShell: .venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m uvicorn main:app --reload --port 8000
```

En otra terminal:
```bash
cd frontend
npm ci
npm run dev
```
Abre la dirección que muestre Vite, normalmente `http://localhost:5173`. La API utiliza `http://localhost:8000` por defecto; para cambiarla, configura `VITE_API_BASE` en el frontend.

## Comprobación manual
1. Comprueba `GET /api/health`.
2. Carga uno de los Excel incluidos y revisa indicadores, gráficos y vista previa.
3. Cambia de hoja si el archivo contiene varias.
4. Comprueba los mensajes al subir un archivo vacío o de una extensión no admitida.

## Alcance
Prototipo con frontend y backend implementados. Las inferencias dependen de la estructura de los datos y requieren revisión humana. La configuración de publicación del frontend no sustituye la ejecución de la API. Las instrucciones anteriores describen la configuración del código; no constituyen una certificación de despliegue o pruebas en producción.
