from adf import adf_to_text


def build_markdown(ticket_key: str, url: str, fields: dict) -> str:
    title = fields.get("summary", "")
    status = fields.get("status", {}).get("name", "")
    assignee = (fields.get("assignee") or {}).get("displayName", "Unassigned")
    reporter = (fields.get("reporter") or {}).get("displayName", "")
    priority = fields.get("priority", {}).get("name", "")
    issue_type = fields.get("issuetype", {}).get("name", "")
    created = (fields.get("created") or "")[:10]
    updated = (fields.get("updated") or "")[:10]
    labels = fields.get("labels") or []
    description_adf = fields.get("description")
    description = adf_to_text(description_adf).strip() if description_adf else "_No description_"
    subtasks = fields.get("subtasks") or []

    lines = [
        f"# [{ticket_key}] {title}",
        "",
        f"**Type:** {issue_type}  ",
        f"**Status:** {status}  ",
        f"**Priority:** {priority}  ",
        f"**Assignee:** {assignee}  ",
        f"**Reporter:** {reporter}  ",
        f"**Created:** {created}  ",
        f"**Updated:** {updated}  ",
    ]

    if labels:
        lines.append(f"**Labels:** {', '.join(labels)}  ")

    lines += ["", f"**URL:** {url}", "", "---", "", "## Description", "", description]

    if subtasks:
        lines += ["", "## Subtasks", ""]
        for s in subtasks:
            s_key = s.get("key", "")
            s_title = s.get("fields", {}).get("summary", "")
            s_status = s.get("fields", {}).get("status", {}).get("name", "")
            lines.append(f"- [{s_key}] {s_title} `{s_status}`")

    return "\n".join(lines)
