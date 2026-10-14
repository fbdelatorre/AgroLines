"""Render the offline policy without external assets or a Markdown dependency."""

import html
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent / "docs/privacy/offline"


def render():
    source = (ROOT / "politica-privacidade.md").read_text(encoding="utf-8")
    blocks = []
    for paragraph in source.strip().split("\n\n"):
        heading = re.match(r"^(#{1,6}) (.*)$", paragraph)
        if heading:
            level, content = len(heading[1]), heading[2]
            blocks.append(f"<h{level}>{html.escape(content)}</h{level}>")
        else:
            blocks.append("<p>" + html.escape(paragraph.replace("\n", " ")) + "</p>")
    document = (
        '<!doctype html>\n<html lang="pt-BR"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        "<title>Privacidade AgroLines — edição offline</title>"
        "<style>body{max-width:850px;margin:2rem auto;padding:0 1rem;"
        "font-family:system-ui,sans-serif;line-height:1.6;color:#17232a}"
        "h1,h2{line-height:1.25}p{overflow-wrap:anywhere}</style></head><body>\n"
        + "\n".join(blocks)
        + "\n</body></html>\n"
    )
    (ROOT / "politica-privacidade.html").write_text(document, encoding="utf-8")
    plain = re.sub(r"(?m)^#{1,6} ", "", source)
    (ROOT / "politica-privacidade.txt").write_text(plain, encoding="utf-8")


if __name__ == "__main__":
    render()
