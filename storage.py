import subprocess
from pathlib import Path

from config import REPOS_DIR, TICKETS_DIR


def save_ticket(markdown: str, ticket_key: str) -> Path:
    project_key = ticket_key.split("-")[0]
    out_dir = TICKETS_DIR / project_key
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / f"{ticket_key}.md"
    out_file.write_text(markdown, encoding="utf-8")
    print(f"Saved: {out_file}")
    return out_file


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
