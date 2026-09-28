# Sleep & Mood Tracker

A REST API that records how many hours you sleep and how you feel each day
(mood from 1 to 10), then analyses whether more sleep actually means a better mood.

Built with **Python, FastAPI, SQLAlchemy and PostgreSQL**, developed test-first (TDD)
and packaged with Docker.

## Features

- Record daily sleep hours and mood, with input validation
- One entry per date (duplicates are rejected)
- Statistics: average mood per sleep bucket (under 6h / 6-8h / over 8h)
- Correlation between sleep and mood, with a readable interpretation
- Data pipeline: bulk-import history from a CSV file (validate, clean, load)
- Automated tests that run on an in-memory database and never touch real data

## Tech stack

| Area | Tool |
|---|---|
| Language | Python 3 |
| API | FastAPI |
| Database | PostgreSQL + SQLAlchemy |
| Testing | pytest (TDD) |
| Packaging | Docker, Docker Compose |

## Project structure

```
analysis.py      Pure functions: bucket averages, correlation (no DB, easy to test)
database.py      Database connection and session setup
models.py        SQLAlchemy table definition
main.py          FastAPI application and endpoints
csv_import.py    CSV data pipeline (extract, transform, load)
tests/           pytest test suite
sample_data.csv  30 days of example data
```

## Run locally

1. Create a PostgreSQL database:
   ```sql
   CREATE DATABASE sleep_mood_db;
   ```
2. Copy `.env.example` to `.env` and set your password.
3. Install dependencies and start the server:
   ```bash
   pip install -r requirements.txt
   uvicorn main:app --reload
   ```
4. Open http://127.0.0.1:8000/docs for the interactive API documentation.

## Run with Docker

```bash
docker compose up --build
```

The API is available at http://localhost:8000/docs.

## Import data from CSV

The CSV needs the columns `date,sleep_hours,mood`:

```bash
python csv_import.py sample_data.csv
```

Invalid rows stop the import with a clear message (for example `Line 3: mood must be
between 1 and 10`). Dates that already exist are skipped, so the import is safe to
run more than once.

## API endpoints

| Method | Path | Description |
|---|---|---|
| POST | `/entries` | Add a day (`date`, `sleep_hours` 0-24, `mood` 1-10) |
| GET | `/entries` | List all entries, ordered by date |
| DELETE | `/entries/{id}` | Delete an entry |
| GET | `/stats` | Averages per sleep bucket, correlation and interpretation |

Example response from `/stats`:

```json
{
  "total_entries": 30,
  "average_mood_by_sleep": {"under_6h": 5.67, "6_to_8h": 7.0, "over_8h": 8.13},
  "correlation": 0.80,
  "interpretation": "strong positive"
}
```

## Run the tests

```bash
python -m pytest
```

The tests use a temporary in-memory database, so they are fast and never modify
your real data.

## Notes

The sample data in `sample_data.csv` is generated for demonstration, not real
measurements.
