"""HTTP API for bounded, validated Excel analysis uploads."""

import io
import logging
from zipfile import BadZipFile, ZipFile

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from analyzer import build_dashboard

logger = logging.getLogger(__name__)

app = FastAPI(title="Excel Dashboard API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "https://fredyfuness.github.io"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

ALLOWED_EXTENSIONS = (".xlsx", ".xlsm")
MAX_UPLOAD_BYTES = 10 * 1024 * 1024  # 10 MiB
MAX_UNCOMPRESSED_BYTES = 80 * 1024 * 1024  # ZIP expansion guard
MAX_ZIP_MEMBERS = 1000


def validate_excel_archive(file_bytes: bytes) -> None:
    """Reject arbitrary ZIPs and oversized declared OOXML payloads."""
    try:
        with ZipFile(io.BytesIO(file_bytes)) as archive:
            members = archive.infolist()
            names = {member.filename for member in members}
            if not {"[Content_Types].xml", "xl/workbook.xml"}.issubset(names):
                raise HTTPException(
                    status_code=400,
                    detail="El archivo no tiene la estructura de un Excel válido",
                )
            if (
                len(members) > MAX_ZIP_MEMBERS
                or sum(member.file_size for member in members) > MAX_UNCOMPRESSED_BYTES
            ):
                raise HTTPException(
                    status_code=413,
                    detail="El contenido del Excel supera el límite permitido",
                )
    except (BadZipFile, OSError) as exc:
        raise HTTPException(
            status_code=400, detail="El archivo no tiene un formato Excel válido"
        ) from exc


@app.post("/api/analyze")
async def analyze(file: UploadFile = File(...), sheet_name: str | None = Form(None)):
    filename = file.filename or ""
    if not filename.lower().endswith(ALLOWED_EXTENSIONS):
        raise HTTPException(
            status_code=400, detail="Solo se admiten archivos Excel .xlsx y .xlsm"
        )

    # Limit what this handler reads; configure a proxy limit as well, since
    # multipart parsing occurs before entering the endpoint.
    try:
        file_bytes = await file.read(MAX_UPLOAD_BYTES + 1)
    finally:
        await file.close()

    if not file_bytes:
        raise HTTPException(status_code=400, detail="El archivo está vacío")
    if len(file_bytes) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="El archivo supera los 10 MiB")

    validate_excel_archive(file_bytes)

    try:
        return build_dashboard(file_bytes, sheet_name)
    except (ValueError, BadZipFile, KeyError) as exc:
        raise HTTPException(
            status_code=400, detail=f"No se pudo leer el archivo: {exc}"
        ) from exc
    except Exception as exc:
        logger.exception("Error inesperado al procesar el Excel")
        raise HTTPException(
            status_code=422, detail="No se pudo procesar el archivo Excel"
        ) from exc


@app.get("/api/health")
async def health():
    return {"status": "ok"}
