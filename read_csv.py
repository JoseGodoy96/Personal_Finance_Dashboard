import pandas as pd

df = pd.read_excel("example.xlsx", header=4)

df = df.dropna(how="all")

df["Fecha"] = pd.to_datetime(df["Fecha"], dayfirst=True, errors="coerce")
df["Importe"] = pd.to_numeric(df["Importe"], errors="coerce")
df["Disponible"] = pd.to_numeric(df["Disponible"], errors="coerce")
df = df[["Fecha", "Concepto", "Movimiento", "Importe", "Disponible"]]

df = df.rename(columns={
    "Fecha": "date",
    "Concepto": "concept",
    "Movimiento": "movement",
    "Importe": "amount",
    "Disponible": "balance",
})
total_gastos = df.loc[df["amount"] < 0, "amount"].sum()
total_ingresos = df.loc[df["amount"] > 0, "amount"].sum()
neto = total_ingresos + total_gastos

