def test_create_entry(client):
    response = client.post("/entries", json={
        "food_name": "Apple",
        "calories": 95,
        "protein_g": 0.5,
        "carbs_g": 25,
        "fat_g": 0.3,
    })
    assert response.status_code == 201
    data = response.json()
    assert data["food_name"] == "Apple"
    assert data["calories"] == 95
    assert data["source"] == "manual"
    assert "id" in data


def test_create_entry_minimal(client):
    response = client.post("/entries", json={
        "food_name": "Banana",
        "calories": 105,
    })
    assert response.status_code == 201
    assert response.json()["food_name"] == "Banana"


def test_create_entry_validation_error(client):
    response = client.post("/entries", json={"food_name": "", "calories": 100})
    assert response.status_code == 422


def test_get_entry(client):
    create_response = client.post("/entries", json={"food_name": "Apple", "calories": 95})
    entry_id = create_response.json()["id"]

    response = client.get(f"/entries/{entry_id}")
    assert response.status_code == 200
    assert response.json()["id"] == entry_id


def test_get_entry_not_found(client):
    response = client.get("/entries/9999")
    assert response.status_code == 404


def test_list_entries(client):
    client.post("/entries", json={"food_name": "Apple", "calories": 95})
    client.post("/entries", json={"food_name": "Banana", "calories": 105})

    response = client.get("/entries")
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_update_entry(client):
    create_response = client.post("/entries", json={"food_name": "Apple", "calories": 95})
    entry_id = create_response.json()["id"]

    response = client.put(f"/entries/{entry_id}", json={"calories": 100})
    assert response.status_code == 200
    assert response.json()["calories"] == 100
    assert response.json()["food_name"] == "Apple"


def test_delete_entry(client):
    create_response = client.post("/entries", json={"food_name": "Apple", "calories": 95})
    entry_id = create_response.json()["id"]

    response = client.delete(f"/entries/{entry_id}")
    assert response.status_code == 204

    get_response = client.get(f"/entries/{entry_id}")
    assert get_response.status_code == 404
