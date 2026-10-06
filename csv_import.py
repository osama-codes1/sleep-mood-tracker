"""Data pipeline: load sleep/mood records from a CSV file into PostgreSQL.

Pipeline steps:
    1. Extract   - read the CSV file
    2. Transform - validate and clean every row
    3. Load      - insert new rows, skipping dates that already exist

Usage:
    python csv_import.py sample_data.csv
"""

import csv
import datetime
import sys

from sqlalchemy.orm import Session

import models
from database import Base, SessionLocal, engine

REQUIRED_COLUMNS = {"date", "sleep_hours", "mood"}


def parse_rows(rows) -> list[dict]:
    """Validate raw CSV rows and convert them to clean Python values.

    Raises ValueError with the line number if any row is invalid.
    """
    cleaned = []

    for line_number, row in enumerate(rows, start=2):
        try:
            date = datetime.date.fromisoformat(row["date"].strip())
            sleep_hours = float(row["sleep_hours"])
            mood = int(row["mood"])
        except (ValueError, KeyError, AttributeError, TypeError) as error:
            raise ValueError(f"Line {line_number}: invalid row ({error})") from error

        if not 0 <= sleep_hours <= 24:
            raise ValueError(f"Line {line_number}: sleep_hours must be between 0 and 24")
        if not 1 <= mood <= 10:
            raise ValueError(f"Line {line_number}: mood must be between 1 and 10")

        cleaned.append({"date": date, "sleep_hours": sleep_hours, "mood": mood})

    return cleaned


def read_csv(path: str) -> list[dict]:
    """Read a CSV file and return validated rows."""
    with open(path, newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)
        missing = REQUIRED_COLUMNS - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"Missing required columns: {', '.join(sorted(missing))}")
        return parse_rows(reader)


def load_entries(db: Session, entries: list[dict]) -> tuple[int, int]:
    """Insert entries into the database. Returns (inserted, skipped)."""
    existing_dates = {row.date for row in db.query(models.Entry.date).all()}
    inserted = 0
    skipped = 0

    for entry in entries:
        if entry["date"] in existing_dates:
            skipped += 1
            continue
        db.add(models.Entry(**entry))
        existing_dates.add(entry["date"])
        inserted += 1

    db.commit()
    return inserted, skipped


def main():
    if len(sys.argv) != 2:
        print("Usage: python csv_import.py <file.csv>")
        sys.exit(1)

    Base.metadata.create_all(bind=engine)

    try:
        entries = read_csv(sys.argv[1])
    except (ValueError, FileNotFoundError) as error:
        print(f"Import failed: {error}")
        sys.exit(1)

    with SessionLocal() as db:
        inserted, skipped = load_entries(db, entries)

    print(f"Done. Inserted {inserted} rows, skipped {skipped} duplicates.")


if __name__ == "__main__":
    main()
