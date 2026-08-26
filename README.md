# 🇧🇩 Bangladesh Financial Data Platform

A full-stack data engineering platform that collects, cleans, warehouses, streams, and visualizes real Bangladesh economic and financial data — exchange rates, inflation, foreign reserves, trade, and workers' remittances — end to end, from raw government sources to a live dashboard.

Built as a learning project to practice real-world data engineering: messy real data, a proper warehouse schema, orchestrated batch pipelines, event streaming, a documented API, and a working frontend.

---

## Architecture

```
Bangladesh Bank / World Bank / Exchange Rate API
                    │
                    ▼
         Python ingestion clients (Phase 1)
                    │
                    ▼
              Raw JSON / Excel
           (data/raw/, date-partitioned)
                    │
                    ▼
        ┌───────────┴───────────┐
        │                       │
  Airflow DAG              Kafka producer
  (daily batch)          (30s polling loop)
        │                       │
        ▼                       ▼
   ETL loaders              Kafka topic
  (src/loaders/)        (exchange_rates_stream)
        │                       │
        │                       ▼
        │                 Kafka consumer
        │                       │
        └───────────┬───────────┘
                     ▼
            PostgreSQL warehouse
         (star schema: dim_* + fact_*)
                     │
                     ▼
              FastAPI backend
        (REST endpoints + WebSocket)
                     │
                     ▼
             React dashboard
       (Vite + Tailwind + Recharts)
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Ingestion | Python, `requests`, `pandas`, `openpyxl` |
| Orchestration | Apache Airflow (Docker, CeleryExecutor) |
| Streaming | Apache Kafka (KRaft mode, Docker) |
| Warehouse | PostgreSQL 18 |
| Backend API | FastAPI, SQLAlchemy, Pydantic, WebSocket |
| Frontend | React (Vite), Tailwind CSS v4, Recharts, react-router-dom |
| Containers | Docker Desktop, Docker Compose |

---

## Data Sources

| Dataset | Source | Notes |
|---|---|---|
| Exchange rates (live) | [open.er-api.com](https://open.er-api.com) | Free, no API key. Polled every 30s via Kafka producer, and daily via Airflow batch. |
| Inflation, reserves, remittance (historical) | [World Bank Indicators API](https://api.worldbank.org/v2) | Annual data, calendar-year based. |
| Trade (exports/imports) | [Bangladesh Bank — Historical Time Series (1972–2024)](https://www.bb.org.bd/en/index.php/econdata/index) | Fiscal-year based (July–June). Parsed from a raw multi-sheet Excel file. |

**Data honesty note:** where source data had genuine gaps — for example, Bangladesh Bank did not publish USD trade figures for fiscal years 1973–74 through 1987–88 — those years are simply absent from `fact_trade` rather than filled in with estimates or interpolated values. No number in this platform is fabricated.

---

## Project Structure

```
bd-financial-platform/
├── src/
│   ├── clients/           # API clients (exchange rate, World Bank, BB downloader)
│   ├── loaders/            # ETL scripts: raw files → PostgreSQL
│   ├── streaming/          # Kafka producer & consumer
│   ├── api/                # FastAPI app, routers, schemas
│   ├── config.py
│   ├── db.py
│   ├── logger.py
│   └── run_ingestion.py    # Phase 1 batch entrypoint
├── sql/
│   └── 001_create_schema.sql
├── airflow/
│   ├── docker-compose.yaml
│   └── dags/bd_financial_pipeline.py
├── kafka/
│   └── docker-compose.yaml
├── frontend/                # React dashboard (Vite)
├── data/raw/                 # Ingested raw files (gitignored)
└── requirements.txt
```

---

## Prerequisites

- Python 3.12+
- Node.js 18+ and npm
- PostgreSQL 18 (or compatible)
- Docker Desktop (for Airflow and Kafka)
- Git

---

## First-Time Setup

### 1. Clone and create a virtual environment

```bash
git clone https://github.com/mashraf02/bd-financial-platform.git
cd bd-financial-platform
python -m venv venv
source venv/Scripts/activate   # Windows Git Bash
pip install -r requirements.txt
```

### 2. Set up environment variables

Create a `.env` file in the project root:

```env
DATA_ROOT=./data/raw
LOG_LEVEL=INFO

DB_HOST=localhost
DB_PORT=5432
DB_NAME=bd_financial
DB_USER=postgres
DB_PASSWORD=your_postgres_password
```

### 3. Create the database and schema

```bash
psql -U postgres -c "CREATE DATABASE bd_financial;"
psql -U postgres -d bd_financial -f sql/001_create_schema.sql
```

### 4. Populate dimension tables

```bash
python -m src.populate_dim_date
python -m src.populate_dim_lookups
```

### 5. Run initial ingestion and load

```bash
python -m src.run_ingestion
python -m src.loaders.load_exchange_rates
python -m src.loaders.load_world_bank
python -m src.loaders.load_bb_trade
```

### 6. Set up the frontend

```bash
cd frontend
npm install
```

### 7. Set up Airflow (optional, for scheduled orchestration)

```bash
cd airflow
docker compose up airflow-init
docker compose up -d
```
Visit `http://localhost:8080` (login: `airflow` / `airflow`).

