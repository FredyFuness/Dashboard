from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from analyzer import build_dashboard

app = FastAPI(title="Excel Dashboard API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

ALLOWED_EXTENSIONS = (".xlsx", ".xls", ".xlsm")


@app.post("/api/analyze")
async def analyze(file: UploadFile = File(...), sheet_name: str | None = Form(None)):
    if not file.filename.lower().endswith(ALLOWED_EXTENSIONS):
        raise HTTPException(status_code=400, detail="El archivo debe ser un Excel (.xlsx, .xls, .xlsm)")

    file_bytes = await file.read()
    if not file_bytes:
        raise HTTPException(status_code=400, detail="El archivo está vacío")

    try:
        return build_dashboard(file_bytes, sheet_name)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=f"No se pudo leer la hoja: {exc}") from exc
    except Exception as exc:
        raise HTTPException(status_code=422, detail=f"No se pudo procesar el archivo: {exc}") from exc


@app.get("/api/health")
async def health():
    return {"status": "ok"}
