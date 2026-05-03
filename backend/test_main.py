import pytest
from fastapi.testclient import TestClient
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from main import app

client = TestClient(app)

def test_root_endpoint():
    """Verify the API root is healthy and serving properly."""
    response = client.get("/")
    assert response.status_code == 200
    # Check if we get JSON back (when static files are missing) or a file
    assert "status" in response.json() or response.headers["content-type"] == "text/html"

def test_generate_validation():
    """Verify that the API enforces validation rules on the input."""
    # Test missing payload
    response = client.post("/generate", json={})
    assert response.status_code == 422 # Unprocessable Entity

    # Test invalid type
    response = client.post("/generate", json={"prompt": "test topic", "type": "invalid"})
    assert response.status_code == 422

    # Test empty prompt
    response = client.post("/generate", json={"prompt": "   ", "type": "10mark"})
    assert response.status_code == 422

def test_generate_length_limits():
    """Verify that the API enforces length limits on the prompt."""
    long_prompt = "A" * 5001
    response = client.post("/generate", json={"prompt": long_prompt, "type": "10mark"})
    assert response.status_code == 422

def test_health_check():
    """Simple check for API availability."""
    response = client.get("/")
    assert response.status_code == 200
