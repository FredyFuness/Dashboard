import io

import pandas as pd
from fastapi.testclient import TestClient

from main import MAX_UPLOAD_BYTES, app

client = TestClient(app)


def excel_bytes(data=None):
    buffer = io.BytesIO()
    frame = pd.DataFrame(data if data is not None else {
        "Fecha": pd.to_datetime(["2026-01-01", "2026-01-02", "2026-01-03"]),
        "Ventas": [10, 20, 30],
        "Marca": ["A", "B", "A"],
    })
    frame.to_excel(buffer, index=False)
    return buffer.getvalue()


def upload(content, name="datos.xlsx", **data):
    return client.post(
        "/api/analyze",
        files={"file": (name, content, "application/octet-stream")},
        data=data,
    )


def test_health():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_valid_excel_generates_dashboard():
    response = upload(excel_bytes())
    assert response.status_code == 200
    result = response.json()
    assert result["rowCount"] == 3
    assert result["selectedSheet"] == "Sheet1"
    assert result["kpis"][0]["sum"] == 60
    assert result["charts"]
    assert result["preview"]["rows"]


def test_rejects_unsupported_extension():
    response = upload(b"some,data", "datos.csv")
    assert response.status_code == 400


def test_rejects_empty_file():
    response = upload(b"")
    assert response.status_code == 400


def test_rejects_oversized_file():
    response = upload(b"x" * (MAX_UPLOAD_BYTES + 1))
    assert response.status_code == 413


def test_rejects_fake_xlsx():
    response = upload(b"not an Excel workbook")
    assert response.status_code == 400


def test_rejects_unknown_sheet():
    response = upload(excel_bytes(), sheet_name="No existe")
    assert response.status_code == 400


def test_rejects_empty_sheet():
    response = upload(excel_bytes({"a": [], "b": []}))
    assert response.status_code == 400


def test_handles_missing_dates_and_null_values():
    response = upload(excel_bytes({
        "Fecha": pd.to_datetime(["2026-01-01", None, "2026-01-03"]),
        "Ventas": [10, 20, None],
        "Marca": ["A", "B", "A"],
    }))
    assert response.status_code == 200
    result = response.json()
    assert result["rowCount"] == 3
    assert result["charts"]
