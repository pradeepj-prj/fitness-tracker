def test_get_settings(client):
    response = client.get("/settings")
    assert response.status_code == 200
    data = response.json()
    assert data["daily_calorie_goal"] == 2000


def test_update_settings(client):
    response = client.put("/settings", json={"daily_calorie_goal": 1800})
    assert response.status_code == 200
    assert response.json()["daily_calorie_goal"] == 1800

    get_response = client.get("/settings")
    assert get_response.json()["daily_calorie_goal"] == 1800


def test_update_settings_validation(client):
    response = client.put("/settings", json={"daily_calorie_goal": -100})
    assert response.status_code == 422

    response = client.put("/settings", json={"daily_calorie_goal": 20000})
    assert response.status_code == 422
