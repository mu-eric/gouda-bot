# Fromage Bot

A Discord bot integrating Mistral AI's API for intelligent (and slightly pretentious) responses.

## Project Overview

This bot, operating under the persona "Fromage," is designed to interact with users on Discord. It leverages the Mistral AI API (e.g., `mistral-large-latest`) for natural language understanding and conversation generation, embodying the personality of a sophisticated (and somewhat snobby) cheese connoisseur.

## Tech Stack

*   **Backend:** Python 3.12
*   **Discord API:** `discord.py`
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
    ```
7.  **Interact:** Talk to the bot via Direct Message or by mentioning it in a channel (`@Fromage`, which might still be Gouda Bot unless changed in the Discord Developer Portal).

## Development

*   Dependencies are managed in `pyproject.toml`.
*   Use `sudo /home/vscode/.local/bin/uv pip install --system -e '.[dev]'` inside the container to install/update dependencies.

## Contributing

(Add contribution guidelines later if applicable)

## License

[MIT License](https://choosealicense.com/licenses/mit/)