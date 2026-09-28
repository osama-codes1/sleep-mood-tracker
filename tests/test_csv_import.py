import datetime

import pytest

import models
from csv_import import parse_rows, load_entries


def test_parse_rows_converts_types():
    rows = [{"date": "2026-09-01", "sleep_hours": "7.5", "mood": "8"}]
    assert parse_rows(rows) == [
        {"date": datetime.date(2026, 9, 1), "sleep_hours": 7.5, "mood": 8}
    ]


def test_parse_rows_rejects_bad_date_with_line_number():
    rows = [
        {"date": "2026-09-01", "sleep_hours": "7", "mood": "8"},
        {"date": "not-a-date", "sleep_hours": "7", "mood": "8"},
    ]
    with pytest.raises(ValueError, match="Line 3"):
        parse_rows(rows)


def test_parse_rows_rejects_out_of_range_mood():
    rows = [{"date": "2026-09-01", "sleep_hours": "7", "mood": "15"}]
    with pytest.raises(ValueError, match="mood"):
        parse_rows(rows)


def test_parse_rows_rejects_out_of_range_sleep():
    rows = [{"date": "2026-09-01", "sleep_hours": "40", "mood": "5"}]
    with pytest.raises(ValueError, match="sleep_hours"):
        parse_rows(rows)


def test_load_entries_skips_existing_dates(db_session):
    entries = [
        {"date": datetime.date(2026, 9, 1), "sleep_hours": 7.0, "mood": 8},
        {"date": datetime.date(2026, 9, 2), "sleep_hours": 6.0, "mood": 6},
    ]
    assert load_entries(db_session, entries) == (2, 0)
    # Loading the same data again inserts nothing
    assert load_entries(db_session, entries) == (0, 2)
    assert db_session.query(models.Entry).count() == 2
