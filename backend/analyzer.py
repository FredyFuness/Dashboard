"""Infers column types from an uploaded spreadsheet and builds KPI / chart
specs that the frontend can render directly with Recharts."""

import io
import math
from typing import Any

import pandas as pd

from insights import build_insights

MAX_CATEGORIES = 10
MAX_CHARTS = 6
PREVIEW_ROWS = 50


def _clean(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
        return None
    if isinstance(value, (pd.Timestamp,)):
        return value.isoformat()
    if pd.isna(value):
        return None
    return value


def _clean_records(df: pd.DataFrame) -> list[dict[str, Any]]:
    return [{k: _clean(v) for k, v in row.items()} for row in df.to_dict(orient="records")]


def list_sheets(file_bytes: bytes) -> list[str]:
    with pd.ExcelFile(io.BytesIO(file_bytes)) as xls:
        return xls.sheet_names


def _read_sheet(file_bytes: bytes, sheet_name: str) -> pd.DataFrame:
    df = pd.read_excel(io.BytesIO(file_bytes), sheet_name=sheet_name)
    df = df.dropna(axis=1, how="all").dropna(axis=0, how="all")
    df.columns = [str(c).strip() for c in df.columns]
    return df


def _is_id_like(col_name: str, series: pd.Series, n_rows: int) -> bool:
    name = col_name.strip().lower()
    name_suggests_id = name == "id" or name.endswith("_id") or name.endswith(" id")
    if not name_suggests_id:
        return False
    return series.nunique(dropna=True) >= n_rows * 0.98


def _classify_columns(df: pd.DataFrame) -> dict[str, list[str]]:
    numeric, datetime_cols, categorical = [], [], []
    n_rows = len(df)

    for col in df.columns:
        series = df[col]

        if pd.api.types.is_datetime64_any_dtype(series):
            datetime_cols.append(col)
            continue

        if pd.api.types.is_numeric_dtype(series):
            if not _is_id_like(col, series, n_rows):
                numeric.append(col)
            continue

        parsed = pd.to_datetime(series, errors="coerce", format="mixed")
        if parsed.notna().mean() > 0.9:
            df[col] = parsed
            datetime_cols.append(col)
            continue

        n_unique = series.nunique(dropna=True)
        if 0 < n_unique <= max(n_rows * 0.9, MAX_CATEGORIES):
            categorical.append(col)

    return {"numeric": numeric, "datetime": datetime_cols, "categorical": categorical}


def _kpis(df: pd.DataFrame, numeric_cols: list[str]) -> list[dict[str, Any]]:
    kpis = []
    for col in numeric_cols[:6]:
        series = df[col].dropna()
        if series.empty:
            continue
        kpis.append(
            {
                "label": col,
                "sum": _clean(round(float(series.sum()), 2)),
                "avg": _clean(round(float(series.mean()), 2)),
                "min": _clean(round(float(series.min()), 2)),
                "max": _clean(round(float(series.max()), 2)),
                "count": int(series.count()),
            }
        )
    return kpis


def _time_series_charts(
    df: pd.DataFrame, datetime_cols: list[str], numeric_cols: list[str]
) -> list[dict[str, Any]]:
    charts = []
    if not datetime_cols or not numeric_cols:
        return charts

    date_col = datetime_cols[0]
    span_days = (df[date_col].max() - df[date_col].min()).days if len(df) > 1 else 0
    freq = "D" if span_days <= 90 else ("W" if span_days <= 730 else "MS")

    grouped = df.set_index(date_col).sort_index()
    metrics = numeric_cols[:3]
    agg = grouped[metrics].resample(freq).sum().reset_index()
    agg[date_col] = agg[date_col].dt.strftime("%Y-%m-%d")

    charts.append(
        {
            "type": "line",
            "title": f"Evolución en el tiempo por {date_col}",
            "xKey": date_col,
            "yKeys": metrics,
            "data": _clean_records(agg),
        }
    )
    return charts


def _categorical_charts(
    df: pd.DataFrame, categorical_cols: list[str], numeric_cols: list[str]
) -> list[dict[str, Any]]:
    charts = []
    metric = numeric_cols[0] if numeric_cols else None

    for cat_col in categorical_cols[:3]:
        if metric:
            grouped = (
                df.groupby(cat_col, dropna=True)[metric]
                .sum()
                .sort_values(ascending=False)
                .head(MAX_CATEGORIES)
                .reset_index()
            )
            grouped.rename(columns={metric: "value"}, inplace=True)
        else:
            grouped = (
                df[cat_col]
                .value_counts(dropna=True)
                .head(MAX_CATEGORIES)
                .rename_axis(cat_col)
                .reset_index(name="value")
            )

        chart_type = "pie" if df[cat_col].nunique(dropna=True) <= 8 else "bar"
        charts.append(
            {
                "type": chart_type,
                "title": f"{metric or 'Cantidad'} por {cat_col}",
                "xKey": cat_col,
                "yKeys": ["value"],
                "data": _clean_records(grouped),
            }
        )
    return charts


def build_dashboard(file_bytes: bytes, sheet_name: str | None = None) -> dict[str, Any]:
    sheets = list_sheets(file_bytes)
    selected_sheet = sheet_name if sheet_name in sheets else sheets[0]

    df = _read_sheet(file_bytes, selected_sheet)
    columns = _classify_columns(df)

    charts = [
        *_time_series_charts(df, columns["datetime"], columns["numeric"]),
        *_categorical_charts(df, columns["categorical"], columns["numeric"]),
    ][:MAX_CHARTS]

    return {
        "sheets": sheets,
        "selectedSheet": selected_sheet,
        "rowCount": len(df),
        "columns": columns,
        "kpis": _kpis(df, columns["numeric"]),
        "charts": charts,
        "insights": build_insights(df, columns),
        "preview": {
            "columns": list(df.columns),
            "rows": _clean_records(df.head(PREVIEW_ROWS)),
        },
    }
