import re
import subprocess
from pathlib import Path

from config import FILENAME_FORMAT, LINK_FORMAT, REPOS_DIR, TASKS_FILE, TICKETS_DIR

DONE_STATUSES = {"done", "closed", "resolved"}
PREV_TICKETS_DIR = TICKETS_DIR.parent / "prev-tickets"


def _slugify(text: str) -> str:
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text.strip())
    return text.strip("-")


def _filename_stem(ticket_key: str, title: str = "") -> str:
    if FILENAME_FORMAT == "full" and title:
        return f"{ticket_key}_{_slugify(title)}"
    return ticket_key


def save_ticket(markdown: str, ticket_key: str, title: str = "") -> Path:
    project_key = ticket_key.split("-")[0]
    out_dir = TICKETS_DIR / project_key
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / f"{_filename_stem(ticket_key, title)}.md"
    out_file.write_text(markdown, encoding="utf-8")
    print(f"Saved: {out_file}")
    return out_file


def ticket_path(ticket_key: str, title: str = "") -> Path:
    project_key = ticket_key.split("-")[0]
    out_dir = TICKETS_DIR / project_key
    if FILENAME_FORMAT == "full":
        existing = sorted(out_dir.glob(f"{ticket_key}_*.md"))
        if existing:
            return existing[0]
    return out_dir / f"{_filename_stem(ticket_key, title)}.md"


def _format_link(ticket_key: str, title: str, ticket_file: Path | None) -> str:
    path = ticket_file or ticket_path(ticket_key, title)
    if LINK_FORMAT == "wikilink":
        return f"[[{path.stem}]]"
    resolved = path.resolve()
    return f"[{ticket_key} — {title}]({resolved})"


def append_task_checkbox(ticket_key: str, title: str, ticket_file: Path | None = None):
    if not TASKS_FILE:
        print("TASKS_FILE not set in .env, skipping task append.")
        return
    tasks_path = Path(str(TASKS_FILE).replace("~", str(Path.home())))
    tasks_path.parent.mkdir(parents=True, exist_ok=True)

    entry = f"- [ ] {_format_link(ticket_key, title, ticket_file)}\n"
    project_key = ticket_key.split("-")[0]
    section_header = f"## {project_key}"

    if not tasks_path.exists():
        tasks_path.write_text(f"{section_header}\n\n{entry}", encoding="utf-8")
        print(f"Task added to {tasks_path}")
        return

    lines = tasks_path.read_text(encoding="utf-8").splitlines(keepends=True)

    # Find the target section and insert before the next section or EOF
    section_start = None
    insert_at = None
    for i, line in enumerate(lines):
        if line.strip() == section_header or line.strip().startswith(section_header + " "):
            section_start = i
        elif section_start is not None and line.startswith("## "):
            insert_at = i
            break

    if section_start is None:
        # Section doesn't exist — append it at the end
        if lines and not lines[-1].endswith("\n"):
            lines.append("\n")
        lines.append(f"\n{section_header}\n\n{entry}")
    else:
        if insert_at is None:
            insert_at = len(lines)
        # Insert before trailing blank lines of the section
        while insert_at > section_start and lines[insert_at - 1].strip() == "":
            insert_at -= 1
        lines.insert(insert_at, entry)

    tasks_path.write_text("".join(lines), encoding="utf-8")
    print(f"Task added to {tasks_path}")


def archive_tickets():
    from jira import fetch_status

    if not TICKETS_DIR.exists():
        print("Tickets directory not found.")
        return

    index_path = TICKETS_DIR / "INDEX.md"
    archived_keys = []

    for project_dir in sorted(TICKETS_DIR.iterdir()):
        if not project_dir.is_dir():
            continue
        project_key = project_dir.name

        for ticket_file in sorted(project_dir.glob("*.md")):
            m = re.match(r"^([A-Z]+-\d+)", ticket_file.stem)
            if not m:
                continue
            ticket_key = m.group(1)

            status = fetch_status(ticket_key)
            if status.lower() not in DONE_STATUSES:
                continue

            dest_dir = PREV_TICKETS_DIR / project_key
            dest_dir.mkdir(parents=True, exist_ok=True)

            files_to_move = [ticket_file] + sorted(project_dir.glob(f"{ticket_key}-*.md"))
            for f in files_to_move:
                f.rename(dest_dir / f.name)
                print(f"Archived: {f.name}")
            archived_keys.append(ticket_key)

    if archived_keys and index_path.exists():
        lines = index_path.read_text(encoding="utf-8").splitlines(keepends=True)
        filtered = [l for l in lines if not any(key in l for key in archived_keys)]
        index_path.write_text("".join(filtered), encoding="utf-8")
        print(f"Updated INDEX.md: removed {len(archived_keys)} entr{'y' if len(archived_keys) == 1 else 'ies'}")

    if not archived_keys:
        print("No tickets to archive.")


def link_as_task(out_file: Path):
    dirs = sorted(d.name for d in REPOS_DIR.iterdir() if d.is_dir())
    result = subprocess.run(
        ["fzf", "--prompt=Select repo: "],
        input="\n".join(dirs),
        text=True,
        stdout=subprocess.PIPE,
    )
    if result.returncode != 0 or not result.stdout.strip():
        print("No repo selected, skipping TASK.md.")
        return
    chosen = result.stdout.strip()
    task_file = REPOS_DIR / chosen / "TASK.md"
    if task_file.exists() or task_file.is_symlink():
        bak = task_file.with_suffix(".md.bak")
        task_file.rename(bak)
        print(f"Backed up existing TASK.md to {bak.name}")
    task_file.symlink_to(out_file)
    print(f"Symlinked: {task_file} -> {out_file}")
