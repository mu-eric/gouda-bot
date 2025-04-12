# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased] - YYYY-MM-DD

## [0.3.0] - 2025-04-12

### Added
- Per-channel system prompts: The bot can now have different personalities/prompts set for individual channels.
- `$resetprompt` command: Allows users with 'Manage Messages' permission to reset a channel's custom prompt back to the default.
- Database persistence for channel prompts: Custom prompts set via `$setprompt` are now stored in the `history.db` SQLite database and persist across restarts.

### Changed
- `$setprompt` command now sets the system prompt only for the specific channel where it is used, not globally for the bot.
- Refactored prompt handling in `AIHandler` cog to fetch the appropriate prompt (channel-specific or default) from the database or config before calling the AI.
- Removed global `bot.current_system_prompt` attribute.
- Updated database schema (`database.py`) to include a `channel_prompts` table.

### Fixed
- Corrected Mistral API call structure in `AIHandler` to use `chat.complete_async`.
- Fixed indentation errors in `AIHandler` after refactoring.
- Updated bot status message in `on_ready` to show correct `$help` prefix.

## [0.2.0] - 2025-04-12

### Added
- Added `$setprompt` command for the bot owner to change the system prompt dynamically. This also clears the current channel's history.
- Added `$clearhistory` command for users with "Manage Messages" permission to clear the bot's message history in the current channel.
- Added `username` column to the message history database (`history.db`).
- Initial project setup with basic Discord connection and Mistral AI ping.
- SQLite database for conversation history.
- Basic logging.
- Username tracking in database and API calls.

### Changed
- Switched from `discord.Client` to `discord.ext.commands.Bot` to support bot commands.
- Refined the default system prompt multiple times to achieve a more witty and engaging persona, less purely helpful or overly pretentious.
- Message history sent to Mistral AI now includes sanitized usernames via the `name` field for user messages.
- Updated bot status message.
- Updated Mistral AI client usage to `mistralai` library v1.x (`Mistral` client, `chat.complete_async`).
- **Major Refactor:** Migrated core logic into `discord.py` Cogs (`cogs/admin_commands.py`, `cogs/ai_handler.py`).
- **Major Refactor:** Moved configuration loading and constants to `config.py`.
- **Major Refactor:** Moved database functions to `database.py`.
- **Major Personality Shift:** Updated default system prompt from 'cheese connoisseur' to 'thoughtful, empathetic companion' targeting INFJ/INFP interaction styles.

### Fixed
- Ensured bot checks for `send_messages` permission before attempting to send messages, preventing crashes in channels where it lacks permission.
- Added basic error handling for commands (`$setprompt`, `$clearhistory`).
- Ensured database initialization (`init_db`) occurs before bot attempts database operations on startup.

### Removed
- System prompt simplification (reverted to more detailed version in config).
- (Placeholder for future removals, e.g., previous LLM integrations if any existed before Mistral)

## [0.1.0] - 2025-04-10

### Added
- Initial version of the bot.
