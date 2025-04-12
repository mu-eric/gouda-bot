import pytest
import os
import sys
import sqlite3
import logging

# Add project root to the Python path to allow importing 'database' and 'config'
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, PROJECT_ROOT)

import database
import config

# Helper Context Manager for Mocks
class MockConnectionContextManager:
    def __init__(self, mock_connection):
        self.mock_connection = mock_connection

    def __enter__(self):
        # Delegate to the mock's __enter__ and return the mock connection
        # IMPORTANT: The 'with' statement uses the return value of __enter__
        # So, __enter__ should return the object that has .cursor(), etc.
        # Let's return the underlying mock_connection itself from __enter__
        return self.mock_connection.__enter__()

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Delegate to the mock's __exit__
        return self.mock_connection.__exit__(exc_type, exc_val, exc_tb)

    def close(self):
        # Delegate to the mock's close method
        return self.mock_connection.close()

    def cursor(self):
        # Delegate to the mock's cursor method
        return self.mock_connection.cursor()

    def commit(self):
        # Delegate commit
        return self.mock_connection.commit()

    def rollback(self):
        # Delegate rollback
        return self.mock_connection.rollback()

# Fixture to set up an in-memory database for testing
@pytest.fixture
def test_db(monkeypatch):
    """Creates an in-memory SQLite database for testing and initializes schema."""
    # Use monkeypatch to temporarily change the DB_FILE in the config module
    # This ensures database functions operate on the in-memory DB
    monkeypatch.setattr(config, 'DB_FILE', ':memory:')

    # Create a single connection for the test
    conn = sqlite3.connect(':memory:')
    # Set row_factory for the connection so get_history returns dicts
    conn.row_factory = sqlite3.Row

    # Initialize the schema using this connection
    database.init_db(conn=conn)

    # Yield the connection to the test function
    yield conn

    # Teardown: Close the connection after the test is done
    conn.close()

def test_example(test_db):
    """An example test to ensure the fixture works."""
    # This test uses the 'test_db' fixture, which sets up the in-memory DB
    assert True # Replace with actual test logic

# --- TODO: Add tests for database functions below ---

# --- Tests for History Management ---

def test_save_and_get_history(test_db):
    """Test saving messages and retrieving history."""
    conv_id = "test_conv_1"
    user_name = "test_user"

    # Save some messages
    database.save_message(conv_id, "user", "Hello", username=user_name, conn=test_db)
    database.save_message(conv_id, "assistant", "Hi there!", conn=test_db)
    database.save_message(conv_id, "user", "How are you?", username=user_name, conn=test_db)

    # Retrieve history
    history = database.get_history(conv_id, limit=5, conn=test_db)

    assert len(history) == 3
    assert history[0]["role"] == "user"
    assert history[0]["content"] == "Hello"
    assert history[0]["username"] == user_name
    assert history[1]["role"] == "assistant"
    assert history[1]["content"] == "Hi there!"
    assert history[1]["username"] is None # Assistant messages shouldn't have username
    assert history[2]["role"] == "user"
    assert history[2]["content"] == "How are you?"

    # Test history limit
    limited_history = database.get_history(conv_id, limit=1, conn=test_db)
    assert len(limited_history) == 1
    assert limited_history[0]["content"] == "How are you?" # Should be the latest

def test_get_history_empty(test_db):
    """Test retrieving history for a non-existent conversation."""
    history = database.get_history("non_existent_conv", limit=5, conn=test_db)
    assert len(history) == 0

def test_clear_history(test_db):
    """Test clearing conversation history."""
    conv_id = "test_conv_clear"

    # Add messages
    database.save_message(conv_id, "user", "Message 1", conn=test_db)
    database.save_message(conv_id, "user", "Message 2", conn=test_db)
    history_before = database.get_history(conv_id, limit=5, conn=test_db)
    assert len(history_before) == 2

    # Clear history
    deleted_count = database.clear_conversation_history(conv_id, conn=test_db)
    assert deleted_count == 2

    # Verify history is empty
    history_after = database.get_history(conv_id, limit=5, conn=test_db)
    assert len(history_after) == 0

    # Verify clearing non-existent history
    deleted_count_non_existent = database.clear_conversation_history("non_existent_clear", conn=test_db)
    assert deleted_count_non_existent == 0

# --- Tests for Prompt Management ---

def test_set_and_get_channel_prompt(test_db):
    """Test setting and retrieving a channel-specific prompt."""
    conv_id = "prompt_conv_1"
    prompt_text = "You are a test bot."

    # Set prompt
    success = database.set_channel_prompt(conv_id, prompt_text, conn=test_db)
    assert success is True

    # Get prompt
    retrieved_prompt = database.get_channel_prompt(conv_id, conn=test_db)
    assert retrieved_prompt == prompt_text

