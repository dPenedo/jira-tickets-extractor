# Jira tickets extractor

Pulls Jira tickets via the REST API and converts them to clean, readable markdown files and organized by project. Ready to be used as context for AI models or just for personal reference.

## Platform

Linux and macOS. The `-t` flag requires `fzf` installed and a proper terminal (not a piped shell).

## Requirements

- Python 3.10+
- A Jira Cloud account with an API token
- `fzf` (optional, only needed for `-t`)

## Setup

```bash
git clone https://github.com/youruser/jira-tickets-extractor
cd jira-tickets-extractor
python -m venv env
source env/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Edit `.env` with your credentials and paths:

```env
JIRA_EMAIL=you@example.com
JIRA_TOKEN=your_atlassian_api_token
TICKETS_DIR=/path/to/your/tickets
REPOS_DIR=/path/to/your/repos
```

You can generate an API token at [id.atlassian.com/manage-profile/security/api-tokens](https://id.atlassian.com/manage-profile/security/api-tokens).

## Usage

```bash
python main.py -u https://your-domain.atlassian.net/browse/PROJ-123
```

The ticket is saved as `{TICKETS_DIR}/{PROJECT}/PROJ-123.md`.

### Batch extraction

```bash
for i in $(seq 1 21); do
  python main.py -u "https://your-domain.atlassian.net/browse/CON-$i"
done
```

## Output format

Each ticket is saved as a markdown file with front matter-style metadata followed by the full description and subtasks:

```markdown
# [PROJ-123] Ticket title

**Type:** Story
**Status:** In Progress
**Priority:** Medium
**Assignee:** Jane Doe
**Reporter:** John Smith
**Created:** 2026-01-10
**Updated:** 2026-02-25

**URL:** https://your-domain.atlassian.net/browse/PROJ-123

---

## Description

...

## Subtasks

- [PROJ-124] Subtask title `To Do`
```

Jira's Atlassian Document Format (ADF) is parsed and converted to proper markdown, including headings, lists, nested lists, code blocks, blockquotes, and inline formatting.

## The `-t` flag

```bash
python main.py -u https://your-domain.atlassian.net/browse/PROJ-123 -t
```

After saving the ticket, an `fzf` picker opens over your `REPOS_DIR`. Select a repo and `TASK.md` is created there as a symlink pointing to the saved ticket file. If a `TASK.md` already exists, it gets backed up as `TASK.md.bak` first.

If you work on AI coding tools this is 🔥 — drop any ticket directly into your repo context with one command and your AI assistant has everything it needs.

## License

MIT
# jira-tickets-extractor
