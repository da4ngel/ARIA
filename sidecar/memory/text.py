"""Word-level matching, shared by retrieval and by episode salience.

**This is the code that carries most real retrievals**, which is not how it was
meant to be. `nomic-embed-text` runs on the CPU (rule 2) and measured 55-107ms
against a 60ms deadline, so 77% of retrievals on 2026-08-12 fell back to word
matching. Treating that path as a token gesture is what made "have we discussed
about any jobs?" answerable only by luck:

- **`jobs` did not match `job`.** There was no stemming at all, so the plural
  the user actually typed missed the singular in every stored summary.
- **`discussed` matched everything.** The summariser opens most episodes with
  it, so it behaved as a stopword that had not been declared one — and the top
  three hits for a question about jobs were "Discussed capitals of countries",
  "Discussed current time in Sri Lanka" and "Discussed various topics", all
  scoring on that one word.
- **A longer question retrieved less.** The score divided by the query's own
  word count, so "did we have any conversation regarding any job kind of
  things?" scored *below* the terser form of the same question. Being specific
  made her worse at remembering.

The answers here are deliberately small and explicit rather than a dependency:
a suffix stemmer with guards, a stopword list that includes the summariser's
own vocabulary, and IDF-weighted coverage so a rare word carries the match and
filler words cannot dilute it.

Lives in its own module because `episodic._salience` needs `content_words` too,
and `retrieval` already imports `episodic` — importing it back would be a cycle.
"""

from __future__ import annotations

import math
import re
from collections import Counter
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterable, Sequence

_WORD = re.compile(r"[a-z0-9']+")

#: Words that match everything and therefore discriminate nothing.
_STOPWORDS = frozenset(
    {
        # ── grammar ──
        "the", "a", "an", "and", "or", "but", "is", "are", "was", "were", "be",
        "been", "am", "do", "does", "did", "have", "has", "had", "i", "me", "my",
        "you", "your", "he", "she", "it", "we", "they", "this", "that", "these",
        "those", "to", "of", "in", "on", "at", "for", "with", "about", "from",
        "what", "when", "where", "who", "how", "why", "can", "could", "would",
        "should", "will", "shall", "may", "might", "please", "just", "some",
        "any", "there", "then", "than", "so", "if", "as", "by", "not", "no",
        "yes", "one", "us", "our", "their", "his", "her", "them", "which",
        # ── the summariser's own vocabulary ──
        # Every one of these was measured opening real episode summaries. They
        # are not stopwords in English; they are stopwords *in this corpus*, and
        # leaving them in is what made "Discussed capitals of countries" the
        # best answer to a question about jobs.
        "discuss", "discussion", "ask", "answer", "reply", "respond", "request",
        "provide", "user", "assistant", "aria", "conversation", "chat", "topic",
        "various", "specific", "regarding", "mention", "say", "tell", "talk",
        "thing", "stuff", "kind", "sort", "want", "need", "get", "got", "make",
        "like", "know", "think", "go", "come", "take", "give", "use", "help",
    }
)

#: Shorter than this and a stem is noise rather than a word.
_MIN_STEM = 3
#: `pressed` must not become `pres`. Porter's guard: these letters double
#: legitimately at the end of a stem, so undoubling them corrupts the word.
_NEVER_UNDOUBLE = frozenset("slzf")


def stem(word: str) -> str:
    """Strip a plural or tense suffix. Crude on purpose, and guarded.

    Not a linguistic stemmer and not trying to be — it exists so `jobs` finds
    `job`, `discussed` finds `discuss` and `working` finds `work`. Every rule
    refuses to produce a stem under three characters, so a short word is
    returned untouched rather than mangled into a different one.
    """
    if len(word) <= _MIN_STEM:
        return word

    if word.endswith("ies") and len(word) > 4:
        return word[:-3] + "y"
    if word.endswith("ing") and len(word) - 3 >= _MIN_STEM:
        return _undouble(word[:-3])
    if word.endswith("ed") and len(word) - 2 >= _MIN_STEM:
        return _undouble(word[:-2])
    if word.endswith("ly") and len(word) - 2 >= _MIN_STEM:
        return word[:-2]
    if word.endswith("es") and len(word) - 2 >= _MIN_STEM:
        return word[:-2]
    # `class`, `bus`, `this` — a trailing s after s/u/i is part of the word,
    # not a plural.
    if word.endswith("s") and word[-2] not in "sui" and len(word) - 1 >= _MIN_STEM:
        return word[:-1]
    return word


def _undouble(stemmed: str) -> str:
    """`runn` -> `run`, but `press` stays `press`."""
    if (
        len(stemmed) > _MIN_STEM
        and stemmed[-1] == stemmed[-2]
        and stemmed[-1] not in _NEVER_UNDOUBLE
    ):
        return stemmed[:-1]
    return stemmed


def content_words(text: str) -> set[str]:
    """The words in `text` worth matching on, stemmed."""
    words = set()
    for raw in _WORD.findall(text.lower()):
        if len(raw) < 2 or raw in _STOPWORDS:
            continue
        rooted = stem(raw)
        if len(rooted) < 2 or rooted in _STOPWORDS:
            continue
        words.add(rooted)
    return words


def idf(documents: Sequence[set[str]]) -> dict[str, float]:
    """How rare each word is across the candidate set.

    Computed over the rows actually being ranked rather than the whole database:
    the scan is bounded, the corpus is small, and a word's usefulness here is
    exactly how well it separates *these* candidates from each other.
    """
    if not documents:
        return {}
    total = len(documents)
    seen: Counter[str] = Counter()
    for doc in documents:
        seen.update(doc)
    return {word: math.log(1.0 + total / count) for word, count in seen.items()}


def coverage(query: Iterable[str], document: set[str], weights: dict[str, float]) -> float:
    """How much of the query's meaning this document accounts for, 0..1.

    IDF-weighted, which is the part that matters. Plain overlap divided by the
    query length punished a specific question for being specific — "did we have
    any conversation regarding any job kind of things?" scored below "any jobs?"
    for the same episode. Weighting by rarity means the one word that carries
    the question carries the match, and the filler around it costs nothing.

    A word absent from `weights` — it appeared in the query but in none of the
    candidates — is given the maximum weight in the denominator. It is the most
    discriminating word there is, and failing to find it is real evidence
    against the match rather than something to shrug off.
    """
    query_words = set(query)
    if not query_words or not document:
        return 0.0

    default = max(weights.values(), default=1.0)
    total = 0.0
    matched = 0.0
    for word in query_words:
        weight = weights.get(word, default)
        total += weight
        if word in document:
            matched += weight
    return matched / total if total else 0.0