### 8. Set up Kafka (optional, for live streaming)

```bash
cd kafka
docker compose up -d
docker exec kafka /opt/kafka/bin/kafka-topics.sh --create \
  --topic exchange_rates_stream \
  --bootstrap-server localhost:9092 \
  --partitions 1 --replication-factor 1
```

---

## Running the Platform (Day-to-Day)

Once everything is set up, here's the full startup sequence to bring the whole platform online. Each numbered step marked "own terminal" needs a dedicated terminal window that stays open.

### 1. Start Docker Desktop
Launch it and wait for "Engine running."

### 2. Confirm PostgreSQL is running
```bash
psql -U postgres -c "SELECT 1;"
```

### 3. Start Kafka
```bash
cd kafka
docker compose start
```

### 4. Start Airflow (optional)
```bash
cd airflow
docker compose start
```

### 5. Start the backend API — own terminal
```bash
source venv/Scripts/activate
uvicorn src.api.main:app --reload --port 8000
```
API docs: `http://localhost:8000/docs`

### 6. Start the Kafka producer — own terminal
```bash
source venv/Scripts/activate
python -m src.streaming.producer
```

### 7. Start the Kafka consumer — own terminal
```bash
source venv/Scripts/activate
python -m src.streaming.consumer
```

### 8. Start the frontend — own terminal
```bash
cd frontend
npm run dev
```
Dashboard: `http://localhost:5173`

### Shutting everything down

```bash
# Stop the 4 running processes with Ctrl+C in each terminal, then:
cd kafka && docker compose stop
cd ../airflow && docker compose stop
```

---

## API Reference

| Endpoint | Description |
|---|---|
| `GET /` | Health check |
| `GET /api/dashboard` | Combined snapshot of headline indicators |
| `GET /api/exchange-rates` | All exchange rates (filterable by `rate_type`) |
| `GET /api/exchange-rates/{code}` | History for one currency |
| `GET /api/inflation` | Annual inflation data |
| `GET /api/reserves` | Annual foreign reserves data |
| `GET /api/trade` | Fiscal-year trade data (exports/imports/balance) |
| `GET /api/remittance` | Annual remittance inflow data |
| `WS /ws/exchange-rates` | Live-updating exchange rate stream |

Full interactive documentation is auto-generated at `/docs` while the backend is running.

---

## Database Schema

Star schema with three dimension tables and five fact tables:

- **`dim_date`** — one row per calendar day (1971–2027), carrying both calendar-year and Bangladesh fiscal-year (July–June) fields
- **`dim_currency`** — 14 tracked currencies
- **`dim_source`** — the 3 data sources (API / World Bank / Bangladesh Bank)
- **`fact_exchange_rate`**, **`fact_inflation`**, **`fact_reserves`**, **`fact_trade`**, **`fact_remittance`**

Every fact table has a `UNIQUE` constraint and every loader uses `ON CONFLICT ... DO UPDATE`, making all loads idempotent — safe to re-run at any time without creating duplicates.

---

## Known Limitations / Future Improvements

- `fact_exchange_rate` currently accumulates one row per day per currency from the batch loader; a "latest snapshot only" query helper would simplify frontend consumption.
- Only 2 of Bangladesh Bank's ~46 historical data sheets are currently parsed (`Table IB` for trade, `TableXXII` referenced for exchange rates). The remaining sheets (interest rates, GDP detail, stock market data) are ingested as raw files but not yet loaded into the warehouse.
- No automated test suite yet.
- Not yet deployed — runs locally only. A natural next step would be frontend on Vercel, backend on a small VPS/EC2, and Postgres on a managed service (e.g. RDS).
- No CI/CD pipeline yet.

---

## Project Phases

This project was built in five phases, each with a written explanation of the concepts and decisions involved:

1. **Data Collection & Ingestion** — raw API and file fetching, retry logic, structured logging, date-partitioned storage
2. **Data Engineering Pipeline** — PostgreSQL star schema, fiscal-year modeling, cleaning messy real-world Excel data
3. **Orchestration & Streaming** — Airflow (Docker) for scheduled batch runs, Kafka (KRaft mode) for live streaming
4. **Backend API** — FastAPI REST endpoints and a live WebSocket feed
5. **Frontend Dashboard** — React + Recharts dashboard consuming the API and WebSocket

---

## License

Personal learning project. Data sourced from public APIs and Bangladesh Bank's Open Data Initiative.
