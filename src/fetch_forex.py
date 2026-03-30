# We are importing 3 libraries we installed earlier
import requests          # lets Python make calls to the internet
import json              # helps us read the data that comes back from the API
import os                # lets Python talk to your operating system
from dotenv import load_dotenv  # reads our secret API key from the .env file

# This line goes and reads your .env file and loads the API key into memory
load_dotenv()

# This line grabs the API key value and stores it in a variable called api_key
api_key = os.getenv("ALPHA_VANTAGE_API_KEY")

# This is the URL we are calling - like typing an address into a browser
# We are asking for EUR/USD exchange rate data
url = f"https://www.alphavantage.co/query?function=FX_DAILY&from_symbol=EUR&to_symbol=USD&apikey={api_key}"

# This line actually makes the call to the internet and gets the response back
response = requests.get(url)

# This converts the response into a Python dictionary we can work with
data = response.json()

# This prints the raw data so we can see what came back
print(data)