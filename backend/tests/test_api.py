import io
from zipfile import ZipFile, ZIP_DEFLATED

import pandas as pd
from fastapi.testclient import TestClient

from main import MAX_UPLOAD_BYTES, MAX_UNCOMPRESSED_BYTES, app

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


def test_rejects_arbitrary_zip_renamed_to_xlsx():
    buffer = io.BytesIO()
    with ZipFile(buffer, "w") as archive:
        archive.writestr("notes.txt", "This is not an Excel workbook")
    response = upload(buffer.getvalue())
    assert response.status_code == 400
    assert "estructura" in response.json()["detail"]


def test_rejects_zip_expansion_bomb():
    buffer = io.BytesIO()
    with ZipFile(buffer, "w", compression=ZIP_DEFLATED) as archive:
        archive.writestr("[Content_Types].xml", "test")
        archive.writestr("xl/workbook.xml", "test")
        archive.writestr("xl/worksheets/sheet1.xml", b"x" * (MAX_UNCOMPRESSED_BYTES + 1))
    response = upload(buffer.getvalue())
    assert response.status_code == 413


def test_selects_requested_sheet():
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        pd.DataFrame({"Total": [1, 2]}).to_excel(writer, sheet_name="Uno", index=False)
        pd.DataFrame({"Total": [5, 10, 15]}).to_excel(writer, sheet_name="Dos", index=False)
    response = upload(buffer.getvalue(), sheet_name="Dos")
    assert response.status_code == 200
    result = response.json()
    assert result["sheets"] == ["Uno", "Dos"]
    assert result["selectedSheet"] == "Dos"
    assert result["rowCount"] == 3
    assert result["kpis"][0]["sum"] == 30


def test_accepts_xlsm_extension_for_valid_workbook():
    assert upload(excel_bytes(), name="datos.xlsm").status_code == 200


def test_rejects_columns_duplicated_after_whitespace_trimming():
    response = upload(excel_bytes({"Monto": [1, 2], " Monto ": [3, 4]}))
    assert response.status_code == 400
    assert "duplicados" in response.json()["detail"]


def test_category_named_value_keeps_chart_series_distinct():
    response = upload(excel_bytes({"value": ["A", "B", "B"], "Ventas": [2, 3, 4]}))
    assert response.status_code == 200
    chart = response.json()["charts"][0]
    assert chart["xKey"] == "value"
    assert chart["yKeys"] == ["_dashboard_value"]
    assert "value" in chart["data"][0]
    assert "_dashboard_value" in chart["data"][0]


def test_category_named_value_without_metric():
    response = upload(excel_bytes({"value": ["A", "B", "B"]}))
    assert response.status_code == 200
    chart = response.json()["charts"][0]
    assert chart["xKey"] == "value"
    assert chart["yKeys"] == ["_dashboard_value"]


def test_preview_is_limited_to_50_rows():
    response = upload(excel_bytes({"Monto": list(range(70))}))
    assert response.status_code == 200
    result = response.json()
    assert result["rowCount"] == 70
    assert len(result["preview"]["rows"]) == 50


def test_unexpected_error_does_not_leak_in_http_response(monkeypatch):
    def fail(*_args, **_kwargs):
        raise RuntimeError("secret internal detail")
    monkeypatch.setattr("main.build_dashboard", fail)
    response = upload(excel_bytes())
    assert response.status_code == 422
    assert "secret internal detail" not in response.text
