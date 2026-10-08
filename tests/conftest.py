import os

os.environ["LLM_PROVIDER"] = "mock"

import pytest
from fastapi.testclient import TestClient

from sentinelia.config import get_settings
from sentinelia.main import app


@pytest.fixture
def client():
    get_settings.cache_clear()
    with TestClient(app) as test_client:
        yield test_client

