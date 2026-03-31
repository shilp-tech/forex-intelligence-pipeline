import os
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

db_host     = os.getenv("DB_HOST")
db_name     = os.getenv("DB_NAME")
db_user     = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")

connection_string = f"postgresql://{db_user}:{db_password}@{db_host}:5432/{db_name}"
engine = create_engine(connection_string)

with engine.connect() as connection:
    result = connection.execute(text("SELECT * FROM forex_rates ORDER BY date ASC"))
    df = pd.DataFrame(result.fetchall(), columns=result.keys())

print(f"Loaded {len(df)} rows from database")

df["sma_7"]            = df["close"].rolling(window=7).mean().round(5)
df["sma_14"]           = df["close"].rolling(window=14).mean().round(5)
df["daily_change"]     = (df["close"] - df["open"]).round(5)
df["daily_change_pct"] = ((df["close"] - df["open"]) / df["open"] * 100).round(4)
df["volatility"]       = (df["high"] - df["low"]).round(5)
df["volatility_7d"]    = df["volatility"].rolling(window=7).mean().round(5)

print("\nSample of last 5 rows:")
print(df[["date", "close", "sma_7", "sma_14", "daily_change_pct", "volatility"]].tail(5))

add_columns_sql = """
ALTER TABLE forex_rates
    ADD COLUMN IF NOT EXISTS sma_7             NUMERIC(10,5),
    ADD COLUMN IF NOT EXISTS sma_14            NUMERIC(10,5),
    ADD COLUMN IF NOT EXISTS daily_change      NUMERIC(10,5),
    ADD COLUMN IF NOT EXISTS daily_change_pct  NUMERIC(10,4),
    ADD COLUMN IF NOT EXISTS volatility        NUMERIC(10,5),
    ADD COLUMN IF NOT EXISTS volatility_7d     NUMERIC(10,5);
"""

with engine.begin() as connection:
    connection.execute(text(add_columns_sql))

    updated = 0
    for _, row in df.iterrows():
        sql = text("""
            UPDATE forex_rates
            SET
                sma_7            = :sma_7,
                sma_14           = :sma_14,
                daily_change     = :daily_change,
                daily_change_pct = :daily_change_pct,
                volatility       = :volatility,
                volatility_7d    = :volatility_7d
            WHERE date = :date AND currency_pair = :currency_pair
        """)
        connection.execute(sql, {
            "sma_7":            None if pd.isna(row["sma_7"]) else row["sma_7"],
            "sma_14":           None if pd.isna(row["sma_14"]) else row["sma_14"],
            "daily_change":     row["daily_change"],
            "daily_change_pct": row["daily_change_pct"],
            "volatility":       row["volatility"],
            "volatility_7d":    None if pd.isna(row["volatility_7d"]) else row["volatility_7d"],
            "date":             row["date"],
            "currency_pair":    row["currency_pair"]
        })
        updated += 1

print(f"\nAnalytics saved to database for {updated} rows")