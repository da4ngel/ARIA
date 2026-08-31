"""Exporting a knowledge map.

Rendering is pure, so these read the output rather than a filesystem. The one
thing worth pinning beyond shape is provenance: a roadmap planned from a stated
goal is a different claim from a map read out of somebody's own lecture notes,
and `source_path` being NULL is the only thing that tells them apart.
"""

from __future__ import annotations

from sidecar.memory.study import Concept, StudyState
from sidecar.memory.study_export import dots, render, to_html, to_markdown


def _state(*, source: str | None = "lecture.pptx") -> StudyState:
    return StudyState(
        subject_id=1,
        subject="Information Security",
        source_path=source,
        concepts=(
            Concept(id=1, name="CIA Triad", summary="Confidentiality, integrity, availability.",
                    position=0, level=5, asked=6, correct=6),
            Concept(id=2, name="Access Control", summary="Who may do what.",
                    position=1, level=2, asked=4, correct=1),
            Concept(id=3, name="Replay Attacks", summary="", position=2, level=0,
                    asked=0, correct=0),
        ),
    )


def test_the_dots_are_a_five_position_scale() -> None:
    assert dots(0) == "○○○○○"
    assert dots(3) == "●●●○○"
    assert dots(5) == "●●●●●"


# ── Markdown ──────────────────────────────────────────────────────────


def test_markdown_carries_every_concept_in_order() -> None:
    out = to_markdown(_state())
    assert "# Information Security" in out
    # Inside the map, not the whole document — "Next up" names a concept
    # before the map begins, so a search from the top finds it out of order.
    body = out[out.index("## The map") :]
    assert body.index("CIA Triad") < body.index("Access Control") < body.index("Replay Attacks")


def test_markdown_names_where_the_map_came_from() -> None:
    assert "From lecture.pptx" in to_markdown(_state())


def test_a_planned_roadmap_says_it_was_planned() -> None:
    """**Provenance, not decoration.** A roadmap presented as though it came
    from his own notes is exactly the quiet claim every anti-invention clause
    in `context.py` exists to stop."""
    assert "Planned roadmap" in to_markdown(_state(source=None))


def test_markdown_lists_what_needs_revision() -> None:
    out = to_markdown(_state())
    assert "## Needs revision" in out
    assert "- Access Control" in out
    # Solid and untouched concepts are not "needing revision".
    assert out.count("- CIA Triad") == 0


def test_a_score_is_shown_only_where_something_was_asked() -> None:
    out = to_markdown(_state())
    assert "1/4 right" in out
    # Nothing has been asked about Replay Attacks, so there is no 0/0.
    assert "0/0" not in out


def test_the_next_concept_is_called_out() -> None:
    assert "**Next up:** Access Control" in to_markdown(_state())


# ── HTML ──────────────────────────────────────────────────────────────


def test_the_page_is_self_contained() -> None:
    """It has to render the same months later on a machine that is offline, so
    no web font and no external stylesheet."""
    out = to_html(_state())
    assert "<style>" in out
    assert "http://" not in out
    assert "https://" not in out
    assert "<link" not in out


def test_the_page_has_print_rules_because_that_is_the_pdf_export() -> None:
    assert "@media print" in to_html(_state())


def test_a_subject_name_cannot_inject_markup() -> None:
    """A subject name is free text that came from a model reading a lecture."""
    hostile = StudyState(
        subject_id=1,
        subject="<script>alert(1)</script>",
        source_path=None,
        concepts=(Concept(id=1, name="<b>x</b>", summary="", position=0, level=1,
                          asked=0, correct=0),),
    )
    out = to_html(hostile)
    assert "<script>" not in out
    assert "&lt;script&gt;" in out
    assert "<b>x</b>" not in out


# ── the chooser ───────────────────────────────────────────────────────


def test_the_format_decides_the_extension() -> None:
    assert render(_state(), "md")[1] == ".md"
    assert render(_state(), "html")[1] == ".html"


def test_an_unknown_format_falls_back_to_markdown() -> None:
    """Rather than refusing: a file he can read beats an error."""
    assert render(_state(), "sideways")[1] == ".md"
