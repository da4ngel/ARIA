"""How a study session is being run right now, as opposed to what it is about.

Eyaas asked for Study Mode as a console rather than a viewer — Learn, Practice,
Revision, Rapid review, Exam and Teach-back as things you pick. A sub-mode is
the *shape of this session*: `ConversationMode.STUDY` says she is teaching, and
this says whether she is introducing something new, drilling what failed, or
sitting silently while he explains it back.

**Volatile, not stable, and that is the load-bearing decision.**
`ConversationMode` lives in the stable prefix and is resolved at import into 36
strings — two persona levels by three capability variants by six modes. Nesting
a second axis under it makes 216, and Study's stable block already sits at 798
of the 800-token local budget with no room for anything. A sub-mode also changes
several times within one session, which is precisely what the volatile section
is for. The cost is ~40 tokens on a block that only exists in Study mode, ≈19ms
a turn at the measured 480ms/1000.

**Every field here is read by something**, the rule `modes.py` states in its own
docstring: `line` by the prompt block, `asks` by the prompt block, `over` by the
concept filter, `reveal_answers` by `study_check`. A field nothing consumes is
not a policy — it is the `affect_state` / `procedures` / `record_new_offers`
pattern this codebase keeps rediscovering.

**And a sub-mode changes style and emphasis, never permission.** It reaches the
prompt and one tool's reporting. No tier moves, no confirmation is skipped,
nothing about `ModePolicy`'s own ceiling is touched.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class StudySubMode(StrEnum):
    """The six. `LEARN` is the default and behaves exactly as Study did before
    sub-modes existed — nothing changes for anyone who never opens the panel."""

    LEARN = "learn"
    PRACTICE = "practice"
    REVISION = "revision"
    RAPID = "rapid"
    EXAM = "exam"
    TEACH_BACK = "teach_back"


class Scope(StrEnum):
    """Which concepts a sub-mode works over.

    Read by `study.render` to pick what the prompt block puts in front of her,
    so the sub-mode and the concepts named always agree — a Revision session
    listing a concept he has already mastered is the two disagreeing.
    """

    #: The next thing he has not met, which is `StudyState.next_concept`.
    NEXT = "next"
    #: Anything with a level above 0 — he has seen it, so it can be tested.
    COVERED = "covered"
    #: Weak or recently wrong. "Due", as Eyaas defined it: derived from what is
    #: already stored rather than from a review schedule that does not exist.
    WEAK = "weak"


@dataclass(frozen=True)
class SubModePolicy:
    """One way of running a study session."""

    sub_mode: StudySubMode
    label: str

    #: What goes in the volatile study block. One or two sentences — this is
    #: paid every turn of a study session, unlike `_MODE_TEXT`'s block.
    line: str

    #: How many questions a turn of this sub-mode should ask. Named in the
    #: prompt rather than enforced: `study_check` caps at 4 and the model
    #: decides within that, the same way `ask_user` is guided by its
    #: description rather than by a counter.
    asks: int

    scope: Scope

    #: Whether `study_check` may report which answer was right.
    #:
    #: **Exam's one mechanical lever.** A tool result is an instruction to a
    #: model, so handing it "the answer was X" mid-exam is how the answer
    #: reaches his screen before the exam is over. Everything else about a
    #: sub-mode is prompt text a model may or may not follow; this cannot be,
    #: because the information simply must not be in the room.
    reveal_answers: bool = True

    #: The message the panel sends when this button is pressed. It lands in the
    #: transcript as his, because pressing the button *is* asking.
    opener: str = ""


POLICIES: dict[StudySubMode, SubModePolicy] = {
    StudySubMode.LEARN: SubModePolicy(
        sub_mode=StudySubMode.LEARN,
        label="Learn",
        # Empty on purpose. Learn is the default, and an empty line means the
        # study block is byte-for-byte what it was before sub-modes shipped —
        # the same guarantee NORMAL keeps for `ConversationMode`.
        line="",
        asks=1,
        scope=Scope.NEXT,
        opener="Teach me the next thing.",
    ),
    StudySubMode.PRACTICE: SubModePolicy(
        sub_mode=StudySubMode.PRACTICE,
        label="Practice",
        line=(
            "Practice: do not teach anything new. Ask about what he has already "
            "covered, tell him straight away how each answer went, and keep "
            "going. Vary how hard they are."
        ),
        asks=3,
        scope=Scope.COVERED,
        opener="Practise what I have covered so far.",
    ),
    StudySubMode.REVISION: SubModePolicy(
        sub_mode=StudySubMode.REVISION,
        label="Revision",
        line=(
            "Revision: work only on what is shaky below. Re-explain the part "
            "that failed rather than the whole idea, then ask again. Do not "
            "move on to anything new."
        ),
        asks=3,
        scope=Scope.WEAK,
        opener="Go over the things I keep getting wrong.",
    ),
    StudySubMode.RAPID: SubModePolicy(
        sub_mode=StudySubMode.RAPID,
        label="Rapid review",
        line=(
            "Rapid review: one line on each concept he has covered, in order, "
            "no questions and no detail. This is a skim before an exam, not a "
            "lesson."
        ),
        asks=0,
        scope=Scope.COVERED,
        opener="Give me a rapid review of everything.",
    ),
    StudySubMode.EXAM: SubModePolicy(
        sub_mode=StudySubMode.EXAM,
        label="Exam",
        line=(
            "Exam: ask four questions in one go and say nothing about how he "
            "did until every answer is in. Do not teach, do not hint, do not "
            "react between questions. Then give him the score and what to "
            "review."
        ),
        asks=4,
        scope=Scope.COVERED,
        reveal_answers=False,
        opener="Test me. Exam conditions.",
    ),
    StudySubMode.TEACH_BACK: SubModePolicy(
        sub_mode=StudySubMode.TEACH_BACK,
        label="Teach-back",
        line=(
            "Teach-back: he explains, you listen. Name one concept and ask him "
            "to explain it as if to someone who has never met it. Then say what "
            "was missing or wrong in his explanation — not your own version of "
            "it."
        ),
        asks=1,
        scope=Scope.COVERED,
        opener="Let me explain something back to you.",
    ),
}


def policy_for(sub_mode: StudySubMode | None) -> SubModePolicy:
    """Never raises, and `None` means Learn — `modes.policy_for`'s contract."""
    if sub_mode is None:
        return POLICIES[StudySubMode.LEARN]
    return POLICIES.get(sub_mode, POLICIES[StudySubMode.LEARN])


def parse(raw: str | None) -> StudySubMode | None:
    """A sub-mode name off the wire, or `None` for anything unrecognised.

    Lenient rather than strict: the caller is a panel button, and an unknown
    string should land on Learn rather than fail a click.
    """
    if not raw:
        return None
    try:
        return StudySubMode(raw)
    except ValueError:
        return None
