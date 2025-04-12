# cogs/admin_commands.py
import logging
from discord.ext import commands
import database # Import our database module

class AdminCommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name='setprompt')
    @commands.is_owner() # Restrict to bot owner
    @commands.guild_only() # Ensure it's used in a server channel
    async def set_prompt(self, ctx: commands.Context, *, new_prompt: str):
        """Sets a new system prompt for Fromage (Bot Owner only)."""
        if not new_prompt:
            await ctx.send("Please provide the new system prompt text after the command.")
            return

        # Store the new prompt on the bot instance itself
        # This assumes bot.current_system_prompt is initialized in the main bot.py
        self.bot.current_system_prompt = new_prompt
        logging.info(f"System prompt updated by {ctx.author} to: '{new_prompt[:100]}...' ")

        # Then clear the history for the current channel
        conversation_id = str(ctx.channel.id)
        deleted_count = 0
        try:
            # Call with the specific conversation_id
            deleted_count = database.clear_conversation_history(conversation_id)
            logging.info(f"History for channel {conversation_id} cleared by set_prompt command.")
        except Exception as e:
            logging.exception(f"Error clearing history during set_prompt for channel {conversation_id}: {e}")
            await ctx.send("System prompt updated, but I encountered an issue clearing the history for this channel.")
            return # Stop here if history clearing failed

        await ctx.send(f"System prompt updated successfully! I've also cleared my memory of our last {deleted_count} exchanges in this channel to match the new persona.")

    @set_prompt.error
    async def set_prompt_error(self, ctx: commands.Context, error):
        if isinstance(error, commands.NotOwner):
            await ctx.send("My apologies, only the bot owner can sculpt my core persona.")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("You seem to have forgotten the prompt itself. What wisdom were you trying to impart?")
        elif isinstance(error, commands.NoPrivateMessage):
             await ctx.send("Such sensitive operations are best performed within the confines of a server channel, wouldn't you agree?")
        else:
            logging.error(f"Unhandled error in set_prompt command: {error}")
            await ctx.send("An unexpected difficulty arose while attempting to update my prompt.")


    @commands.command(name='clearhistory')
    @commands.has_permissions(manage_messages=True) # Require 'Manage Messages' permission
    @commands.guild_only() # Ensure it's used in a server channel
    async def clear_history(self, ctx: commands.Context):
        """Clears Fromage's memory (message history) for this channel."""
        conversation_id = str(ctx.channel.id)
        deleted_count = 0
        try:
            # Call with the specific conversation_id
            deleted_count = database.clear_conversation_history(conversation_id)
            await ctx.send(f"Very well. I have purged my memory of our last {deleted_count} exchanges in this channel. A fresh start, perhaps?" if deleted_count > 0 else "My memory of this channel is already pristine.")
        except Exception as e:
            logging.exception(f"Error clearing history for channel {conversation_id}: {e}")
            await ctx.send("Ah, forgive me. I encountered a slight difficulty whilst clearing my memory banks.")

    @clear_history.error
    async def clear_history_error(self, ctx: commands.Context, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("A noble request, but purging memories requires the 'Manage Messages' permission.")
        elif isinstance(error, commands.NoPrivateMessage):
             await ctx.send("Clearing history pertains to specific channels; this command cannot be used in DMs.")
        else:
            logging.error(f"Unhandled error in clear_history command: {error}")
            await ctx.send("An unexpected difficulty arose while attempting to clear the history.")

# This setup function is required for the cog to be loaded by the bot
async def setup(bot: commands.Bot):
    await bot.add_cog(AdminCommands(bot))
    logging.info("AdminCommands Cog loaded.")
