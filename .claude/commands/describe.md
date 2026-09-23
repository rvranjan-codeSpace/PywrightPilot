---
description: Describe this project's purpose, structure, and key commands
allowed-tools: Read, Glob
---

Summarize this project for the user. Read the following files to ground the summary (skip any that don't exist):

1. `CLAUDE.md` — project overview, architecture, and common commands
2. `README.md` — high-level description and key features
3. `pyproject.toml` — dependencies, pytest config, and `base_url`

Then produce a concise summary covering:

- **What it is**: one or two sentences on the project's purpose.
- **Stack**: language, frameworks/tools (e.g. Playwright, Pytest, Allure, Axe, `uv`, `Ruff`).
- **Structure**: key directories (`src/pages`, `src/utilities`, `tests`, etc.) and what each holds.
- **How to run it**: setup and the most common test commands.
- **Notable conventions**: anything a new contributor should know (Page Object Model, test markers, fixtures, DB utilities/slash commands).

Keep the summary tight — headers with a few bullets each, not prose paragraphs.
