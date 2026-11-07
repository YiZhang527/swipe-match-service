import pytest
from fastapi.testclient import TestClient
from moto import mock_aws

from app.init_tables import create_tables
from app.main import app


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "testing")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "testing")
    monkeypatch.setenv("AWS_SESSION_TOKEN", "testing")
    monkeypatch.setenv("AWS_REGION", "us-east-1")
    monkeypatch.setenv("AWS_DEFAULT_REGION", "us-east-1")
    monkeypatch.setenv("SWIPES_TABLE", "swipes")
    monkeypatch.setenv("MATCHES_TABLE", "matches")
    monkeypatch.delenv("DYNAMODB_ENDPOINT", raising=False)
    with mock_aws():
        create_tables()
        yield TestClient(app)
