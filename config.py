import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(dotenv_path=Path(__file__).parent / ".env")

JIRA_EMAIL = os.getenv("JIRA_EMAIL")
JIRA_TOKEN = os.getenv("JIRA_TOKEN")

TICKETS_DIR = Path(os.getenv("TICKETS_DIR", "tickets"))
REPOS_DIR = Path(os.getenv("REPOS_DIR", str(Path.home() / "repos")))
