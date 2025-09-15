import os
import sys
import pytest

# Ensure the app module is importable
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from api.index import app


@pytest.fixture()
def client():
    app.config.update({
        "TESTING": True,
    })
    with app.test_client() as client:
        yield client


