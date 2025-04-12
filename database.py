import sqlite3
import logging
import config # Import our config module

# --- Database Setup and Functions ---

def init_db(conn=None):
    """Initializes the database and creates tables if they don't exist. Uses provided connection or creates new."""
    # Use the provided connection or create a new one
    db_conn = conn or sqlite3.connect(config.DB_FILE)
    try:
        # No need for context manager if we handle closing explicitly for created connections
        cursor = db_conn.cursor()

        # Create messages table
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

        # Create channel_prompts table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS channel_prompts (
            conversation_id TEXT PRIMARY KEY,
            system_prompt TEXT NOT NULL
        )
        ''')

        # Commit changes if we created the connection
        # If conn was passed, the caller is responsible for commits/closing
        if not conn:
            db_conn.commit()
        logging.info(f"Database '{config.DB_FILE}' initialized.")

    except sqlite3.Error as e:
        logging.error(f"Database initialization error: {e}")
    finally:
        # Close the connection only if it was created within this function
        if not conn and db_conn:
            db_conn.close()

def save_message(conversation_id, role, content, username=None, conn=None):
    """Saves a message to the database. Uses provided connection or creates new."""
    db_conn = conn or sqlite3.connect(config.DB_FILE)
    try:
        with db_conn as current_conn:
            cursor = current_conn.cursor()
            cursor.execute('''
                INSERT INTO messages (conversation_id, role, content, username)
                VALUES (?, ?, ?, ?)
            ''', (conversation_id, role, content, username))
            current_conn.commit()
    except sqlite3.Error as e:
        logging.error(f"Error saving message to database: {e}")
    finally:
        if not conn and db_conn: # Only close if connection was created here
            db_conn.close()

def get_history(conversation_id, limit=config.HISTORY_LIMIT, conn=None):
    """Retrieves the last 'limit' messages for a conversation. Uses provided connection or creates new."""
    messages = []
    db_conn = conn or sqlite3.connect(config.DB_FILE)
    connection_created = False # Flag to track if we need to close connection
    try:
        # Ensure connection is treated as context manager if created here
        if not conn:
            db_conn.row_factory = sqlite3.Row # Get dict-like rows
            connection_created = True

        cursor = db_conn.cursor()

        cursor.execute('''
            SELECT role, content, username FROM messages
            WHERE conversation_id = ?
            ORDER BY timestamp ASC
        ''', (conversation_id,))
        rows = cursor.fetchall()
        # Slice the last 'limit' rows from the results ordered chronologically
        messages = [dict(row) for row in rows[-limit:]]

    except sqlite3.Error as e:
        logging.error(f"Error retrieving history from database: {e}")
    finally:
        if connection_created and db_conn:
            db_conn.close()
    return messages

def clear_conversation_history(conversation_id, conn=None):
    """Clears all messages for a specific conversation. Returns number of deleted rows. Uses provided connection or creates new."""
    deleted_count = 0
    db_conn = conn or sqlite3.connect(config.DB_FILE)
    try:
        with db_conn as current_conn:
            cursor = current_conn.cursor()
            cursor.execute("DELETE FROM messages WHERE conversation_id = ?", (conversation_id,))
            deleted_count = cursor.rowcount
            current_conn.commit()
    except sqlite3.Error as e:
        logging.error(f"Error clearing history from database: {e}")
    finally:
        if not conn and db_conn: # Only close if connection was created here
            db_conn.close()
    return deleted_count

# --- Prompt Management ---

def set_channel_prompt(conversation_id, prompt, conn=None):
    """Sets or updates the system prompt for a specific channel. Uses provided connection or creates new."""
    success = False
    db_conn = conn or sqlite3.connect(config.DB_FILE)
    try:
        with db_conn as current_conn:
            cursor = current_conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO channel_prompts (conversation_id, system_prompt)
                VALUES (?, ?)
            ''', (conversation_id, prompt))
            current_conn.commit()
            success = True
    except sqlite3.Error as e:
        logging.error(f"Error setting prompt for channel {conversation_id}: {e}")
    finally:
        if not conn and db_conn: # Only close if connection was created here
            db_conn.close()
    return success

def get_channel_prompt(conversation_id, conn=None):
    """Gets the system prompt for a specific channel. Returns None if not set. Uses provided connection or creates new."""
    prompt = None
    db_conn = conn or sqlite3.connect(config.DB_FILE)
    try:
        # No need for context manager if using existing conn directly
        cursor = db_conn.cursor()
        cursor.execute("SELECT system_prompt FROM channel_prompts WHERE conversation_id = ?", (conversation_id,))
        result = cursor.fetchone()
        if result:
            prompt = result[0]
    except sqlite3.Error as e:
        logging.error(f"Error getting prompt for channel {conversation_id}: {e}")
    finally:
        if not conn and db_conn: # Only close if connection was created here
            db_conn.close()
    return prompt

def delete_channel_prompt(conversation_id, conn=None):
    """Deletes the system prompt for a specific channel. Returns True if deleted, False otherwise. Uses provided connection or creates new."""
    deleted = False
    db_conn = conn or sqlite3.connect(config.DB_FILE)
    try:
        with db_conn as current_conn:
            cursor = current_conn.cursor()
            cursor.execute("DELETE FROM channel_prompts WHERE conversation_id = ?", (conversation_id,))
            # Check if any row was actually deleted
            if cursor.rowcount > 0:
                deleted = True
            current_conn.commit()
    except sqlite3.Error as e:
        logging.error(f"Error deleting prompt for channel {conversation_id}: {e}")
    finally:
        if not conn and db_conn: # Only close if connection was created here
            db_conn.close()
    return deleted
