# bot.py
import discord
import logging
import os
import asyncio
from discord.ext import commands

# Import our custom modules
import config
import database

# --- Basic Logging Setup ---
# Configure logging level and format
log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
logging.basicConfig(level=getattr(logging, log_level, logging.INFO),
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# Suppress overly verbose discord logs if desired
# logging.getLogger('discord').setLevel(logging.WARNING)
# logging.getLogger('discord.http').setLevel(logging.WARNING)
# logging.getLogger('discord.gateway').setLevel(logging.WARNING)

# --- Bot Setup ---
# Define necessary intents
intents = discord.Intents.default()
intents.message_content = True  # Required for reading message content
intents.members = True # Potentially needed for username resolution, enable if needed
intents.guilds = True # Needed for guild-only commands and context

# Initialize the bot
bot = commands.Bot(command_prefix="$", intents=intents)

# Store the system prompt on the bot instance for Cogs to access
# Initialize with the default from config
bot.current_system_prompt = config.DEFAULT_SYSTEM_PROMPT

# --- Cog Loading ---
async def load_extensions():
    """Loads all cogs from the 'cogs' directory."""
    cogs_dir = "cogs"
    if not os.path.exists(cogs_dir):
        logging.warning(f"Cogs directory '{cogs_dir}' not found. No cogs will be loaded.")
        return

    for filename in os.listdir(cogs_dir):
        if filename.endswith(".py") and not filename.startswith("_"):
            extension = f"{cogs_dir}.{filename[:-3]}"
            try:
                await bot.load_extension(extension)
                logging.info(f"Successfully loaded extension: {extension}")
            except commands.ExtensionNotFound:
                logging.error(f"Extension not found: {extension}")
            except commands.ExtensionAlreadyLoaded:
                logging.warning(f"Extension already loaded: {extension}")
            except commands.NoEntryPointError:
                logging.error(f"Extension '{extension}' has no setup() function.")
            except commands.ExtensionFailed as e:
                logging.exception(f"Extension {extension} failed to load: {e.args[0]}") # Log the original exception
            except Exception as e:
                logging.exception(f"An unexpected error occurred loading extension {extension}: {e}")

# --- Bot Events ---
@bot.event
async def on_ready():
    """Called when the bot is ready and connected to Discord."""
    logging.info(f'Logged in as {bot.user.name} ({bot.user.id})')
    logging.info(f'discord.py version: {discord.__version__}')
    logging.info('------')
    # Set a status (optional)
    status_message = "CheeseCraft | $help"
    await bot.change_presence(
        status=discord.Status.online,
        activity=discord.Activity(type=discord.ActivityType.playing, name=status_message)
    )
    logging.info("Bot is ready and listening!")

# --- Run the Bot ---
async def main():
    """Main entry point: Initializes DB, loads cogs, runs bot."""
    # Ensure DB is initialized *before* starting the bot
    database.init_db()

    # Load cogs
    await load_extensions()

    # Start the bot
    if not config.DISCORD_TOKEN:
        logging.critical("Cannot start bot: DISCORD_TOKEN is missing.")
    else:
        try:
            await bot.start(config.DISCORD_TOKEN)
        except discord.errors.LoginFailure:
            logging.error("Invalid Discord token provided. Please check your .env file.")
        except discord.errors.PrivilegedIntentsRequired as e:
            logging.error(f"Privileged Intents Error: {e}. Make sure required intents (e.g., Message Content) are enabled in the Discord Developer Portal.")
        except Exception as e:
            logging.exception(f"An unexpected error occurred while running the bot: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Bot shutting down gracefully.")
    except Exception as e:
        logging.exception(f"Critical error during startup or shutdown: {e}")