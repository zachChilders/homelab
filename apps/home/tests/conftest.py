import pytest
from src.main import app

@pytest.fixture
def test_app():
    return app 