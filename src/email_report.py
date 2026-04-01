import os
import smtplib
import pandas as pd
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# Load credentials from .env file
load_dotenv()

db_host        = os.getenv("DB_HOST")
db_name        = os.getenv("DB_NAME")
db_user        = os.getenv("DB_USER")
db_password    = os.getenv("DB_PASSWORD")
email_sender   = os.getenv("EMAIL_SENDER")
email_password = os.getenv("EMAIL_PASSWORD")
email_receiver = os.getenv("EMAIL_RECEIVER")

# Connect to database and pull latest 7 days of data
connection_string = f"postgresql://{db_user}:{db_password}@{db_host}:5432/{db_name}"
engine = create_engine(connection_string)

with engine.connect() as connection:
    result = connection.execute(text("""
        SELECT date, close, sma_7, daily_change_pct, volatility
        FROM forex_rates
        WHERE currency_pair = 'USD/INR'
        ORDER BY date DESC
        LIMIT 7
    """))
    df = pd.DataFrame(result.fetchall(), columns=result.keys())

# Get the most recent row for the summary
latest = df.iloc[0]

# Build the email subject
subject = f"Forex Daily Report — USD/INR {latest['date'].strftime('%Y-%m-%d')}"

# Build the email body in HTML so it looks professional
html_body = f"""
<html>
<body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">

<h2 style="color: #2c3e50;">Forex Intelligence Report</h2>
<h3 style="color: #7f8c8d;">USD/INR — {latest['date'].strftime('%B %d, %Y')}</h3>

<table style="width:100%; border-collapse: collapse; margin: 20px 0;">
  <tr style="background-color: #3498db; color: white;">
    <td style="padding: 10px;">Closing Price</td>
    <td style="padding: 10px;"><strong>{latest['close']:.5f}</strong></td>
  </tr>
  <tr style="background-color: #f2f2f2;">
    <td style="padding: 10px;">7-Day Moving Average</td>
    <td style="padding: 10px;">{latest['sma_7']:.5f}</td>
  </tr>
  <tr>
    <td style="padding: 10px;">Daily Change</td>
    <td style="padding: 10px; color: {'green' if latest['daily_change_pct'] > 0 else 'red'};">
      {latest['daily_change_pct']:+.4f}%
    </td>
  </tr>
  <tr style="background-color: #f2f2f2;">
    <td style="padding: 10px;">Daily Volatility</td>
    <td style="padding: 10px;">{latest['volatility']:.5f}</td>
  </tr>
</table>

<h3 style="color: #2c3e50;">Last 7 Days</h3>
<table style="width:100%; border-collapse: collapse;">
  <tr style="background-color: #2c3e50; color: white;">
    <th style="padding: 8px;">Date</th>
    <th style="padding: 8px;">Close</th>
    <th style="padding: 8px;">Change %</th>
    <th style="padding: 8px;">Volatility</th>
  </tr>
"""

# Add a row for each of the last 7 days
for _, row in df.iterrows():
    color = "green" if row['daily_change_pct'] > 0 else "red"
    html_body += f"""
  <tr style="border-bottom: 1px solid #ddd;">
    <td style="padding: 8px;">{row['date'].strftime('%Y-%m-%d')}</td>
    <td style="padding: 8px;">{row['close']:.5f}</td>
    <td style="padding: 8px; color: {color};">{row['daily_change_pct']:+.4f}%</td>
    <td style="padding: 8px;">{row['volatility']:.5f}</td>
  </tr>
"""

html_body += """
</table>

<p style="color: #7f8c8d; font-size: 12px; margin-top: 30px;">
  Generated automatically by Forex Intelligence Pipeline
</p>

</body>
</html>
"""

# Set up the email
message = MIMEMultipart("alternative")
message["Subject"] = subject
message["From"]    = email_sender
message["To"]      = email_receiver
message.attach(MIMEText(html_body, "html"))

# Send via Gmail SMTP
with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
    server.login(email_sender, email_password)
    server.sendmail(email_sender, email_receiver, message.as_string())

print(f"Email report sent to {email_receiver}")
print(f"Subject: {subject}")