def test_get_channel_prompt_not_set(test_db):
    """Test getting a prompt for a channel where none is set."""
    retrieved_prompt = database.get_channel_prompt("prompt_conv_not_set", conn=test_db)
    assert retrieved_prompt is None

def test_update_channel_prompt(test_db):
    """Test updating an existing channel prompt."""
    conv_id = "prompt_conv_update"
    initial_prompt = "Initial prompt."
    updated_prompt = "Updated prompt."

    # Set initial prompt
    database.set_channel_prompt(conv_id, initial_prompt, conn=test_db)
    assert database.get_channel_prompt(conv_id, conn=test_db) == initial_prompt

    # Update prompt
    success = database.set_channel_prompt(conv_id, updated_prompt, conn=test_db)
    assert success is True
    assert database.get_channel_prompt(conv_id, conn=test_db) == updated_prompt

def test_delete_channel_prompt(test_db):
    """Test deleting a channel prompt."""
    conv_id = "prompt_conv_delete"
    prompt_text = "To be deleted."

    # Set prompt
    database.set_channel_prompt(conv_id, prompt_text, conn=test_db)
    assert database.get_channel_prompt(conv_id, conn=test_db) == prompt_text

    # Delete prompt
    deleted = database.delete_channel_prompt(conv_id, conn=test_db)
    assert deleted is True

    # Verify prompt is gone
    assert database.get_channel_prompt(conv_id, conn=test_db) is None

def test_delete_channel_prompt_not_set(test_db):
    """Test deleting a prompt that was never set."""
    deleted = database.delete_channel_prompt("prompt_conv_delete_not_set", conn=test_db)
    assert deleted is False # Should indicate nothing was deleted

# --- Tests for Self-Managed Connections ---

def test_save_message_no_conn(tmp_path, monkeypatch):
    """Test save_message when it manages its own connection."""
    db_path = tmp_path / "test_save_no_conn.db"
    monkeypatch.setattr(config, 'DB_FILE', str(db_path))
    database.init_db() # Initialize the temporary file DB

    conv_id = "self_conn_save"
    database.save_message(conv_id, "user", "Testing self connect")

    # Verify by connecting manually or using get_history with self-connect
    history = database.get_history(conv_id, limit=1) # Let get_history connect itself
    assert len(history) == 1
    assert history[0]['content'] == "Testing self connect"

def test_get_history_no_conn(tmp_path, monkeypatch):
    """Test get_history when it manages its own connection."""
    db_path = tmp_path / "test_get_no_conn.db"
    monkeypatch.setattr(config, 'DB_FILE', str(db_path))
    database.init_db()

    conv_id = "self_conn_get"
    # Use self-connecting save
    database.save_message(conv_id, "user", "Msg 1")
    database.save_message(conv_id, "user", "Msg 2")

    history = database.get_history(conv_id, limit=2)
    assert len(history) == 2
    assert history[0]['content'] == "Msg 1"
    assert history[1]['content'] == "Msg 2"

def test_clear_history_no_conn(tmp_path, monkeypatch):
    """Test clear_conversation_history managing its own connection."""
    db_path = tmp_path / "test_clear_no_conn.db"
    monkeypatch.setattr(config, 'DB_FILE', str(db_path))
    database.init_db()
    conv_id = "self_conn_clear"
    database.save_message(conv_id, "user", "To clear")

    deleted_count = database.clear_conversation_history(conv_id)
    assert deleted_count == 1
    history = database.get_history(conv_id, limit=1)
    assert len(history) == 0

def test_set_prompt_no_conn(tmp_path, monkeypatch):
    """Test set_channel_prompt managing its own connection."""
    db_path = tmp_path / "test_set_prompt_no_conn.db"
    monkeypatch.setattr(config, 'DB_FILE', str(db_path))
    database.init_db()
    conv_id = "self_conn_set_prompt"
    prompt = "Self connect prompt"

    success = database.set_channel_prompt(conv_id, prompt)
    assert success is True
    retrieved = database.get_channel_prompt(conv_id)
    assert retrieved == prompt

