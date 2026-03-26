import argparse
from urllib.parse import urlparse

from config import JIRA_EMAIL, JIRA_TOKEN
from formatter import build_markdown
from jira import fetch_issue
from storage import append_task_checkbox, archive_tickets, link_as_task, save_ticket, ticket_path


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-u", "--url",
        help="Jira ticket URL (e.g. https://bloyal.atlassian.net/browse/APP-92)",
    )
    parser.add_argument(
        "-x", "--archive",
        action="store_true",
        help="Archive Done/Closed/Resolved tickets to prev-tickets/",
    )
    parser.add_argument(
        "-t",
        action="store_true",
        help="Save ticket and symlink TASK.md in a selected repo (via fzf)",
    )
    parser.add_argument(
        "-T",
        action="store_true",
        help="Only symlink TASK.md (skip saving the ticket file)",
    )
    parser.add_argument(
        "-a",
        action="store_true",
        help="Save ticket and append a checkbox task entry to TASKS_FILE",
    )
    parser.add_argument(
        "-A",
        action="store_true",
        help="Only append a checkbox task entry to TASKS_FILE (skip saving the ticket file)",
    )
    return parser.parse_args()


def main():
    if not JIRA_EMAIL or not JIRA_TOKEN:
        raise ValueError("JIRA_EMAIL and JIRA_TOKEN required in .env")

    args = parse_args()

    if args.archive:
        archive_tickets()
        return

    if not args.url:
        raise SystemExit("error: -u/--url is required unless --archive is used")

    parsed = urlparse(args.url)
    domain = f"{parsed.scheme}://{parsed.netloc}"
    ticket_key = parsed.path.strip("/").split("/")[-1]

    fields = fetch_issue(domain, ticket_key)
    title = fields.get("summary", "")

    save = args.t or args.a or not (args.T or args.A)
    if save:
        markdown = build_markdown(ticket_key, args.url, fields)
        out_file = save_ticket(markdown, ticket_key)
    else:
        out_file = None

    if args.t or args.T:
        link_as_task(out_file or ticket_path(ticket_key))

    if args.a:
        append_task_checkbox(ticket_key, title, out_file)

    if args.A:
        expected = ticket_path(ticket_key)
        if expected.exists():
            append_task_checkbox(ticket_key, title, expected)
        else:
            answer = input(f"Ticket file not found. Create it? [y/N] ").strip().lower()
            if answer == "y":
                if out_file is None:
                    markdown = build_markdown(ticket_key, args.url, fields)
                    out_file = save_ticket(markdown, ticket_key)
                append_task_checkbox(ticket_key, title, out_file)
            else:
                append_task_checkbox(ticket_key, title)


if __name__ == "__main__":
    main()
