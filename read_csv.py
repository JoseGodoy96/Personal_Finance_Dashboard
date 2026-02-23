import hashlib
import sqlite3
from pathlib import Path

import pandas as pd

DB_PATH = Path("finance.db")
EXCEL_PATH = Path("example.xlsx")


def clean_text(x) -> str:
    if pd.isna(x):
        return ""
    s = str(x).strip().lower()
    s = " ".join(s.split())
    return s


def make_hash_uid(date, amount, concept, movement, currency) -> str:
    base = f"{date}|{amount:.2f}|{concept}|{movement}|{currency}"
    return hashlib.sha1(base.encode("utf-8")).hexdigest()


def main() -> None:
    if not EXCEL_PATH.exists():
        raise FileNotFoundError(f"No existe: {EXCEL_PATH.resolve()}")
    if not DB_PATH.exists():
        raise FileNotFoundError(f"No existe: {DB_PATH.resolve()} (corré db_init.py)")
    df = pd.read_excel(EXCEL_PATH, header=4)
    df = df.dropna(how="all")
    df["Fecha"] = pd.to_datetime(df["Fecha"], dayfirst=True, errors="coerce")
    df["Importe"] = pd.to_numeric(df["Importe"], errors="coerce")
    df["Disponible"] = pd.to_numeric(df["Disponible"], errors="coerce")
    df = df.dropna(subset=["Fecha", "Importe"])
    rows = []
    for _, r in df.iterrows():
        date = r["Fecha"].date().isoformat() if pd.notna(r["Fecha"]) else None
        concept = str(r.get("Concepto", "") if pd.notna(r.get("Concepto")) else "").strip()
        movement = str(r.get("Movimiento", "") if pd.notna(r.get("Movimiento")) else "").strip()
        currency = str(r.get("Divisa", "") if pd.notna(r.get("Divisa")) else "").strip()
        amount = float(r["Importe"])
        balance = float(r["Disponible"]) if pd.notna(r.get("Disponible")) else None
        notes = str(r.get("Observaciones", "") if pd.notna(r.get("Observaciones")) else "").strip() or None
        hash_uid = make_hash_uid(
            date=date,
            amount=amount,
            concept=clean_text(concept),
            movement=clean_text(movement),
            currency=currency.upper(),
        )

        rows.append(
            (
                date,
                concept,
                movement,
                amount,
                currency,
                balance,
                notes,
                hash_uid,
            )
        )
    sql = """
    INSERT OR IGNORE INTO transactions
    (date, concept, movement, amount, currency, balance, notes, hash_uid)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?);
    """

    conn = sqlite3.connect(DB_PATH)
    try:
        cur = conn.cursor()
        before = cur.execute("SELECT COUNT(*) FROM transactions;").fetchone()[0]
        cur.executemany(sql, rows)
        conn.commit()
        after = cur.execute("SELECT COUNT(*) FROM transactions;").fetchone()[0]
        inserted = after - before
        print(f"✅ Leídas del Excel: {len(df)}")
        print(f"✅ Intentadas insertar: {len(rows)}")
        print(f"✅ Insertadas nuevas: {inserted}")
        print(f"📦 Total en DB: {after}")

    finally:
        conn.close()


if __name__ == "__main__":
    main()