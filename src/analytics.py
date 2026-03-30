import os
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# Load credentials from .env file
load_dotenv()

db_host     = os.getenv("DB_HOST")
db_name     = os.getenv("DB_NAME")
db_user     = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")

# Build connection and create engine
connection_string = f"postgresql://{db_user}:{db_password}@{db_host}:5432/{db_name}"
engine = create_engine(connection_string)

# ── STEP 1: PULL data from the database into Pandas ──────────────
# Instead of calling the API again we read directly from our database
# This is more efficient - we already stored the data, no need to fetch it again
with engine.connect() as connection:
    df = pd.read_sql(
        "SELECT * FROM forex_rates ORDER BY date ASC",
        connection
    )

print(f"Loaded {len(df)} rows from database")
print(df.head(3))

# ── STEP 2: COMPUTE analytics ────────────────────────────────────

# 7-day Simple Moving Average (SMA)
# This smooths out daily noise by averaging the last 7 closing prices
# Traders use this to spot trends - if price is above SMA it's bullish
df["sma_7"] = df["close"].rolling(window=7).mean().round(5)

# 14-day Simple Moving Average
# A slower moving average - used alongside sma_7 to spot crossovers
df["sma_14"] = df["close"].rolling(window=14).mean().round(5)

# Daily price change
# How much did the rate move from open to close each day?
# Positive = EUR strengthened, Negative = EUR weakened
df["daily_change"] = (df["close"] - df["open"]).round(5)

# Daily percentage change
# Same as above but expressed as a percentage - easier to compare across days
df["daily_change_pct"] = ((df["close"] - df["open"]) / df["open"] * 100).round(4)

# Daily volatility
# How wide was the price range that day? High - Low
# High volatility = big market moves, Low volatility = quiet market
df["volatility"] = (df["high"] - df["low"]).round(5)

# 7-day rolling volatility
# Average volatility over the last 7 days
# Tells us if the market is getting more or less volatile over time
df["volatility_7d"] = df["volatility"].rolling(window=7).mean().round(5)

print("\nAnalytics computed. Sample of last 5 rows:")
print(df[["date", "close", "sma_7", "sma_14",
          "daily_change_pct", "volatility"]].tail(5))

# ── STEP 3: SAVE analytics back to database ───────────────────────
# We need to add these new columns to our existing table
# First let's add the columns if they don't exist yet
add_columns_sql = """
ALTER TABLE forex_rates
    ADD COLUMN IF NOT EXISTS sma_7             NUMERIC(10,5),
    ADD COLUMN IF NOT EXISTS sma_14            NUMERIC(10,5),
    ADD COLUMN IF NOT EXISTS daily_change      NUMERIC(10,5),
    ADD COLUMN IF NOT EXISTS daily_change_pct  NUMERIC(10,4),
    ADD COLUMN IF NOT EXISTS volatility        NUMERIC(10,5),
    ADD COLUMN IF NOT EXISTS volatility_7d     NUMERIC(10,5);
"""

with engine.connect() as connection:
    # Add the new columns to the table
    connection.execute(text(add_columns_sql))
    connection.commit()

    # Now update each row with its computed analytics values
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

    connection.commit()

print(f"\nAnalytics saved to database for {updated} rows")
print("Columns added: sma_7, sma_14, daily_change, daily_change_pct, volatility, volatility_7d")