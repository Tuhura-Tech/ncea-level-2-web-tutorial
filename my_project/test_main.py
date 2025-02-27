from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from main import app, engine, SQLModel
import pytest
from playwright.sync_api import Page, expect


@pytest.fixture()
def test_db():
    SQLModel.metadata.create_all(engine)
    yield
    SQLModel.metadata.drop_all(engine)
    

def test_create_post(test_db):
    client = TestClient(app)

    response = client.post(
        "/posts/", params = {"post_title": "test", "post_content": "test", "post_date": "test"}
    )
    
    data = response.json()
    assert data["title"] == "test"
    assert data["id"] is not None

def test_read_posts(test_db):
    client = TestClient(app)

    client.post(
        "/posts/", params = {"post_title": "test", "post_content": "test", "post_date": "test"}
    )

    client.post(
        "/posts/", params = {"post_title": "test2", "post_content": "test2", "post_date": "test2"}
    )

    response = client.get(
        "/posts/"
    )

    data = response.json()
    assert len(data) == 2


