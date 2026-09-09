import pytest

def pytest_configure(config):
    config.addinivalue_line(
        "markers",
        "slow: marks tests as slow (real Groq API calls). Run with: pytest -m slow"
    )
