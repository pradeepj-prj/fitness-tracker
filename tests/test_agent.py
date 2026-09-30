from app.agent import tools
from app.agent.service import _message_content_for_model, _system_prompt
from app.config import settings
from app.models import AgentConversation, AgentMessage


def test_agent_food_tool_writes_and_reads(db_session):
    created = tools.create_food_entry(
        db_session,
        profile="vidhi",
        food_name="tea",
        calories=90,
        logged_at="2026-09-30T02:00:00",
    )

    assert created["id"]
    assert created["source"] == "manual"

    entries = tools.list_entries(db_session, profile="vidhi", date="2026-09-30")
    assert len(entries) == 1
    assert entries[0]["food_name"] == "tea"

    deficit = tools.get_deficit(db_session, profile="vidhi", date="2026-09-30")
    assert deficit["total_consumed"] == 90


def test_agent_chat_requires_openai_key(client, monkeypatch):
    monkeypatch.setattr(settings, "OPENAI_API_KEY", None)

    response = client.post(
        "/agent/chat",
        data={"profile": "vidhi", "message": "I had tea"},
    )

    assert response.status_code == 503
    assert response.json()["detail"] == "OPENAI_API_KEY is not configured"


def test_get_conversation_returns_recent_messages(client, db_session):
    db_session.add(AgentConversation(id="conv1", profile="vidhi"))
    db_session.add(AgentMessage(conversation_id="conv1", profile="vidhi", role="user", content="hello"))
    db_session.add(AgentMessage(conversation_id="conv1", profile="vidhi", role="assistant", content="hi"))
    db_session.commit()

    response = client.get("/agent/conversations/conv1?profile=vidhi")

    assert response.status_code == 200
    assert [message["content"] for message in response.json()["messages"]] == ["hello", "hi"]


def test_get_conversation_not_found(client):
    response = client.get("/agent/conversations/missing?profile=vidhi")

    assert response.status_code == 404


def test_model_context_includes_assistant_tool_summary():
    row = AgentMessage(
        conversation_id="conv1",
        profile="vidhi",
        role="assistant",
        content="Logged Coke Zero — 0 cal.",
        tool_summary='{"tool":"create_food_entry","result":{"id":604,"food_name":"Coke Zero"}}',
    )

    content = _message_content_for_model(row)

    assert "Logged Coke Zero" in content
    assert "Internal tracker tool results" in content
    assert "create_food_entry" in content
    assert "604" in content


def test_system_prompt_requires_db_check_before_unsaved_claims():
    prompt = _system_prompt("vidhi", None)

    assert "Never say a saved entry was not saved unless a read tool confirms that" in prompt
    assert "Zero-calorie drinks such as Coke Zero can be logged as 0 calories" in prompt
