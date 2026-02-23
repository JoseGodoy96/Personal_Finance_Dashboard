import sqlite3
from pathlib import Path

DB_PATH = Path("finance.db")

SCHEMA_SQL = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS transactions (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    date      TEXT NOT NULL,         -- ISO date: YYYY-MM-DD
    concept         TEXT,
    movement        TEXT,
    amount          REAL NOT NULL,
    currency        TEXT,
    balance         REAL,
    notes           TEXT,

    -- Para deduplicar (evitar importar el mismo movimiento dos veces)
    hash_uid        TEXT NOT NULL UNIQUE,

    -- Para categorización futura
    category        TEXT,
    category_source TEXT DEFAULT 'rule',   -- rule | ml | manual

    created_at      TEXT DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_transactions_date ON transactions(date);
CREATE INDEX IF NOT EXISTS idx_transactions_amount ON transactions(amount);
"""

def main() -> None:
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.executescript(SCHEMA_SQL)
        conn.commit()
        print(f"✅ DB lista: {DB_PATH.resolve()}")
        cur = conn.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
        print("Tablas:", [r[0] for r in cur.fetchall()])
    finally:
        conn.close()

if __name__ == "__main__":
    main()