import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# Load credentials from .env file
load_dotenv()

db_host     = os.getenv("DB_HOST")
db_name     = os.getenv("DB_NAME")
db_user     = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")

# Build connection string and create engine
connection_string = f"postgresql://{db_user}:{db_password}@{db_host}:5432/{db_name}"
engine = create_engine(connection_string)

# This is the SQL command that creates our table
# Think of this as designing the columns of a spreadsheet before adding data
create_table_sql = """
CREATE TABLE IF NOT EXISTS forex_rates (
    id               SERIAL PRIMARY KEY,
    currency_pair    VARCHAR(10) NOT NULL,
    date             DATE NOT NULL,
    open             NUMERIC(10, 5) NOT NULL,
    high             NUMERIC(10, 5) NOT NULL,
    low              NUMERIC(10, 5) NOT NULL,
    close            NUMERIC(10, 5) NOT NULL,
    created_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(currency_pair, date)
);
"""

# Connect and run the SQL command
with engine.connect() as connection:
    connection.execute(text(create_table_sql))
    # commit() saves the change permanently to the database
    connection.commit()
    print("Table forex_rates created successfully!")
    print("Columns: id, currency_pair, date, open, high, low, close, created_at")