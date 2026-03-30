# Import the libraries we need
import requests          # to call the API
import pandas as pd      # to clean and organize the data
import os                # to talk to the operating system
from dotenv import load_dotenv  # to read our API key from .env

# Load the API key from .env file
load_dotenv()
api_key = os.getenv("ALPHA_VANTAGE_API_KEY")

# Call the API - same as before
url = f"https://www.alphavantage.co/query?function=FX_DAILY&from_symbol=EUR&to_symbol=USD&apikey={api_key}"
response = requests.get(url)
data = response.json()

# Pull out just the price data section - ignore the Meta Data section
# Think of this like saying "give me only the second drawer, not the whole cabinet"
raw_prices = data["Time Series FX (Daily)"]

# Convert the raw data into a Pandas DataFrame - this is our clean table
# pd.DataFrame.from_dict turns the messy dictionary into rows and columns
df = pd.DataFrame.from_dict(raw_prices, orient="index")

# Rename the columns to clean readable names
# The API gives ugly names like "1. open" - we rename them to just "open"
df.columns = ["open", "high", "low", "close"]

# Convert the number columns from text to actual decimal numbers
# Right now "1.15270" is just text - we need it to be a real number for math later
df["open"]  = df["open"].astype(float)
df["high"]  = df["high"].astype(float)
df["low"]   = df["low"].astype(float)
df["close"] = df["close"].astype(float)

# The dates are currently the index - move them into their own proper column
df.index.name = "date"
df = df.reset_index()

# Convert the date column to a proper date format
# Right now "2026-03-27" is just text - we tell Pandas it's a real date
df["date"] = pd.to_datetime(df["date"])

# Sort by date so oldest is at top, newest at bottom
df = df.sort_values("date").reset_index(drop=True)

# Add a column to record which currency pair this data is for
df["currency_pair"] = "EUR/USD"

# Print the clean table so we can see it
print(df)
print(f"\nTotal rows: {len(df)}")
print(f"\nLatest date: {df['date'].max()}")
print(f"Oldest date: {df['date'].min()}")



# Save the clean data to a CSV file in our data folder
# index=False means don't write the row numbers (0,1,2...) into the file
df.to_csv("data/EUR_USD_clean.csv", index=False)

print("\nData saved to data/EUR_USD_clean.csv")