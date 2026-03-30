import os
import requests
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# Load credentials from .env file
load_dotenv()

api_key     = os.getenv("ALPHA_VANTAGE_API_KEY")
db_host     = os.getenv("DB_HOST")
db_name     = os.getenv("DB_NAME")
db_user     = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")

# ── STEP 1: FETCH data from the API ──────────────────────────────
url = f"https://www.alphavantage.co/query?function=FX_DAILY&from_symbol=EUR&to_symbol=USD&apikey={api_key}"
response = requests.get(url)
data = response.json()

# Pull out just the price data section
raw_prices = data["Time Series FX (Daily)"]

# ── STEP 2: CLEAN the data with Pandas ───────────────────────────
df = pd.DataFrame.from_dict(raw_prices, orient="index")

# Rename columns to clean names
df.columns = ["open", "high", "low", "close"]

# Convert text numbers to real decimal numbers
df["open"]  = df["open"].astype(float)
df["high"]  = df["high"].astype(float)
df["low"]   = df["low"].astype(float)
df["close"] = df["close"].astype(float)

# Move date from index into its own column
df.index.name = "date"
df = df.reset_index()

# Convert date column to proper date format
df["date"] = pd.to_datetime(df["date"])

# Sort oldest to newest
df = df.sort_values("date").reset_index(drop=True)

# Add currency pair column
df["currency_pair"] = "EUR/USD"

print(f"Fetched {len(df)} rows from API")

# ── STEP 3: LOAD into the database ───────────────────────────────
connection_string = f"postgresql://{db_user}:{db_password}@{db_host}:5432/{db_name}"
engine = create_engine(connection_string)

# Keep track of how many rows we actually insert
inserted = 0
skipped  = 0

with engine.connect() as connection:
    for _, row in df.iterrows():
        # This is our UPSERT logic - remember the duplicate problem you spotted?
        # ON CONFLICT DO NOTHING means: if this date+pair already exists, skip it
        # This is how we prevent duplicate data every time the pipeline runs
        sql = text("""
            INSERT INTO forex_rates (currency_pair, date, open, high, low, close)
            VALUES (:currency_pair, :date, :open, :high, :low, :close)
            ON CONFLICT (currency_pair, date) DO NOTHING
        """)

        result = connection.execute(sql, {
            "currency_pair": row["currency_pair"],
            "date":          row["date"],
            "open":          row["open"],
            "high":          row["high"],
            "low":           row["low"],
            "close":         row["close"]
        })

        # rowcount tells us if a row was actually inserted (1) or skipped (0)
        if result.rowcount == 1:
            inserted += 1
        else:
            skipped += 1

    # Save all inserts permanently to the database
    connection.commit()

print(f"Rows inserted: {inserted}")
print(f"Rows skipped (duplicates): {skipped}")
print(f"Total rows now in database: {inserted + skipped}")
print("Data successfully loaded into AWS RDS!")