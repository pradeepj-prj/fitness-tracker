from app.config import settings


def test_auth_gate_redirects_html_and_blocks_api(client, monkeypatch):
    monkeypatch.setattr(settings, "AUTH_USERNAME", "tracker")
    monkeypatch.setattr(settings, "AUTH_PASSWORD", "secret")
    monkeypatch.setattr(settings, "SESSION_SECRET", "test-secret")
    monkeypatch.setattr(settings, "SESSION_COOKIE_SECURE", False)

    html_response = client.get("/chat/", follow_redirects=False)
    assert html_response.status_code == 303
    assert html_response.headers["location"] == "/login"

    api_response = client.get("/entries")
    assert api_response.status_code == 401
    assert api_response.json()["detail"] == "Authentication required"


def test_login_sets_session_cookie(client, monkeypatch):
    monkeypatch.setattr(settings, "AUTH_USERNAME", "tracker")
    monkeypatch.setattr(settings, "AUTH_PASSWORD", "secret")
    monkeypatch.setattr(settings, "SESSION_SECRET", "test-secret")
    monkeypatch.setattr(settings, "SESSION_COOKIE_SECURE", False)

    bad_response = client.post(
        "/auth/login",
        data={"username": "tracker", "password": "wrong"},
    )
    assert bad_response.status_code == 401

    login_response = client.post(
        "/auth/login",
        data={"username": "tracker", "password": "secret"},
        follow_redirects=False,
    )
    assert login_response.status_code == 303

    chat_response = client.get("/chat/")
    assert chat_response.status_code == 200
    assert "Calorie Tracker" in chat_response.text
