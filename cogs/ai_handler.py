# cogs/ai_handler.py
import logging
import re
import discord
from discord.ext import commands
from mistralai import Mistral
import config  # Import our config module
import database # Import our database module
import time

class AIHandler(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.mistral_client = self.initialize_mistral()

    def initialize_mistral(self):
        """Initializes the Mistral client."""
        if config.MISTRAL_API_KEY:
            try:
                client = Mistral(api_key=config.MISTRAL_API_KEY)
                # Optionally, perform a simple test call here if desired
                logging.info("Mistral AI client initialized successfully.")
                return client
            except Exception as e:
                logging.error(f"Failed to initialize Mistral AI client: {e}")
                return None
        else:
            logging.warning("Mistral API key not found. AI features will be disabled.")
            return None

    def format_history_for_api(self, history: list[dict]) -> list[dict]:
        """Formats the database history into dictionaries for the API."""
        messages = []
        for msg in history:
            # Map db roles ('user', 'assistant') to API roles if needed
            # (Assuming they are already compatible based on previous code)
            role = msg.get('role', 'user') # Default to user if role is missing? Adjust as needed.
            content = msg.get('content', '')
            # Add name field only if role is 'user' and username exists
            name = msg.get('username') if role == 'user' else None

            # Create dictionary, including name only when appropriate
            if name:
                 messages.append({"role": role, "content": content, "name": name})
            else:
                 messages.append({"role": role, "content": content})
        return messages

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """Handles incoming messages, interacts with Mistral AI if mentioned."""
        # Ignore messages from the bot itself
        if message.author == self.bot.user:
            return

        # Ignore messages that don't mention the bot
        if not self.bot.user.mentioned_in(message):
            return

        # Ignore messages starting with the command prefix
        # Use self.bot.command_prefix which is set in main bot.py
        if message.content.startswith(self.bot.command_prefix):
             return

        # Check if Mistral client is available (stored on the cog instance)
        if not self.mistral_client:
            logging.warning("Mistral client not available. Cannot process AI request.")
            # Maybe send a message indicating AI is offline?
            # await message.channel.send("My apologies, my connection to the digital ether seems disrupted. I cannot process this request right now.")
            return

        # Get conversation ID (channel ID)
        conversation_id = str(message.channel.id)

        # Get user display name (use global_name if available, fallback to name)
        user_name = message.author.global_name if message.author.global_name else message.author.name
        # Sanitize username for the 'name' field in dictionary
        # Must be ^[a-zA-Z0-9_-]{1,64}$
        sanitized_user_name = re.sub(r'[^a-zA-Z0-9_-]', '_', user_name)
        if not sanitized_user_name: # Handle empty names after sanitization
            sanitized_user_name = "user"
        sanitized_user_name = sanitized_user_name[:64] # Enforce max length

        # Extract user input, removing the bot mention
        user_input = message.content.replace(f'<@{self.bot.user.id}>', '').strip()
        if not user_input: # Ignore empty messages after removing mention
             return

        logging.info(f"Processing message from {user_name} ({message.author}) in conv {conversation_id}: \"{user_input[:50]}...\"")

        # Save user message to DB
        database.save_message(conversation_id, "user", user_input, username=sanitized_user_name)

        # Retrieve history and format for API
        history = database.get_history(conversation_id, limit=config.HISTORY_LIMIT)
        formatted_history = self.format_history_for_api(history)

        # Add the system prompt as the first message
        # Use the prompt stored on the bot instance (set in main bot.py)
        system_message = {"role": "system", "content": self.bot.current_system_prompt}
        api_messages = [system_message] + formatted_history

        # Call Mistral AI API
        try:
            start_time = time.time()
            chat_response = await self.mistral_client.chat.complete_async(
                 model="mistral-large-latest", # Or your preferred model
                 messages=api_messages,
            )

            if chat_response.choices:
                ai_response = chat_response.choices[0].message.content
                end_time = time.time()
                logging.info(f"Mistral API call successful. Time taken: {end_time - start_time:.2f}s")

                # Save AI response
                database.save_message(conversation_id, "assistant", ai_response)

                # Send AI response to Discord
                await message.channel.send(ai_response)
            else:
                logging.warning("Mistral API returned no choices.")
                await message.channel.send("I pondered your words but couldn't quite form a response.")

        except Exception as e:
            logging.exception(f"Error during Mistral API call or processing: {e}")
            await message.channel.send("Forgive me, a fleeting disturbance in the æther has scrambled my thoughts. Could you try again?")

# This setup function is required for the cog to be loaded by the bot
async def setup(bot: commands.Bot):
    # Pass the bot instance to the Cog
    await bot.add_cog(AIHandler(bot))
    logging.info("AIHandler Cog loaded.")
