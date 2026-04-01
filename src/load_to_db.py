import os
import requests
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

api_key     = os.getenv("ALPHA_VANTAGE_API_KEY")
db_host     = os.getenv("DB_HOST")
db_name     = os.getenv("DB_NAME")
db_user     = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")

url = f"https://www.alphavantage.co/query?function=FX_DAILY&from_symbol=USD&to_symbol=INR&apikey={api_key}"
response = requests.get(url)
data = response.json()

raw_prices = data["Time Series FX (Daily)"]

df = pd.DataFrame.from_dict(raw_prices, orient="index")
df.columns = ["open", "high", "low", "close"]
df["open"]  = df["open"].astype(float)
df["high"]  = df["high"].astype(float)
df["low"]   = df["low"].astype(float)
df["close"] = df["close"].astype(float)
df.index.name = "date"
df = df.reset_index()
df["date"] = pd.to_datetime(df["date"])
df = df.sort_values("date").reset_index(drop=True)
df["currency_pair"] = "USD/INR"

print(f"Fetched {len(df)} rows from API")

connection_string = f"postgresql://{db_user}:{db_password}@{db_host}:5432/{db_name}"
engine = create_engine(connection_string)

inserted = 0
skipped  = 0

with engine.begin() as connection:
    for _, row in df.iterrows():
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
        if result.rowcount == 1:
            inserted += 1
        else:
            skipped += 1

print(f"Rows inserted: {inserted}")
print(f"Rows skipped (duplicates): {skipped}")
print(f"Total rows now in database: {inserted + skipped}")
print("Data successfully loaded into AWS RDS!")
