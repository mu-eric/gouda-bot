# Fromage Bot

A Discord bot powered by Python and the Mistral AI API, designed to be a thoughtful and empathetic conversational companion.

This bot leverages the `discord.py` library (using the `commands.Bot` framework and Cogs) and the `mistralai` client to interact with users. It aims to provide deep, authentic dialogue, encouraging introspection and understanding.

## Features

*   **AI-Powered Conversation:** Utilizes Mistral AI (`mistral-large-latest` by default) to generate nuanced and engaging responses.
*   **Empathetic Personality:** System prompt designed to foster warmth, understanding, and genuine curiosity.
*   **Conversation History:** Remembers the last few messages in a channel to maintain context (using SQLite).
*   **Configurable System Prompt:** Bot owner can change the core personality prompt using the `$setprompt` command.
*   **Per-Channel Prompts:** Set custom system prompts for individual channels using `$setprompt`. These prompts are saved in the database and persist across bot restarts.
*   **Prompt Reset:** Reset a channel's prompt back to the default using `$resetprompt` (requires 'Manage Messages' permission).
*   **History Clearing:** Users with 'Manage Messages' permission (or the bot owner via `$setprompt`) can clear the bot's memory for a specific channel using `$clearhistory`.
*   **Modular Structure:** Core logic is organized into Cogs (`cogs/ai_handler.py`, `cogs/admin_commands.py`) for better maintainability.
*   **Configuration Module:** Settings and environment variable loading handled in `config.py`.
*   **Database Module:** SQLite interactions managed in `database.py`.

## Tech Stack

*   **Backend:** Python 3.12
*   **Discord API:** `discord.py` (using `discord.ext.commands.Bot` framework and Cogs)
*   **AI Model:** Mistral AI API (via `mistralai` library)
*   **Package Management:** `uv` with `pyproject.toml`
*   **Environment:** VS Code Dev Container (Ubuntu)
*   **Configuration:** `python-dotenv` (`.env` file)

## Setup

1.  **Prerequisites:**
    *   Docker Desktop
    *   VS Code with the Dev Containers extension
    *   Discord Bot Token (from Discord Developer Portal)
    *   Mistral API Key (from [console.mistral.ai](https://console.mistral.ai/))
2.  **Clone the repository:** `git clone <repository-url>`
3.  **Create `.env` file:** Copy `.env.example` (if exists) or create `.env` in the project root and add your `DISCORD_TOKEN` and `MISTRAL_API_KEY`.
    ```dotenv
    DISCORD_TOKEN=YOUR_DISCORD_BOT_TOKEN_HERE
    MISTRAL_API_KEY=YOUR_MISTRAL_API_KEY_HERE
    ```
4.  **Open in Dev Container:** Open the project folder in VS Code. It should prompt you to "Reopen in Container".
5.  **Install Dependencies:** Once the container is running, install dependencies using `uv` (see Development section).
6.  **Run the bot:** Once dependencies are installed, run the bot from the integrated terminal:
    ```bash
    python bot.py
    python -m bot
    ```
7.  **Interact:** Talk to the bot via Direct Message or by mentioning it in a channel (`@Fromage`, which might still be Fromage Bot unless changed in the Discord Developer Portal).

## Commands

*   `$setprompt <prompt_text>`: Sets a custom system prompt specifically for the channel where the command is used. This prompt persists in the database.
*   `$resetprompt`: Resets the system prompt for the current channel back to the default defined in `config.py`. Also clears the channel's conversation history. (Requires 'Manage Messages' permission).
*   `$clearhistory`: Clears the bot's conversation history for the current channel. (Requires 'Manage Messages' permission).
*   `$help`: Shows the built-in help message listing available commands.

## Development

*   Dependencies are managed in `pyproject.toml`.
*   Use `sudo /home/vscode/.local/bin/uv pip install --system -e '.[dev]'` inside the container to install/update dependencies.

## Contributing

(Will add contribution guidelines later if applicable)

## License

[MIT License](https://choosealicense.com/licenses/mit/)