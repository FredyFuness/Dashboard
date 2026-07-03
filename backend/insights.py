"""Rule-based analysis that turns the classified dataframe into plain-language
warnings, opportunities and suggested actions for the dashboard."""

from typing import Any

import pandas as pd

MAX_INSIGHTS = 8


def _missing_data_insights(df: pd.DataFrame) -> list[dict[str, Any]]:
    insights = []
    for col in df.columns:
        null_pct = df[col].isna().mean()
        if null_pct > 0.15:
            insights.append(
                {
                    "severity": "warning",
                    "title": f'Datos incompletos en "{col}"',
                    "description": f'El {null_pct * 100:.0f}% de los valores de "{col}" están vacíos.',
                    "suggestion": "Revisá la fuente del archivo para completar los valores faltantes antes de sacar conclusiones.",
                }
            )
    return insights


def _trend_insights(df: pd.DataFrame, datetime_cols: list[str], numeric_cols: list[str]) -> list[dict[str, Any]]:
    if not datetime_cols or not numeric_cols:
        return []

    date_col = datetime_cols[0]
    sorted_df = df.sort_values(date_col)
    half = len(sorted_df) // 2
    if half < 3:
        return []

    insights = []
    for col in numeric_cols[:4]:
        first_half = sorted_df[col].iloc[:half].mean()
        second_half = sorted_df[col].iloc[half:].mean()
        if pd.isna(first_half) or pd.isna(second_half) or first_half == 0:
            continue

        change = (second_half - first_half) / abs(first_half) * 100
        if change <= -15:
            insights.append(
                {
                    "severity": "danger",
                    "title": f"{col} en baja",
                    "description": f"{col} cayó un {abs(change):.0f}% comparando la primera mitad del período con la segunda.",
                    "suggestion": f'Investigá qué cambió recientemente en "{col}" (estacionalidad, precios, demanda) y definí un plan para revertir la tendencia.',
                }
            )
        elif change >= 15:
            insights.append(
                {
                    "severity": "success",
                    "title": f"{col} en alza",
                    "description": f"{col} creció un {change:.0f}% comparando la primera mitad del período con la segunda.",
                    "suggestion": f'Identificá qué está funcionando bien en "{col}" para reforzarlo o replicarlo en otras áreas.',
                }
            )
    return insights


def _category_insights(df: pd.DataFrame, categorical_cols: list[str], numeric_cols: list[str]) -> list[dict[str, Any]]:
    if not categorical_cols or not numeric_cols:
        return []

    metric = numeric_cols[0]
    insights = []
    for cat_col in categorical_cols[:2]:
        grouped = df.groupby(cat_col, dropna=True)[metric].sum().sort_values(ascending=False)
        if len(grouped) < 2:
            continue

        total = grouped.sum()
        top_name, top_value = grouped.index[0], grouped.iloc[0]
        if total:
            top_share = top_value / total * 100
            if top_share >= 50:
                insights.append(
                    {
                        "severity": "info",
                        "title": f'Concentración en "{top_name}"',
                        "description": f'"{top_name}" representa el {top_share:.0f}% del total de {metric} agrupado por {cat_col}.',
                        "suggestion": f'Evaluá si depender tanto de "{top_name}" es un riesgo, y considerá reforzar o diversificar las demás categorías de {cat_col}.',
                    }
                )

        worst_name, worst_value = grouped.index[-1], grouped.iloc[-1]
        avg = grouped.mean()
        if avg and worst_value < avg * 0.5:
            insights.append(
                {
                    "severity": "warning",
                    "title": f'"{worst_name}" muy por debajo del promedio',
                    "description": f'"{worst_name}" tiene un total de {metric} muy por debajo del resto de las categorías de {cat_col}.',
                    "suggestion": f'Revisá si hay una causa puntual (recursos, cobertura, estacionalidad) que explique el bajo desempeño de "{worst_name}" y definí acciones correctivas.',
                }
            )
    return insights


def _outlier_insights(df: pd.DataFrame, numeric_cols: list[str]) -> list[dict[str, Any]]:
    insights = []
    for col in numeric_cols[:4]:
        series = df[col].dropna()
        if len(series) < 5:
            continue

        q1, q3 = series.quantile([0.25, 0.75])
        iqr = q3 - q1
        if iqr == 0:
            continue

        upper, lower = q3 + 1.5 * iqr, q1 - 1.5 * iqr
        outliers = series[(series > upper) | (series < lower)]
        if len(outliers) > 0:
            insights.append(
                {
                    "severity": "info",
                    "title": f'Valores atípicos en "{col}"',
                    "description": f'Se detectaron {len(outliers)} valores fuera del rango esperado en "{col}".',
                    "suggestion": "Verificá si son errores de carga de datos o casos reales excepcionales que merecen atención especial.",
                }
            )
    return insights


def build_insights(df: pd.DataFrame, columns: dict[str, list[str]]) -> list[dict[str, Any]]:
    insights = [
        *_trend_insights(df, columns["datetime"], columns["numeric"]),
        *_category_insights(df, columns["categorical"], columns["numeric"]),
        *_outlier_insights(df, columns["numeric"]),
        *_missing_data_insights(df),
    ]
    return insights[:MAX_INSIGHTS]
