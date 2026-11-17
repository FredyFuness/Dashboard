from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from zipfile import BadZipFile, is_zipfile
import io

from analyzer import build_dashboard

app = FastAPI(title="Excel Dashboard API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "https://fredyfuness.github.io"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

ALLOWED_EXTENSIONS = (".xlsx", ".xlsm")
MAX_UPLOAD_BYTES = 10 * 1024 * 1024  # 10 MiB


@app.post("/api/analyze")
async def analyze(file: UploadFile = File(...), sheet_name: str | None = Form(None)):
    filename = file.filename or ""
    if not filename.lower().endswith(ALLOWED_EXTENSIONS):
        raise HTTPException(status_code=400, detail="Solo se admiten archivos Excel .xlsx y .xlsm")

    # Read at most the configured limit plus one byte, preventing unbounded uploads.
    file_bytes = await file.read(MAX_UPLOAD_BYTES + 1)
    await file.close()
    if not file_bytes:
        raise HTTPException(status_code=400, detail="El archivo está vacío")
    if len(file_bytes) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="El archivo supera el límite de 10 MB")
    if not is_zipfile(io.BytesIO(file_bytes)):
        raise HTTPException(status_code=400, detail="El archivo no tiene un formato Excel válido")

    try:
        return build_dashboard(file_bytes, sheet_name)
    except (ValueError, BadZipFile, KeyError) as exc:
        raise HTTPException(status_code=400, detail=f"No se pudo leer el archivo: {exc}") from exc
    except Exception as exc:
        # Do not disclose backend tracebacks or internal error details to clients.
        raise HTTPException(status_code=422, detail="No se pudo procesar el archivo Excel") from exc


@app.get("/api/health")
async def health():
    return {"status": "ok"}
