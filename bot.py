import os
import discord
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
# Add other environment variables like GCP project ID, etc.
# GOOGLE_PROJECT_ID = os.getenv('GOOGLE_PROJECT_ID')

if not DISCORD_TOKEN:
    print("Error: DISCORD_TOKEN not found in .env file.")
    exit()

# --- Discord Bot Setup ---
intents = discord.Intents.default() # Start with default intents
intents.message_content = True     # Enable message content intent (Privileged Intent)

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')
    await client.change_presence(
        status=discord.Status.online,
        activity=discord.Activity(type=discord.ActivityType.custom, name="🧀 Powered by Gouda 🧀")
    )
    print('Bot is ready and listening!')

@client.event
async def on_message(message):
    # Ignore messages sent by the bot itself
    if message.author == client.user:
        return

    print(f'Message from {message.author}: {message.content}')

    # Basic reply logic (replace with ADK/Dialogflow integration later)
    if message.content.startswith('$hello'):
        await message.channel.send('Hello!')

    # TODO: Add logic to interact with Google Cloud AI services
    # Example: Send message.content to Dialogflow CX or Vertex AI

# --- Run the Bot ---
if __name__ == "__main__":
    try:
        client.run(DISCORD_TOKEN)
    except discord.errors.LoginFailure:
        print("Error: Invalid Discord token. Please check your DISCORD_TOKEN in the .env file.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
