"""A knowledge map as something you can keep — Markdown, or a page you print.

**No PDF library, and that is the trade rather than a shortfall.** `reportlab`
and `weasyprint` are exactly the kind of dependency this project has turned down
five times (`beautifulsoup4`, `python-pptx`, `watchdog`, `send2trash`,
`APScheduler`), and Phase 9 already has an unsolved `ctranslate2` bundling
failure without adding cairo and pango to it. The HTML here is self-contained
and styled for paper; Ctrl+P in any browser turns it into a real PDF, and the
same file doubles as something you can send somebody.

Rendering is pure and separate from writing, so the tests read the output
rather than a filesystem.
"""

from __future__ import annotations

import html
from datetime import UTC, datetime

from sidecar.memory.study import MAX_LEVEL, STRONG_AT_OR_ABOVE, WEAK_AT_OR_BELOW, StudyState

#: Five positions read as a scale at a glance where "3" has to be compared
#: against something — the same reasoning `StudyPanel` uses for its dots.
FILLED, EMPTY = "●", "○"


def dots(level: int) -> str:
    return FILLED * level + EMPTY * (MAX_LEVEL - level)


def _standing(level: int) -> str:
    if level == 0:
        return "not started"
    if level <= WEAK_AT_OR_BELOW:
        return "needs revision"
    if level >= STRONG_AT_OR_ABOVE:
        return "solid"
    return "getting there"


def _stamp() -> str:
    return datetime.now(UTC).astimezone().strftime("%d %B %Y")


def to_markdown(state: StudyState) -> str:
    """The map as Markdown. Plain enough to paste anywhere."""
    covered = len(state.covered)
    total = len(state.concepts)
    lines = [
        f"# {state.subject}",
        "",
        # **Says where the map came from.** A roadmap planned from a stated goal
        # is not the same claim as one read out of his own lecture notes, and
        # `source_path` being NULL is exactly what tells them apart.
        f"*{'Planned roadmap' if not state.source_path else 'From ' + state.source_path}*  ",
        f"*{covered} of {total} covered · exported {_stamp()}*",
        "",
    ]

    if state.next_concept is not None:
        lines += [f"**Next up:** {state.next_concept.name}", ""]

    lines += ["## The map", ""]
    for position, concept in enumerate(state.concepts, start=1):
        lines.append(f"### {position}. {concept.name}")
        lines.append("")
        lines.append(f"`{dots(concept.level)}` {_standing(concept.level)}"
                     + (f" · {concept.correct}/{concept.asked} right" if concept.asked else ""))
        if concept.summary:
            lines += ["", concept.summary]
        lines.append("")

    weak = state.weak
    if weak:
        lines += ["## Needs revision", ""]
        lines += [f"- {c.name}" for c in weak]
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


#: Deliberately no web fonts and no external stylesheet: this has to render the
#: same when the file is opened months later on a machine that is offline, and
#: `@media print` is what makes Ctrl+P produce something worth keeping.
_STYLE = """
:root { color-scheme: light; }
* { box-sizing: border-box; }
body {
  margin: 0 auto; padding: 3rem 1.5rem; max-width: 46rem;
  font: 16px/1.6 "Segoe UI", system-ui, -apple-system, sans-serif;
  color: #1b2220; background: #fff;
}
h1 { font-size: 2rem; margin: 0 0 .25rem; }
h2 { font-size: 1.15rem; margin: 2.5rem 0 .75rem; padding-bottom: .3rem;
     border-bottom: 1px solid #dfe5e2; }
h3 { font-size: 1rem; margin: 1.5rem 0 .25rem; }
.meta { color: #6b7a74; font-size: .875rem; margin: 0 0 .25rem; }
.next { display: inline-block; margin: 1rem 0 0; padding: .4rem .75rem;
        border-radius: .5rem; background: #eef2ff; color: #3a4a9f; font-size: .875rem; }
.level { font-family: ui-monospace, Consolas, monospace; letter-spacing: .1em; }
.standing { color: #6b7a74; font-size: .875rem; }
.summary { margin: .35rem 0 0; }
ul { padding-left: 1.25rem; }
li { margin: .2rem 0; }
.weak { color: #8a5a2b; }
@media print {
  body { padding: 0; max-width: none; }
  h2, h3 { break-after: avoid; }
  .concept { break-inside: avoid; }
}
"""


def to_html(state: StudyState) -> str:
    """A self-contained page. Ctrl+P is the PDF export."""
    covered = len(state.covered)
    total = len(state.concepts)
    esc = html.escape
    origin = "Planned roadmap" if not state.source_path else f"From {state.source_path}"

    parts = [
        "<!doctype html>",
        '<html lang="en"><head><meta charset="utf-8">',
        f"<title>{esc(state.subject)}</title>",
        f"<style>{_STYLE}</style>",
        "</head><body>",
        f"<h1>{esc(state.subject)}</h1>",
        f'<p class="meta">{esc(origin)}</p>',
        f'<p class="meta">{covered} of {total} covered · exported {_stamp()}</p>',
    ]
    if state.next_concept is not None:
        parts.append(f'<p class="next">Next up: {esc(state.next_concept.name)}</p>')

    parts.append("<h2>The map</h2>")
    for position, concept in enumerate(state.concepts, start=1):
        scored = f" · {concept.correct}/{concept.asked} right" if concept.asked else ""
        parts.append('<div class="concept">')
        parts.append(f"<h3>{position}. {esc(concept.name)}</h3>")
        parts.append(
            f'<p class="standing"><span class="level">{dots(concept.level)}</span> '
            f"{_standing(concept.level)}{scored}</p>"
        )
        if concept.summary:
            parts.append(f'<p class="summary">{esc(concept.summary)}</p>')
        parts.append("</div>")

    if state.weak:
        parts.append('<h2 class="weak">Needs revision</h2><ul>')
        parts += [f"<li>{esc(c.name)}</li>" for c in state.weak]
        parts.append("</ul>")

    parts.append("</body></html>")
    return "\n".join(parts)


def render(state: StudyState, fmt: str) -> tuple[str, str]:
    """`(text, extension)` for the requested format."""
    if fmt == "html":
        return to_html(state), ".html"
    return to_markdown(state), ".md"


__all__ = ["dots", "render", "to_html", "to_markdown"]
