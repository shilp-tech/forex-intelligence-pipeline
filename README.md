# Forex Intelligence Pipeline

An end-to-end automated data engineering pipeline that ingests live USD/INR
exchange rate data, stores it in a cloud database, computes financial analytics,
and delivers a live dashboard plus automated daily email reports.

## Architecture
```
Alpha Vantage API → Python Ingestion → AWS S3 → Pandas Cleaning → 
AWS RDS PostgreSQL → Analytics Engine → Grafana Dashboard
                                      → Automated Email Report
```

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.14 |
| Data Processing | Pandas |
| Database | PostgreSQL on AWS RDS |
| Orchestration | Apache Airflow DAG + Cron |
| Dashboard | Grafana |
| Cloud | AWS (RDS + S3) |
| Data Source | Alpha Vantage API |

## Features

- **Live data ingestion** — pulls USD/INR OHLC data daily from Alpha Vantage API
- **Idempotent pipeline** — UPSERT logic prevents duplicate data on every run
- **Financial analytics** — computes SMA-7, SMA-14, daily volatility, daily change %
- **Automated scheduling** — cron job runs full pipeline every day at 9am
- **Live dashboard** — Grafana connected directly to AWS RDS showing real-time charts
- **Daily email report** — HTML formatted report sent automatically every morning

## Project Structure
```
forex-pipeline/
├── src/
│   ├── fetch_forex.py       # Fetch live data from Alpha Vantage API
│   ├── clean_forex.py       # Clean and transform with Pandas
│   ├── db_connect.py        # Database connection utility
│   ├── create_table.py      # Database schema creation
│   ├── load_to_db.py        # Load data with duplicate prevention
│   ├── analytics.py         # Compute SMA, volatility, daily change
│   └── email_report.py      # Generate and send daily HTML report
├── airflow/
│   └── dags/
│       └── forex_pipeline_dag.py  # Airflow DAG definition
├── data/                    # Local CSV storage
├── logs/                    # Pipeline execution logs
└── .env                     # Credentials (not committed to Git)
```

## Setup

1. Clone the repository
```bash
git clone https://github.com/shilp-tech/forex-intelligence-pipeline.git
cd forex-intelligence-pipeline
```

2. Create virtual environment
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

3. Configure environment variables
```bash
cp .env.example .env
# Fill in your credentials
```

4. Set up AWS RDS PostgreSQL database and run schema creation
```bash
python src/create_table.py
```

5. Run the pipeline
```bash
python src/load_to_db.py
python src/analytics.py
```

## Dashboard

Live Grafana dashboard showing:
- USD/INR price with 7-day and 14-day moving averages
- Daily volatility trends
- Daily change percentage bars

## Key Engineering Decisions

**Idempotency** — The pipeline uses PostgreSQL's `ON CONFLICT DO NOTHING` 
to ensure running the pipeline multiple times never creates duplicate data. 
This is critical for production reliability.

**Separation of concerns** — Each script handles exactly one responsibility. 
Fetch, clean, load, and analyze are all separate modules.

**Secure credentials** — All sensitive data stored in `.env` file, never 
committed to version control.

## Author

Shilp Patel — Masters in Advanced Data Analytics