def test_get_prompt_no_conn(tmp_path, monkeypatch):
    """Test get_channel_prompt managing its own connection."""
    db_path = tmp_path / "test_get_prompt_no_conn.db"
    monkeypatch.setattr(config, 'DB_FILE', str(db_path))
    database.init_db()
    conv_id = "self_conn_get_prompt"
    prompt = "Prompt to get"
    database.set_channel_prompt(conv_id, prompt) # Use self-connect set

    retrieved = database.get_channel_prompt(conv_id)
    assert retrieved == prompt
    assert database.get_channel_prompt("nonexistent") is None

def test_delete_prompt_no_conn(tmp_path, monkeypatch):
    """Test delete_channel_prompt managing its own connection."""
    db_path = tmp_path / "test_delete_prompt_no_conn.db"
    monkeypatch.setattr(config, 'DB_FILE', str(db_path))
    database.init_db()
    conv_id = "self_conn_delete_prompt"
    prompt = "Prompt to delete"
    database.set_channel_prompt(conv_id, prompt)

    deleted = database.delete_channel_prompt(conv_id)
    assert deleted is True
    assert database.get_channel_prompt(conv_id) is None
    deleted_again = database.delete_channel_prompt(conv_id)
    assert deleted_again is False

# --- Tests for Error Handling ---

# Note: We are primarily testing that the except block is hit and handled gracefully.
# The caplog fixture captures log output.

def test_save_message_error(mocker, caplog):
    """Test save_message error handling using a mock connection."""
    conv_id = "error_save"
    mock_conn = mocker.MagicMock()
    mock_cursor = mocker.MagicMock(spec=sqlite3.Cursor)
    mock_conn.__enter__.return_value = mock_conn
    mock_conn.__exit__ = mocker.Mock(return_value=None)
    mock_cursor.execute.side_effect = sqlite3.Error("Mock save error")
    mock_conn.cursor.return_value = mock_cursor

    database.save_message(conv_id, "user", "content", conn=mock_conn)

    mock_conn.__exit__.assert_called_once()
    assert "Error saving message to database: Mock save error" in caplog.text

def test_clear_history_error(mocker, caplog):
    """Test clear_history error handling using a mock connection."""
    conv_id = "error_clear"
    mock_conn = mocker.MagicMock()
    mock_cursor = mocker.MagicMock(spec=sqlite3.Cursor)
    mock_conn.__enter__.return_value = mock_conn
    mock_conn.__exit__ = mocker.Mock(return_value=None)
    mock_cursor.execute.side_effect = sqlite3.Error("Mock clear error")
    mock_conn.cursor.return_value = mock_cursor

    deleted_count = database.clear_conversation_history(conv_id, conn=mock_conn)

    mock_conn.__exit__.assert_called_once()
    assert deleted_count == 0 # Should return 0 on error
    assert "Error clearing history from database: Mock clear error" in caplog.text

def test_set_prompt_error(mocker, caplog):
    """Test set_channel_prompt error handling using a mock connection."""
    conv_id = "error_set_prompt"
    mock_conn = mocker.MagicMock()
    mock_cursor = mocker.MagicMock(spec=sqlite3.Cursor)
    mock_conn.__enter__.return_value = mock_conn
    mock_conn.__exit__ = mocker.Mock(return_value=None)
    mock_cursor.execute.side_effect = sqlite3.Error("Mock set prompt error")
    mock_conn.cursor.return_value = mock_cursor

    success = database.set_channel_prompt(conv_id, "prompt", conn=mock_conn)

    mock_conn.__exit__.assert_called_once()
    assert success is False # Should return False on error
    assert f"Error setting prompt for channel {conv_id}: Mock set prompt error" in caplog.text

def test_delete_prompt_error(mocker, caplog):
    """Test delete_channel_prompt error handling using a mock connection."""
    conv_id = "error_delete_prompt"
    mock_conn = mocker.MagicMock()
    mock_cursor = mocker.MagicMock(spec=sqlite3.Cursor)
    mock_conn.__enter__.return_value = mock_conn
    # mock_conn.__exit__ = mocker.Mock(return_value=None)
    mock_conn.__exit__ = mocker.Mock(return_value=None) # Ensure __exit__ doesn't suppress the error
    mock_cursor.execute.side_effect = sqlite3.Error("Mock delete prompt error")
    mock_conn.cursor.return_value = mock_cursor
    # Set rowcount just in case, although execute should raise before it's checked
    mock_cursor.rowcount = 0

    deleted = database.delete_channel_prompt(conv_id, conn=mock_conn)

    mock_conn.__exit__.assert_called_once() # Check __exit__ was called
    assert deleted is False # Should return False on error
    assert f"Error deleting prompt for channel {conv_id}: Mock delete prompt error" in caplog.text

if __name__ == "__main__":
    pytest.main([__file__])