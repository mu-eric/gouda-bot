import os
import discord
import logging
import asyncio
from dotenv import load_dotenv
from mistralai import Mistral # Use the unified Mistral client

# --- Basic Logging Setup ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Load Environment Variables ---
load_dotenv()

DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
MISTRAL_API_KEY = os.getenv('MISTRAL_API_KEY') # API Key for Mistral

if not DISCORD_TOKEN:
    logging.error("DISCORD_TOKEN not found in .env file.")
    exit()
if not MISTRAL_API_KEY:
    logging.warning("MISTRAL_API_KEY not found in .env file. Bot will run but AI features will be disabled.")

# --- Discord Bot Setup ---
intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

# --- Mistral Client Setup ---
mistral_client = None
if MISTRAL_API_KEY:
    try:
        # Use the unified client
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
    status_message = "🧀 Powered by Gouda 🧀"
    if mistral_client:
        status_message = "🧀 Powered by Gouda & Mistral 🧀"

    await client.change_presence(
        status=discord.Status.online,
        activity=discord.Activity(type=discord.ActivityType.custom, name=status_message)
    )
    logging.info('Bot is ready and listening!')

@client.event
async def on_message(message):
    # Ignore messages sent by the bot itself
    if message.author == client.user:
        return

    # Respond if bot is mentioned or it's a DM
    is_dm = isinstance(message.channel, discord.DMChannel)
    if not is_dm and not client.user.mentioned_in(message):
        return

    # Check if Mistral client is available
    if not mistral_client:
        logging.warning("Mistral AI not configured. Cannot process message.")
        # await message.channel.send("My Mistral AI brain is offline right now.")
        return

    user_input = message.content.replace(f'<@!{client.user.id}>', '').strip()
    if not user_input:
        user_input = "Hello!" # Default if only mention is sent

    logging.info(f'Processing message from {message.author}: "{user_input}"')

    # Indicate the bot is thinking
    async with message.channel.typing():
        try:
            messages = [
                {"role": "system", "content": "You are Fromage, an exceptionally sophisticated and somewhat pretentious cheese connoisseur assisting users on Discord. Respond with elaborate descriptions, perhaps a touch condescendingly, always relating things back to the world of fine cheeses, even when the topic is unrelated. Sigh dramatically if users ask simple questions."},
                {"role": "user", "content": user_input}
            ]

            # Use the new async completion method
            chat_response = await mistral_client.chat.complete_async(
                model="mistral-large-latest", # Or choose another model like mistral-small
                messages=messages,
                # temperature=0.7 # Optional parameter
            )

            # Extract the response text
            response_text = chat_response.choices[0].message.content.strip()
            logging.info(f'Mistral response: "{response_text}"')

            # Send the response back to Discord
            if response_text:
                await message.channel.send(response_text)
            else:
                logging.warning("Mistral AI returned an empty response.")
                await message.channel.send("I received an empty response from my AI brain.")

        except discord.errors.Forbidden:
            logging.warning(f"Missing permissions to send message in channel {message.channel.id}")
        except Exception as e:
            logging.exception(f"Error processing message with Mistral AI: {e}")
            try:
                await message.channel.send("An error occurred while trying to get an AI response.")
            except discord.errors.Forbidden:
                logging.warning(f"Missing permissions to send error message in channel {message.channel.id}")

# --- Run the Bot ---
if __name__ == "__main__":
    if not DISCORD_TOKEN:
        logging.critical("Cannot start bot: DISCORD_TOKEN is missing.")
    # Optional: Check if Mistral client is loaded
    # elif not mistral_client:
    #     logging.critical("Cannot start bot: Mistral AI client failed to initialize.")
    else:
        try:
            client.run(DISCORD_TOKEN)
        except discord.errors.LoginFailure:
            logging.error("Invalid Discord token. Check DISCORD_TOKEN.")
        except Exception as e:
            logging.exception(f"An unexpected error occurred while running the bot: {e}")
