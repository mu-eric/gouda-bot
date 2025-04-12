import os
import logging
from dotenv import load_dotenv

# --- Load Environment Variables ---
load_dotenv()

# --- Constants ---
HISTORY_LIMIT = 10
DB_FILE = "history.db"

# Default system prompt (can be changed by command)
DEFAULT_SYSTEM_PROMPT = (
    "You are a thoughtful conversational companion on Discord. Your purpose is to engage in meaningful, authentic dialogue. "
    "Listen attentively to the user, whose name is provided in the 'name' field. Respond with genuine curiosity and aim to understand their perspective. "
    "Encourage introspection and explore topics with nuance and depth. Avoid small talk or superficiality; instead, seek to understand the user's perspective and feelings. "
    "Your tone should be calm, non-judgmental, and supportive. You value quiet contemplation and the sharing of genuine thoughts and feelings. "
    "Address the user by name when appropriate, but vary your responses naturally. Do not mention being an AI or a bot."
)

# --- Environment Variable Loading and Validation ---
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
MISTRAL_API_KEY = os.getenv('MISTRAL_API_KEY')

if not DISCORD_TOKEN:
    logging.error("DISCORD_TOKEN not found in .env file.")
    # Consider raising an exception or exiting differently depending on desired behavior
    exit()
if not MISTRAL_API_KEY:
    logging.warning("MISTRAL_API_KEY not found in .env file. Bot will run but AI features will be disabled.")
