def add_entry(client, date, sleep_hours, mood):
    return client.post(
        "/entries",
        json={"date": date, "sleep_hours": sleep_hours, "mood": mood},
    )


def test_create_entry(client):
    response = add_entry(client, "2026-09-01", 7.5, 8)
    assert response.status_code == 201
    data = response.json()
    assert data["id"] == 1
    assert data["sleep_hours"] == 7.5
    assert data["mood"] == 8


def test_reject_mood_above_10(client):
    assert add_entry(client, "2026-09-01", 7, 11).status_code == 422


def test_reject_mood_below_1(client):
    assert add_entry(client, "2026-09-01", 7, 0).status_code == 422


def test_reject_sleep_hours_above_24(client):
    assert add_entry(client, "2026-09-01", 30, 5).status_code == 422


def test_reject_duplicate_date(client):
    add_entry(client, "2026-09-01", 7, 8)
    response = add_entry(client, "2026-09-01", 6, 5)
    assert response.status_code == 409


def test_list_entries_sorted_by_date(client):
    add_entry(client, "2026-09-02", 6, 6)
    add_entry(client, "2026-09-01", 7, 8)
    response = client.get("/entries")
    assert response.status_code == 200
    dates = [e["date"] for e in response.json()]
    assert dates == ["2026-09-01", "2026-09-02"]


def test_delete_entry(client):
    entry_id = add_entry(client, "2026-09-01", 7, 8).json()["id"]
    assert client.delete(f"/entries/{entry_id}").status_code == 204
    assert client.get("/entries").json() == []


def test_delete_missing_entry_returns_404(client):
    assert client.delete("/entries/999").status_code == 404


def test_stats(client):
    add_entry(client, "2026-09-01", 5, 4)
    add_entry(client, "2026-09-02", 7, 8)
    add_entry(client, "2026-09-03", 9, 9)
    data = client.get("/stats").json()
    assert data["total_entries"] == 3
    assert data["average_mood_by_sleep"]["under_6h"] == 4
    assert data["correlation"] > 0.9
    assert data["interpretation"] == "strong positive"


def test_stats_with_no_entries(client):
    data = client.get("/stats").json()
    assert data["total_entries"] == 0
    assert data["correlation"] is None
    assert data["interpretation"] == "not enough data"
