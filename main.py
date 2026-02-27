import argparse
from urllib.parse import urlparse

from config import JIRA_EMAIL, JIRA_TOKEN
from formatter import build_markdown
from jira import fetch_issue
from storage import link_as_task, save_ticket


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-u", "--url",
        required=True,
        help="Jira ticket URL (e.g. https://bloyal.atlassian.net/browse/APP-92)",
    )
    parser.add_argument(
        "-t", "--task",
        action="store_true",
        help="Also symlink TASK.md in a selected repo (via fzf)",
    )
    return parser.parse_args()


def main():
    if not JIRA_EMAIL or not JIRA_TOKEN:
        raise ValueError("JIRA_EMAIL and JIRA_TOKEN required in .env")

    args = parse_args()

    parsed = urlparse(args.url)
    domain = f"{parsed.scheme}://{parsed.netloc}"
    ticket_key = parsed.path.strip("/").split("/")[-1]

    fields = fetch_issue(domain, ticket_key)
    markdown = build_markdown(ticket_key, args.url, fields)
    out_file = save_ticket(markdown, ticket_key)

    if args.task:
        link_as_task(out_file)


if __name__ == "__main__":
    main()
