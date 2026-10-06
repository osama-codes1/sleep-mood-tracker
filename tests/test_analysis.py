from analysis import group_mood_by_sleep, calculate_correlation, describe_correlation


def test_group_mood_by_sleep_averages_each_bucket():
    entries = [
        {"sleep_hours": 5, "mood": 4},
        {"sleep_hours": 5.5, "mood": 6},
        {"sleep_hours": 7, "mood": 8},
        {"sleep_hours": 9, "mood": 9},
    ]
    result = group_mood_by_sleep(entries)
    assert result["under_6h"] == 5
    assert result["6_to_8h"] == 8
    assert result["over_8h"] == 9


def test_bucket_boundaries():
    entries = [
        {"sleep_hours": 6, "mood": 5},  
        {"sleep_hours": 8, "mood": 7},  
    ]
    result = group_mood_by_sleep(entries)
    assert result["6_to_8h"] == 6
    assert result["under_6h"] is None
    assert result["over_8h"] is None


def test_empty_bucket_returns_none():
    entries = [{"sleep_hours": 7, "mood": 8}]
    result = group_mood_by_sleep(entries)
    assert result["under_6h"] is None


def test_correlation_is_positive_when_more_sleep_means_better_mood():
    entries = [
        {"sleep_hours": 4, "mood": 3},
        {"sleep_hours": 6, "mood": 5},
        {"sleep_hours": 8, "mood": 8},
    ]
    assert calculate_correlation(entries) > 0.9


def test_correlation_is_negative_when_relationship_is_reversed():
    entries = [
        {"sleep_hours": 4, "mood": 9},
        {"sleep_hours": 6, "mood": 6},
        {"sleep_hours": 8, "mood": 3},
    ]
    assert calculate_correlation(entries) < -0.9


def test_correlation_returns_none_with_fewer_than_two_entries():
    assert calculate_correlation([{"sleep_hours": 7, "mood": 7}]) is None


def test_correlation_returns_none_when_sleep_never_changes():
    entries = [
        {"sleep_hours": 8, "mood": 3},
        {"sleep_hours": 8, "mood": 9},
    ]
    assert calculate_correlation(entries) is None


def test_describe_correlation_labels():
    assert describe_correlation(0.85) == "strong positive"
    assert describe_correlation(-0.5) == "moderate negative"
    assert describe_correlation(0.25) == "weak positive"
    assert describe_correlation(0.05) == "no clear relationship"
    assert describe_correlation(None) == "not enough data"
