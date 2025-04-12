import pytest
import os
import importlib
import logging
from unittest.mock import patch

# Import the module we want to test
import config # Import once initially

# Store original values to restore later if needed (pytest fixtures handle this better generally)
ORIGINAL_DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
ORIGINAL_MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")

def test_missing_discord_token_exits(monkeypatch, caplog):
    """Test that the application exits if DISCORD_TOKEN is missing."""
    # Temporarily remove the token from the environment
    monkeypatch.delenv("DISCORD_TOKEN", raising=False)

    # Mock exit to prevent test runner from stopping
    # Also patch load_dotenv to prevent it reloading the token during module reload
    with patch('dotenv.load_dotenv'), \
         patch('builtins.exit') as mock_exit:
        with caplog.at_level(logging.ERROR):
            # Reload the config module to trigger the check
            # Need to use importlib.reload because the check happens at import time
            importlib.reload(config)

    # Assertions
    mock_exit.assert_called_once()
    assert "DISCORD_TOKEN not found in .env file." in caplog.text
    # Ensure the variable is still None in the reloaded module
    assert config.DISCORD_TOKEN is None

    # Restore the token (monkeypatch handles cleanup, but explicit reload ensures module state)
    if ORIGINAL_DISCORD_TOKEN:
        monkeypatch.setenv("DISCORD_TOKEN", ORIGINAL_DISCORD_TOKEN)
        importlib.reload(config)

def test_missing_mistral_api_key_warns(monkeypatch, caplog):
    """Test that a warning is logged if MISTRAL_API_KEY is missing."""
    # Ensure DISCORD_TOKEN is present, otherwise the exit() check stops the test
    if not config.DISCORD_TOKEN: # Check the current value in the module
        if not ORIGINAL_DISCORD_TOKEN:
            pytest.skip("Cannot run test because original DISCORD_TOKEN is also missing")
        monkeypatch.setenv("DISCORD_TOKEN", ORIGINAL_DISCORD_TOKEN)
        importlib.reload(config) # Ensure DISCORD_TOKEN is set before removing MISTRAL_API_KEY

    # Remove MISTRAL_API_KEY
    monkeypatch.delenv("MISTRAL_API_KEY", raising=False)

    # Patch load_dotenv and exit (exit should not be called)
    with patch('dotenv.load_dotenv'), \
         patch('builtins.exit') as mock_exit:
        with caplog.at_level(logging.WARNING):
            importlib.reload(config)

    # Assertions
    mock_exit.assert_not_called()
    assert "MISTRAL_API_KEY not found in .env file." in caplog.text
    assert config.MISTRAL_API_KEY is None

    # Restore MISTRAL_API_KEY
    if ORIGINAL_MISTRAL_API_KEY:
        monkeypatch.setenv("MISTRAL_API_KEY", ORIGINAL_MISTRAL_API_KEY)
        importlib.reload(config)

# Ensure config module is in a known state after tests
# This might be better handled with pytest fixtures/setup/teardown if tests grow
@pytest.fixture(autouse=True, scope='module')
def restore_config_state():
    yield
    # Code here runs after all tests in the module
    if ORIGINAL_DISCORD_TOKEN:
        os.environ["DISCORD_TOKEN"] = ORIGINAL_DISCORD_TOKEN
    else:
        if "DISCORD_TOKEN" in os.environ:
            del os.environ["DISCORD_TOKEN"]

    if ORIGINAL_MISTRAL_API_KEY:
        os.environ["MISTRAL_API_KEY"] = ORIGINAL_MISTRAL_API_KEY
    else:
        if "MISTRAL_API_KEY" in os.environ:
            del os.environ["MISTRAL_API_KEY"]
    # Reload config one last time to reflect original state
    importlib.reload(config)
