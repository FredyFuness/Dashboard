import numpy as np
import pandas as pd

rng = pd.date_range("2024-01-01", periods=120, freq="D")
np.random.seed(1)

# Ventas trending down hard: high in first half, low in second half
ventas = np.concatenate([
    np.random.randint(4000, 5000, size=60),
    np.random.randint(500, 1500, size=60),
])

region = np.random.choice(["Norte", "Sur", "Este", "Oeste"], size=120, p=[0.7, 0.1, 0.1, 0.1])
costo = np.random.uniform(50, 2000, size=120).round(2)
costo[::10] = np.nan  # ~10% missing

df = pd.DataFrame(
    {
        "Fecha": rng,
        "Region": region,
        "Producto": np.random.choice(["A", "B", "C"], size=120),
        "Ventas": ventas,
        "Costo": costo,
        "ID": range(1, 121),
    }
)
df.to_excel("../test_data2.xlsx", index=False, sheet_name="Ventas")
print("created")
