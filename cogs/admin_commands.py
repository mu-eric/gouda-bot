# cogs/admin_commands.py
import logging
from discord.ext import commands
import database # Import our database module
import config # Import config for default prompt reference if needed

class AdminCommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name='setprompt')
    @commands.guild_only() # Ensure it's used in a server channel
    async def set_prompt(self, ctx: commands.Context, *, new_prompt: str):
        """Sets a new system prompt *for this channel*.

        This prompt will be saved and used for all future conversations in this channel
        until reset using $resetprompt.
        """
        if not new_prompt:
            await ctx.send("Please provide the new system prompt text after the command.")
            return

        conversation_id = str(ctx.channel.id)

        # Store the new prompt in the database for this channel
        success = database.set_channel_prompt(conversation_id, new_prompt)

        if not success:
            await ctx.send("I encountered an issue trying to save the new prompt for this channel. Please check the logs.")
            return

        logging.info(f"System prompt for channel {conversation_id} updated by {ctx.author} to: '{new_prompt[:100]}...' ")

        # Then clear the history for the current channel
        deleted_count = 0
        try:
            # Call with the specific conversation_id
            deleted_count = database.clear_conversation_history(conversation_id)
            logging.info(f"History for channel {conversation_id} cleared by set_prompt command.")
        except Exception as e:
            logging.exception(f"Error clearing history during set_prompt for channel {conversation_id}: {e}")
            await ctx.send("I encountered an issue trying to clear the history for this channel. Please check the logs.")
            return # Stop here if history clearing failed

        await ctx.send(f"System prompt updated successfully for this channel! I've also cleared my memory of our last {deleted_count} exchanges here to match the new persona.")

    @set_prompt.error
    async def set_prompt_error(self, ctx: commands.Context, error):
        # if isinstance(error, commands.NotOwner): # Keep or remove based on desired permissions
        #     await ctx.send("My apologies, only the bot owner can sculpt my core persona.")
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("You seem to have forgotten the prompt itself. What wisdom were you trying to impart?")
        elif isinstance(error, commands.NoPrivateMessage):
             await ctx.send("Such sensitive operations are best performed within the confines of a server channel, wouldn't you agree?")
        elif isinstance(error, commands.CheckFailure): # If using custom checks or permissions
             await ctx.send("My apologies, you don't seem to have the necessary permissions for that.")
        else:
            logging.error(f"Unhandled error in set_prompt command: {error}")
            await ctx.send("I encountered an issue trying to update the prompt for this channel. Please check the logs.")


    @commands.command(name='clearhistory')
    @commands.has_permissions(manage_messages=True) # Requires 'Manage Messages' permission
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
            await ctx.send("I encountered an issue trying to clear the history for this channel. Please check the logs.")

    @clear_history.error
    async def clear_history_error(self, ctx: commands.Context, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("A noble request, but purging memories requires the 'Manage Messages' permission.")
        elif isinstance(error, commands.NoPrivateMessage):
             await ctx.send("Clearing history pertains to specific channels; this command cannot be used in DMs.")
        else:
            logging.error(f"Unhandled error in clear_history command: {error}")
            await ctx.send("I encountered an issue trying to clear the history for this channel. Please check the logs.")


    @commands.command(name='resetprompt')
    @commands.has_permissions(manage_messages=True) # Requires 'Manage Messages' permission
    @commands.guild_only()
    async def reset_prompt(self, ctx: commands.Context):
        """Resets the system prompt for this channel back to the default.

        This also clears the conversation history for the channel.
        Requires 'Manage Messages' permission.
        """
        conversation_id = str(ctx.channel.id)

        # Attempt to delete the custom prompt setting
        deleted = database.delete_channel_prompt(conversation_id)

        if deleted:
            # If a custom prompt was deleted, clear the history
            deleted_count = database.clear_conversation_history(conversation_id)
            logging.info(f"Custom prompt for channel {conversation_id} reset by {ctx.author}. History cleared ({deleted_count} messages).")
            await ctx.send(f"The custom system prompt for this channel has been reset to the default. I've also cleared our last {deleted_count} exchanges here.")
        elif deleted is False:
            # If delete_channel_prompt returned False, it might be an error or no prompt existed
            # Let's check if a prompt existed to give a better message
            current_prompt = database.get_channel_prompt(conversation_id)
            if current_prompt is None:
                 await ctx.send("This channel is already using the default system prompt. No changes made.")
            else:
                 # This case implies delete_channel_prompt failed despite a prompt existing (logged in DB function)
                 await ctx.send("I encountered an issue trying to reset the prompt for this channel. Please check the logs.")

    @reset_prompt.error
    async def reset_prompt_error(self, ctx: commands.Context, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("I apologize, you need the 'Manage Messages' permission to reset my prompt in this channel.")
        elif isinstance(error, commands.NoPrivateMessage):
            await ctx.send("Prompt resets should be done within a server channel, please.")
        else:
            logging.error(f"Unhandled error in reset_prompt command: {error}")
            await ctx.send("I encountered an issue trying to reset the prompt for this channel. Please check the logs.")


# Make sure the setup function is present for the cog to load
async def setup(bot: commands.Bot):
    await bot.add_cog(AdminCommands(bot))
    logging.info("AdminCommands Cog loaded.")
