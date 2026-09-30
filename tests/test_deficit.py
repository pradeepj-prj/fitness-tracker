def test_get_deficit_today_no_entries(client):
    response = client.get("/deficit/today")
    assert response.status_code == 200
    data = response.json()
    assert data["daily_goal"] == 2000
    assert data["total_consumed"] == 0
    assert data["remaining"] == 2000
    assert data["entries_count"] == 0


def test_get_deficit_today_with_entries(client):
    client.post("/entries", json={"food_name": "Breakfast", "calories": 500})
    client.post("/entries", json={"food_name": "Lunch", "calories": 700})

    response = client.get("/deficit/today")
    assert response.status_code == 200
    data = response.json()
    assert data["total_consumed"] == 1200
    assert data["remaining"] == 800
    assert data["entries_count"] == 2


def test_get_deficit_with_custom_goal(client):
    client.put("/settings", json={"daily_calorie_goal": 1500})
    client.post("/entries", json={"food_name": "Meal", "calories": 600})

    response = client.get("/deficit/today")
    data = response.json()
    assert data["daily_goal"] == 1500
    assert data["remaining"] == 900


def test_get_deficit_over_goal(client):
    client.put("/settings", json={"daily_calorie_goal": 1000})
    client.post("/entries", json={"food_name": "Big Meal", "calories": 1500})

    response = client.get("/deficit/today")
    data = response.json()
    assert data["remaining"] == -500
