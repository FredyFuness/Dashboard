import numpy as np
import pandas as pd

rng = pd.date_range("2024-01-01", periods=120, freq="D")
np.random.seed(0)
df = pd.DataFrame(
    {
        "Fecha": rng,
        "Region": np.random.choice(["Norte", "Sur", "Este", "Oeste"], size=120),
        "Producto": np.random.choice(["A", "B", "C"], size=120),
        "Ventas": np.random.randint(100, 5000, size=120),
        "Costo": np.random.uniform(50, 2000, size=120).round(2),
        "ID": range(1, 121),
    }
)
df.to_excel("../test_data.xlsx", index=False, sheet_name="Ventas")
print("created")
