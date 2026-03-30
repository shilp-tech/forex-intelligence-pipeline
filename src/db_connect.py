# Import the libraries we need
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# Load all the database credentials from our .env file
load_dotenv()

db_host     = os.getenv("DB_HOST")
db_name     = os.getenv("DB_NAME")
db_user     = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")

# Build the connection string - this is like a URL that tells SQLAlchemy
# exactly how to find and connect to our database
# Format is: postgresql://username:password@host:port/database_name
connection_string = f"postgresql://{db_user}:{db_password}@{db_host}:5432/{db_name}"

# Create the engine - think of this as opening a phone line to the database
# The engine doesn't connect immediately, it just gets ready to connect
engine = create_engine(connection_string)

# Now actually test the connection by running a simple SQL command
# 'with engine.connect()' opens the connection and auto-closes it when done
with engine.connect() as connection:
    # text() wraps our SQL query so SQLAlchemy can understand it
    # SELECT 1 is the simplest possible SQL query - just returns the number 1
    # We use it purely to test if the connection works
    result = connection.execute(text("SELECT 1"))
    print("Database connection successful!")
    print(f"Connected to: {db_host}")
    print(f"Database: {db_name}")