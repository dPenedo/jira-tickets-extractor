import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(dotenv_path=Path(__file__).parent / ".env")

JIRA_EMAIL = os.getenv("JIRA_EMAIL")
JIRA_TOKEN = os.getenv("JIRA_TOKEN")
JIRA_DOMAIN = os.getenv("JIRA_DOMAIN", "")

TICKETS_DIR = Path(os.getenv("TICKETS_DIR", "tickets"))
REPOS_DIR = Path(os.getenv("REPOS_DIR", str(Path.home() / "repos")))
TASKS_FILE = Path(os.getenv("TASKS_FILE", "")) if os.getenv("TASKS_FILE") else None

# "minimal" → CON-32.md  |  "full" → CON-32_ITSugar-duplicate-line-Uids.md
FILENAME_FORMAT = os.getenv("FILENAME_FORMAT", "minimal")

# "markdown" → [CON-32 — title](path)  |  "wikilink" → [[CON-32_ITSugar-...]]
LINK_FORMAT = os.getenv("LINK_FORMAT", "markdown")
