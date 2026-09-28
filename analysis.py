"""Pure analysis functions (no database, no web framework).

Keeping the logic here makes it easy to unit test in isolation.
"""

from statistics import mean, correlation, StatisticsError


def group_mood_by_sleep(entries: list[dict]) -> dict:
    """Return the average mood for each sleep-duration bucket.

    Buckets: under 6 hours, 6 to 8 hours (inclusive), over 8 hours.
    A bucket with no entries returns None instead of raising an error.
    """
    buckets = {"under_6h": [], "6_to_8h": [], "over_8h": []}

    for entry in entries:
        hours = entry["sleep_hours"]
        if hours < 6:
            key = "under_6h"
        elif hours <= 8:
            key = "6_to_8h"
        else:
            key = "over_8h"
        buckets[key].append(entry["mood"])

    return {key: (mean(moods) if moods else None) for key, moods in buckets.items()}


def calculate_correlation(entries: list[dict]) -> float | None:
    """Return the correlation between sleep hours and mood (-1 to 1).

    Returns None when there is not enough data, or when one of the two
    series has no variation (for example, every night has exactly 8 hours).
    """
    if len(entries) < 2:
        return None

    sleep = [e["sleep_hours"] for e in entries]
    mood = [e["mood"] for e in entries]

    try:
        return correlation(sleep, mood)
    except StatisticsError:
        return None


def describe_correlation(value: float | None) -> str:
    """Turn a correlation number into a short human-readable label."""
    if value is None:
        return "not enough data"

    strength = abs(value)
    if strength >= 0.7:
        label = "strong"
    elif strength >= 0.4:
        label = "moderate"
    elif strength >= 0.2:
        label = "weak"
    else:
        return "no clear relationship"

    direction = "positive" if value > 0 else "negative"
    return f"{label} {direction}"
