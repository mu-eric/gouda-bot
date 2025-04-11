# Gouda Bot

A Discord bot integrating Google AI services (using ADK principles).

## Project Overview

This bot is designed to interact with users on Discord, leveraging Google Cloud's AI capabilities. It aims to follow the principles and potentially utilize the [Google Agent Development Kit (ADK)](https://google.github.io/adk-docs/), a framework for building modular and deployable AI agents integrated with Google's ecosystem (like Gemini models and Vertex AI).

## Tech Stack

*   **Backend:** Python 3.12
*   **Discord API:** `discord.py`
*   **Agent/NLU:** Google Cloud AI Services & Google ADK (via `google-cloud-aiplatform`, `google-adk`, etc.)
*   **Package Management:** `uv` with `pyproject.toml`
*   **Environment:** VS Code Dev Container (Ubuntu)
*   **Configuration:** `python-dotenv` (`.env` file)

## Setup

1.  **Prerequisites:**
    *   Docker Desktop
    *   VS Code with the Dev Containers extension
    *   Discord Bot Token (from Discord Developer Portal)
    *   Google Cloud Project with relevant APIs enabled (e.g., Vertex AI, Dialogflow)
    *   Google Cloud credentials configured for the environment (details TBD)
2.  **Clone the repository:** `git clone <repository-url>`
3.  **Create `.env` file:** Copy `.env.example` (if exists) or create `.env` in the project root and add your `DISCORD_TOKEN` and any necessary Google Cloud credentials/variables.
    ```
    DISCORD_TOKEN=YOUR_DISCORD_BOT_TOKEN_HERE
    # GOOGLE_APPLICATION_CREDENTIALS=/path/to/your/keyfile.json (Example)
    # GOOGLE_PROJECT_ID=your-gcp-project-id
    ```
4.  **Open in Dev Container:** Open the project folder in VS Code. It should prompt you to "Reopen in Container".
5.  **Run the bot:** Once the container is built and VS Code is connected, run the bot from the integrated terminal:
    ```bash
    python bot.py
    ```

## Development

*   Dependencies are managed in `pyproject.toml`.
*   Use `uv pip install --system -e '.[dev]'` inside the container to install/update dependencies.

## Contributing

(Add contribution guidelines later if applicable)

## License

[MIT License](https://choosealicense.com/licenses/mit/)