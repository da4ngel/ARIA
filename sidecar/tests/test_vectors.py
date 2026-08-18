"""Vector arithmetic for the memory tables.

Small, but the 0.85 supersession threshold in §8.3 rests entirely on
`cosine_from_l2` being exact rather than approximately right — a drift here
would silently stop contradictions being detected.
"""

from __future__ import annotations

import math

import pytest

from sidecar.memory import vectors


def test_normalise_produces_unit_length() -> None:
    unit = vectors.normalise([3.0, 4.0])
    assert math.isclose(math.sqrt(sum(v * v for v in unit)), 1.0, rel_tol=1e-9)
    assert math.isclose(unit[0], 0.6, rel_tol=1e-9)


def test_normalise_survives_a_zero_vector() -> None:
    """A zero vector has no direction; dividing by its length would raise."""
    assert vectors.normalise([0.0, 0.0, 0.0]) == [0.0, 0.0, 0.0]


def test_pack_is_little_endian_float32() -> None:
    packed = vectors.pack([1.0, 2.0])
    assert len(packed) == 8
    assert packed[:4] == b"\x00\x00\x80\x3f"


@pytest.mark.parametrize(
    ("a", "b", "expected"),
    [
        ([1.0, 0.0], [1.0, 0.0], 1.0),
        ([1.0, 0.0], [0.0, 1.0], 0.0),
        ([1.0, 0.0], [-1.0, 0.0], -1.0),
    ],
)
def test_cosine_from_l2_inverts_exactly(a: list[float], b: list[float], expected: float) -> None:
    """For unit vectors ‖a-b‖² = 2 - 2cos, so the inversion is not an estimate."""
    distance = math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b, strict=True)))
    assert math.isclose(vectors.cosine_from_l2(distance), expected, abs_tol=1e-9)


def test_cosine_from_l2_clamps_float_error() -> None:
    """A float32 round-trip can push an identical pair a hair past 1.0."""
    assert vectors.cosine_from_l2(-0.0001) <= 1.0
    assert vectors.cosine_from_l2(99.0) >= -1.0


def test_cosine_matches_the_l2_route() -> None:
    """The merge step and the search path must agree, or 0.85 means two things."""
    a = vectors.normalise([0.3, 0.9, 0.1])
    b = vectors.normalise([0.4, 0.8, 0.2])
    distance = math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b, strict=True)))
    assert math.isclose(vectors.cosine(a, b), vectors.cosine_from_l2(distance), abs_tol=1e-9)


def test_cosine_is_scale_invariant() -> None:
    """It is used on raw model output, which is not normalised."""
    assert math.isclose(vectors.cosine([1.0, 2.0], [2.0, 4.0]), 1.0, rel_tol=1e-9)


def test_cosine_of_a_zero_vector_is_zero() -> None:
    assert vectors.cosine([0.0, 0.0], [1.0, 1.0]) == 0.0
