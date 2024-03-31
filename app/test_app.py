from fastapi.testclient import TestClient
from app import app  # Adjust the import path according to your project structure

client = TestClient(app)

def test_classify_waybill():
    response = client.post("/waybills/classify", json={"content": "Your waybill content here", "category": "Your category here"})
    assert response.status_code == 200
    data = response.json()
    assert data['content'] == "Your waybill content here"
    assert data['category'] == "Your category here"

def test_analyze_event():
    response = client.post("/events/analyze", json={"event_type": "Your event type here", "details": {"key": "value"}})
    assert response.status_code == 200
    data = response.json()
    assert data['event_type'] == "Your event type here"
    assert data['details'] == {"key": "value"}

def test_generate_market_report():
    response = client.post("/market-reports/generate", json={"industry": "Your industry here", "keywords": ["keyword1", "keyword2"]})
    assert response.status_code == 200
    data = response.json()
    assert data['industry'] == "Your industry here"
    assert data['keywords'] == ["keyword1", "keyword2"]

# def test_interact_with_chatbot():
#     response = client.post("/chatbot/interact", json={"message": "Name the planets in the solar system?", "context": {"key": "value"}})
#     assert response.status_code == 200