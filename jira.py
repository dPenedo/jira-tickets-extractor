import sys

import requests

from config import JIRA_DOMAIN, JIRA_EMAIL, JIRA_TOKEN


def fetch_issue(domain: str, ticket_key: str) -> dict:
    url = f"{domain}/rest/api/3/issue/{ticket_key}"
    response = requests.get(
        url,
        auth=(JIRA_EMAIL, JIRA_TOKEN),
        headers={"Accept": "application/json"},
    )
    if response.status_code != 200:
        print(f"Error {response.status_code}:", response.text)
        sys.exit(1)
    return response.json()["fields"]


def fetch_status(ticket_key: str) -> str:
    if not JIRA_DOMAIN:
        raise ValueError("JIRA_DOMAIN required in .env for --archive")
    fields = fetch_issue(JIRA_DOMAIN, ticket_key)
    return fields["status"]["name"]
