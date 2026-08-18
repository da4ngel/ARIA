"""Vector arithmetic for the memory tables (Phase 5).

**Why this exists next to `indexer._pack`, which looks identical.**

Both pack a float list into the raw little-endian float32 sqlite-vec wants. The
difference is what goes in. The `vec0` tables in `schema.sql` are declared
`float[768]` with no `distance_metric`, so sqlite-vec returns **L2**. That is
fine for the indexer, which only ever *ranks* chunks — the order of L2
distances over unnormalised vectors is good enough to answer "which chunk is
most like this query".

Phase 5 needs a real number, not an order. §8.3's merge rule is "same subject
and predicate, different object, **cosine > 0.85** → supersede", and 0.85 is
meaningless against an unnormalised L2 distance. So `episode_vec` and
`fact_vec` store **unit vectors**, and for unit vectors

    ‖a - b‖² = ‖a‖² + ‖b‖² - 2·(a·b) = 2 - 2·cos(a, b)

which inverts exactly:

    cos = 1 - d²/2

No approximation, no calibration constant.

`file_vec` is deliberately left alone. It already holds unnormalised vectors
written by `indexer._pack`, and normalising new rows into the same table would
mix two scales in one index and quietly degrade `search_content` — rule 10, and
a bug nobody would notice for weeks. **Do not "de-duplicate" these two packers.**
"""

from __future__ import annotations

import math
import struct

__all__ = ["cosine", "cosine_from_l2", "normalise", "pack"]


def normalise(vector: list[float]) -> list[float]:
    """Scale to unit length, so L2 distance carries cosine exactly.

    A zero vector has no direction to preserve, so it is returned unchanged
    rather than dividing by zero. It will score 0.0 against everything, which
    is the honest answer.
    """
    length = math.sqrt(sum(v * v for v in vector))
    if length == 0.0:
        return list(vector)
    return [v / length for v in vector]


def pack(vector: list[float]) -> bytes:
    """Raw little-endian float32, which is sqlite-vec's wire format."""
    return struct.pack(f"<{len(vector)}f", *vector)


def cosine_from_l2(distance: float) -> float:
    """Recover cosine from the L2 distance between two *unit* vectors.

    Only valid for vectors that went through `normalise` on the way in. The
    clamp absorbs float32 round-trip error, which can push an identical pair a
    hair past 1.0.
    """
    cos = 1.0 - (distance * distance) / 2.0
    return max(-1.0, min(1.0, cos))


def cosine(a: list[float], b: list[float]) -> float:
    """Cosine similarity of two vectors, normalised or not.

    Used by the merge step, which compares a freshly embedded fact against
    vectors it already holds in memory rather than through the database.
    """
    dot = sum(x * y for x, y in zip(a, b, strict=True))
    length = math.sqrt(sum(x * x for x in a)) * math.sqrt(sum(y * y for y in b))
    if length == 0.0:
        return 0.0
    return max(-1.0, min(1.0, dot / length))
