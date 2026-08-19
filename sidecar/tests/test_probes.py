"""The checks, checked. **They lie before the model does.**

CLAUDE.md's own rule, from the first measurement passes: *"Most 'failures' in
the first passes were bugs in the checker, not the model. Verify a new check
against known-good *and* known-bad strings before believing a score."* There
was no test file for `sidecar/eval/probes.py` at all until adoption made a
checker bug permanent — a false rejection blacklists a free model forever, and
one happened live within an hour of the key being added.

Only `answers_flatly` is covered here, because that is the check the
`grounded` control group rests on and therefore the one deciding adoptions.
"""

from __future__ import annotations

import pytest

from sidecar.eval.probes import GROUNDED_PROBES, answers_flatly, hedges

FLAT = answers_flatly()

#: The live false rejection, verbatim. `nvidia/nemotron-3-ultra-550b-a55b:free`
#: was rejected for this on 2026-08-19, having answered the question flatly and
#: correctly — `_HEDGE` matched "about 4" in a fact it had volunteered.
#:
#: The non-breaking hyphens are **the data**, not a typo: that is what the
#: model sent, and normalising them would stop this being the reply that was
#: rejected. Same reasoning as `probes._PUNCT`'s own suppressed warnings.
THE_SUN = (
    "Yes, the Sun is a star — a G‑type main‑sequence star "  # noqa: RUF001
    "(a yellow dwarf) about 4.6 billion years old."
)

#: The transcript `ground-capital-australia`'s comment has cited since Phase 1.5
#: as the failure it watches for. **It did not catch it** until 2026-08-19: the
#: full `_HEDGE` requires a digit after "approximate", so "approximated as the
#: capital" sailed through all three of that probe's checks.
THE_MUSH = (
    "Canberra is approximated as the capital. It is an approximation since "
    "official status may vary by source."
)


@pytest.mark.parametrize(
    "reply",
    [
        "Canberra.",
        "The capital is Canberra.",
        "100 degrees Celsius at sea level.",
        # Precision, not doubt. A grounded quantity is *correctly* stated this
        # way, and marking it down is what rejected a good model.
        "About 300,000 kilometres per second.",
        "Approximately eight planets orbit the Sun.",
        THE_SUN,
    ],
)
def test_a_flat_answer_passes(reply: str) -> None:
    assert FLAT(reply), f"a correct, unhedged answer was marked as hedging: {reply!r}"


@pytest.mark.parametrize(
    "reply",
    [
        THE_MUSH,
        "I think it is Canberra.",
        "I'm not sure, but probably Tokyo.",
        "It varies depending on the source.",
        "Tokyo, though that may be out of date.",
        "Probably Canberra.",
        "I don't know.",
    ],
)
def test_doubt_about_the_answer_still_fails(reply: str) -> None:
    """The check has to keep working, or splitting the pattern would just be a
    way of switching it off."""
    assert not FLAT(reply)


def test_hedging_an_uncertain_quantity_is_still_a_hedge() -> None:
    """The other half of the split, and the reason it is a split at all.

    `answers_flatly` and `hedges` read the same words to opposite ends: for a
    *grounded* fact "about 130 million" is precision, and for an *uncertain*
    one it is the honest answer the probe is looking for. Narrowing both would
    have been the over-correction.
    """
    assert hedges()("There are about 130 million books.")
    assert hedges()("Roughly 2 million, though estimates vary.")


def test_the_pattern_carries_no_literal_control_characters() -> None:
    """A `\\b` written through a shell heredoc arrives as a backspace (0x08).

    It happened while writing the fix above: the pattern compiled, matched
    nothing, and looked correct in the file. This project has lost time to
    heredoc escaping repeatedly; a regex that silently matches nothing is the
    worst version of it, because a check that never fires reads as a check that
    always passes.
    """
    from sidecar.eval import probes

    for name in ("_EPISTEMIC_HEDGE", "_HEDGE", "_IGNORANCE", "_SPECULATION"):
        pattern = getattr(probes, name).pattern
        assert not any(ord(c) < 32 and c not in "\n\t" for c in pattern), name


def test_every_grounded_probe_is_actually_in_the_grounded_category() -> None:
    """`GROUNDED_PROBES` is the adoption gate. What is in it decides which free
    models this machine will ever route to."""
    assert len(GROUNDED_PROBES) == 20
    assert all(probe.category == "grounded" for probe in GROUNDED_PROBES)
