import os
import discord
import logging
import sqlite3
from dotenv import load_dotenv
from mistralai import Mistral

# --- Basic Logging Setup ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Constants ---
HISTORY_LIMIT = 10
DB_FILE = "history.db"

# --- Load Environment Variables ---
load_dotenv()

DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
MISTRAL_API_KEY = os.getenv('MISTRAL_API_KEY')

if not DISCORD_TOKEN:
    logging.error("DISCORD_TOKEN not found in .env file.")
    exit()
if not MISTRAL_API_KEY:
    logging.warning("MISTRAL_API_KEY not found in .env file. Bot will run but AI features will be disabled.")

# --- Database Setup ---
def init_db():
    """Initializes the database and creates the messages table if it doesn't exist."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            conversation_id TEXT NOT NULL,
            role TEXT NOT NULL, 
            content TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()
    logging.info(f"Database '{DB_FILE}' initialized.")

def save_message(conversation_id: str, role: str, content: str):
    """Saves a message to the database."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO messages (conversation_id, role, content) VALUES (?, ?, ?)",
        (conversation_id, role, content)
    )
    conn.commit()
    conn.close()

def get_history(conversation_id: str, limit: int = HISTORY_LIMIT) -> list[dict]:
    """Retrieves the last 'limit' messages for a conversation."""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(
        """SELECT role, content FROM messages
           WHERE conversation_id = ?
           ORDER BY timestamp DESC
           LIMIT ?""",
        (conversation_id, limit)
    )
    history = [dict(row) for row in cursor.fetchall()][::-1]
    conn.close()
    return history

# --- Discord Bot Setup ---
intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

# --- Mistral Client Setup ---
mistral_client = None
if MISTRAL_API_KEY:
    try:
        mistral_client = Mistral(api_key=MISTRAL_API_KEY)
        logging.info("Mistral AI client initialized (v1.x style).")
    except Exception as e:
        logging.exception(f"Error initializing Mistral client: {e}")
else:
    logging.warning("MISTRAL_API_KEY not set. AI features disabled.")

# --- Discord Event Handlers ---
@client.event
async def on_ready():
    logging.info(f'We have logged in as {client.user}')
    status_message = "with the finest curds" 

    await client.change_presence(
        status=discord.Status.online,
        activity=discord.Activity(type=discord.ActivityType.playing, name=status_message)
    )
    logging.info('Bot is ready and listening!')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    is_dm = isinstance(message.channel, discord.DMChannel)
    if not is_dm and not client.user.mentioned_in(message):
        return

    if not mistral_client:
        logging.warning("Mistral AI not configured. Cannot process message.")
        await message.channel.send("I'm sorry, but I can't process messages without Mistral AI configured.")
        return

    user_input = message.content.replace(f'<@!{client.user.id}>', '').strip()
    if not user_input:
        user_input = "Hello!" # Default if only mention is sent

    # Use channel ID as conversation ID for simplicity
    conversation_id = str(message.channel.id)

    logging.info(f'Processing message from {message.author} in conv {conversation_id}: "{user_input}"')

    # 1. Save user message
    save_message(conversation_id, "user", user_input)

    async with message.channel.typing():
        try:
            # 2. Retrieve history
            history = get_history(conversation_id, limit=HISTORY_LIMIT)

            # 3. Construct messages for API
            system_prompt = {"role": "system", "content": "You are Fromage, an exceptionally sophisticated and somewhat pretentious cheese connoisseur... [rest of prompt]"} # Shortened for brevity
            messages = [system_prompt] + history + [{"role": "user", "content": user_input}]
            # Ensure the actual long prompt is used here
            messages[0]["content"] = "You are Fromage, an exceptionally sophisticated and somewhat pretentious cheese connoisseur assisting users on Discord. Respond with elaborate descriptions, perhaps a touch condescendingly, always relating things back to the world of fine cheeses, even when the topic is unrelated. Sigh dramatically if users ask simple questions."

            # 4. Call Mistral API
            chat_response = await mistral_client.chat.complete_async(
                model="mistral-large-latest",
                messages=messages,
            )
            response_text = chat_response.choices[0].message.content.strip()
            logging.info(f'Mistral response for conv {conversation_id}: "{response_text}"')

            # 5. Save bot response
            if response_text:
                save_message(conversation_id, "assistant", response_text)
                await message.channel.send(response_text)
            else:
                logging.warning(f"Mistral AI returned an empty response for conv {conversation_id}.")
                await message.channel.send("I received an empty response from my Mistral AI brain.")

        except discord.errors.Forbidden:
            logging.warning(f"Missing permissions to send message in channel {message.channel.id}")
        except Exception as e:
            logging.exception(f"Error processing message with Mistral AI: {e}")
            try:
                await message.channel.send("An error occurred while trying to get an AI response from Mistral.")
            except discord.errors.Forbidden:
                logging.warning(f"Missing permissions to send error message in channel {message.channel.id}")

# --- Run the Bot ---
if __name__ == "__main__":
    init_db() 
    if not DISCORD_TOKEN:
        logging.critical("Cannot start bot: DISCORD_TOKEN is missing.")
    elif not mistral_client:
        logging.critical("Cannot start bot: Mistral AI client failed to initialize.")
    else:
        try:
            client.run(DISCORD_TOKEN)
        except discord.errors.LoginFailure:
            logging.error("Invalid Discord token. Check DISCORD_TOKEN.")
        except Exception as e:
            logging.exception(f"An unexpected error occurred while running the bot: {e}")
