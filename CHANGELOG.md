# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial project structure with `discord.py`, `uv`, `python-dotenv`.
- Integration with Mistral AI API (`mistralai` library v1.x).
- Bot personality configured via system prompt (pretentious cheese connoisseur named Fromage).
- Basic logging setup.
- `.env` file for managing secrets (`DISCORD_TOKEN`, `MISTRAL_API_KEY`).
- `README.md` with setup and usage instructions.
- This `CHANGELOG.md` file.

### Changed
- Updated `mistralai` client usage to align with v1.x (`Mistral` client, `chat.complete_async`).
- Refined system prompt for Mistral AI to establish the "Fromage" persona.

### Removed
- (Placeholder for future removals, e.g., previous LLM integrations if any existed before Mistral)
