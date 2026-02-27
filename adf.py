def adf_to_text(node: dict) -> str:
    """Recursively convert an Atlassian Document Format node to markdown."""
    if not node:
        return ""

    node_type = node.get("type", "")
    content = node.get("content", [])
    text = node.get("text", "")

    if node_type == "text":
        marks = {m["type"] for m in node.get("marks", [])}
        if "code" in marks:
            return f"`{text}`"
        if "strong" in marks:
            return f"**{text}**"
        if "em" in marks:
            return f"*{text}*"
        return text

    if node_type == "hardBreak":
        return "\n"

    if node_type == "paragraph":
        return "".join(adf_to_text(c) for c in content) + "\n\n"

    if node_type == "heading":
        level = node.get("attrs", {}).get("level", 2)
        inner = "".join(adf_to_text(c) for c in content).strip()
        return f"{'#' * level} {inner}\n\n" if inner else ""

    if node_type == "bulletList":
        return "".join(adf_to_text(c) for c in content)

    if node_type == "orderedList":
        lines = []
        for i, item in enumerate(content, 1):
            parts = []
            for c in item.get("content", []):
                if c.get("type") in ("bulletList", "orderedList"):
                    sub = adf_to_text(c).strip()
                    parts.append("\n".join("   " + line for line in sub.splitlines()))
                else:
                    parts.append(adf_to_text(c).strip())
            lines.append(f"{i}. " + "\n".join(p for p in parts if p))
        return "\n".join(lines) + "\n\n"

    if node_type == "listItem":
        return "- " + "".join(adf_to_text(c) for c in content).strip() + "\n"

    if node_type == "codeBlock":
        lang = node.get("attrs", {}).get("language", "")
        inner = "".join(adf_to_text(c) for c in content)
        return f"```{lang}\n{inner}\n```\n\n"

    if node_type == "blockquote":
        inner = "".join(adf_to_text(c) for c in content)
        return "\n".join(f"> {line}" for line in inner.splitlines()) + "\n\n"

    if node_type == "inlineCard":
        url = node.get("attrs", {}).get("url", "")
        return f"[{url}]({url})"

    return "".join(adf_to_text(c) for c in content)
