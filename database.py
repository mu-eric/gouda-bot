import sqlite3
import logging
import config # Import our config module

# --- Database Setup and Functions ---

def init_db():
    """Initializes the database and creates the messages table if it doesn't exist."""
    conn = sqlite3.connect(config.DB_FILE)
    cursor = conn.cursor()
    try:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id TEXT NOT NULL,
                role TEXT NOT NULL, -- 'user' or 'assistant'
                content TEXT NOT NULL,
                username TEXT, -- Store the display name for user messages
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        logging.info(f"Database '{config.DB_FILE}' initialized.")
    except sqlite3.Error as e:
        logging.error(f"Database initialization error: {e}")
    finally:
        conn.close()

def save_message(conversation_id: str, role: str, content: str, username: str = None):
    """Saves a message to the database, including username for user messages."""
    conn = sqlite3.connect(config.DB_FILE)
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO messages (conversation_id, role, content, username) VALUES (?, ?, ?, ?)",
            (conversation_id, role, content, username)
        )
        conn.commit()
    except sqlite3.Error as e:
        logging.error(f"Error saving message to database: {e}")
    finally:
        conn.close()

def get_history(conversation_id: str, limit: int = config.HISTORY_LIMIT) -> list[dict]:
    """Retrieves the last 'limit' messages for a conversation, including username."""
    history = []
    conn = sqlite3.connect(config.DB_FILE)
    conn.row_factory = sqlite3.Row # Return rows as dictionary-like objects
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT role, content, username FROM messages WHERE conversation_id = ? ORDER BY timestamp DESC LIMIT ?",
            (conversation_id, limit)
        )
        # Fetch rows and convert them to simple dicts, reversing order to be chronological
        rows = cursor.fetchall()
        history = [dict(row) for row in reversed(rows)]
    except sqlite3.Error as e:
        logging.error(f"Error retrieving history from database: {e}")
    finally:
        conn.close()
    return history

def clear_conversation_history(conversation_id: str):
    """Deletes all messages for a given conversation ID from the database."""
    conn = sqlite3.connect(config.DB_FILE)
    cursor = conn.cursor()
    deleted_count = 0
    try:
        cursor.execute("DELETE FROM messages WHERE conversation_id = ?", (conversation_id,))
        deleted_count = cursor.rowcount # Get the number of rows deleted
        conn.commit()
        logging.info(f"Cleared {deleted_count} messages for conversation {conversation_id}.")
    except sqlite3.Error as e:
        logging.error(f"Error clearing history for conversation {conversation_id}: {e}")
    finally:
        conn.close()
    return deleted_count
