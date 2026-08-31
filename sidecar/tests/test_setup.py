"""First run: the pull parser, the download, and the two things it must not do.

The wizard's own steps are mostly a report. What is worth testing is the two
paths that *write to disk over a network*, because both fail in ways that are
silent and both leave the machine worse than they found it:

  - Ollama reports a failed pull **in band**, with HTTP 200 and an `error`
    key, so a reader that only watches `status` calls a missing model a
    success and the wizard advances past a step that did nothing.
  - A 310MB download interrupted three quarters of the way through would,
    written directly to its final name, leave a file at exactly the path
    `tts.py` checks for. Speech would then fail on every launch afterwards
    with an ONNX parse error instead of the honest "the weights are missing".
"""

from __future__ import annotations

import json
from collections.abc import AsyncIterator
from pathlib import Path

import httpx
import pytest

from sidecar.core import setup
from sidecar.providers.base import ProviderUnavailable
from sidecar.providers.ollama import OllamaProvider, _parse_pull_line

# ── the pull stream ──────────────────────────────────────────────────


def test_a_layer_line_carries_a_percentage() -> None:
    progress = _parse_pull_line(
        json.dumps({"status": "pulling 2af3b81862c6", "completed": 250, "total": 1000})
    )
    assert progress is not None
    assert progress.percent == 25.0
    assert not progress.done


def test_a_status_only_line_has_no_percentage_rather_than_zero() -> None:
    """`"pulling manifest"` carries no totals, and neither does verification.

    A consumer that read a missing total as zero would slam the bar back to
    the start between every layer.
    """
    progress = _parse_pull_line(json.dumps({"status": "verifying sha256 digest"}))
    assert progress is not None
    assert progress.percent is None
    assert progress.total is None


def test_success_is_the_done_line() -> None:
    progress = _parse_pull_line(json.dumps({"status": "success"}))
    assert progress is not None and progress.done


def test_a_blank_or_unparseable_line_is_skipped_not_fatal() -> None:
    assert _parse_pull_line("") is None
    assert _parse_pull_line("   ") is None
    assert _parse_pull_line("not json at all") is None
    assert _parse_pull_line(json.dumps([1, 2, 3])) is None


def test_an_error_reported_with_a_200_is_raised_rather_than_ignored() -> None:
    """**The one that matters.** `ollama pull nope:latest` answers 200.

    Watching only `status` would report a model nobody has as pulled, and the
    wizard would advance past a step that achieved nothing.
    """
    with pytest.raises(ProviderUnavailable, match="not found"):
        _parse_pull_line(json.dumps({"error": "model 'nope:latest' not found"}))


async def test_pull_yields_every_line_in_order() -> None:
    body = "\n".join(
        [
            json.dumps({"status": "pulling manifest"}),
            json.dumps({"status": "pulling ab12", "completed": 512, "total": 1024}),
            json.dumps({"status": "pulling ab12", "completed": 1024, "total": 1024}),
            json.dumps({"status": "success"}),
        ]
    )
    provider = OllamaProvider()
    provider._client = httpx.AsyncClient(  # noqa: SLF001
        base_url="http://ollama.test",
        transport=httpx.MockTransport(lambda _: httpx.Response(200, text=body)),
    )
    seen = [p async for p in provider.pull("qwen2.5:7b")]
    await provider.aclose()

    assert [p.status for p in seen] == [
        "pulling manifest",
        "pulling ab12",
        "pulling ab12",
        "success",
    ]
    assert [p.percent for p in seen] == [None, 50.0, 100.0, None]
    assert seen[-1].done


# ── the download ─────────────────────────────────────────────────────


async def test_a_download_lands_and_reports_a_total(tmp_path: Path) -> None:
    payload = b"x" * 4096
    client = httpx.AsyncClient(
        transport=httpx.MockTransport(
            lambda _: httpx.Response(200, content=payload, headers={"content-length": "4096"})
        )
    )
    target = tmp_path / "weights.onnx"
    seen = [p async for p in setup._download(client, "http://x/w", target, "weights.onnx")]  # noqa: SLF001
    await client.aclose()

    assert target.read_bytes() == payload
    assert seen[0].total == 4096
    assert seen[-1].done and seen[-1].percent == 100.0


async def test_an_interrupted_download_leaves_no_file_at_the_real_path(
    tmp_path: Path,
) -> None:
    """The whole reason for the `.part`.

    `tts.py` decides speech is available by `Path.exists()`. A truncated file
    at that path turns "the weights are missing", which says what to do, into
    an ONNX parse error on every launch, which does not.
    """

    # Half a file, then the connection drops - the realistic failure, and the
    # one a status-code check would never reach.
    async def body() -> AsyncIterator[bytes]:
        yield b"y" * 2048
        raise httpx.ReadError("connection reset")

    def half_then_drop(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, headers={"content-length": "4096"}, content=body())

    client = httpx.AsyncClient(transport=httpx.MockTransport(half_then_drop))
    target = tmp_path / "kokoro-v1.0.onnx"
    with pytest.raises(httpx.ReadError):
        async for _ in setup._download(client, "http://x/w", target, "kokoro"):  # noqa: SLF001
            pass
    await client.aclose()

    assert not target.exists()
    # The partial *is* left behind, deliberately: it is evidence for anyone
    # looking at the folder, and it is at a name nothing loads.
    assert (tmp_path / "kokoro-v1.0.onnx.part").exists()


async def test_an_already_present_weight_is_not_downloaded_again(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Opening the wizard twice must not cost 310MB twice."""
    for name, _url, _size in setup.KOKORO_FILES:
        (tmp_path / name).write_bytes(b"already here")

    class _Settings:
        models_dir = tmp_path

    monkeypatch.setattr("sidecar.config.get_settings", lambda: _Settings())

    def refuse(*_a: object, **_k: object) -> None:
        raise AssertionError("a present weight was fetched again")

    monkeypatch.setattr(setup, "_download", refuse)

    seen = [p async for p in setup.fetch_voice()]
    assert len(seen) == len(setup.KOKORO_FILES)
    assert all(p.done and p.note == "already present" for p in seen)


# ── the report ───────────────────────────────────────────────────────


async def test_the_state_report_never_leaks_a_key_hint(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Same rule as the diagnostics export, for the same reason.

    `hint` is the last four characters of a real key, and this payload
    crosses a process boundary into a renderer.
    """
    from sidecar.providers.credentials import CredentialKey, CredentialStatus

    monkeypatch.setattr(
        "sidecar.providers.credentials.all_status",
        lambda: [CredentialStatus(key=CredentialKey.OPENAI, present=True, hint="Zk9Q")],
    )
    report = await setup.state()
    assert json.dumps(report).find("Zk9Q") == -1
    assert report["keys"] == [{"key": "openai_api_key", "present": True}]


async def test_it_reports_what_is_missing_rather_than_failing(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """A wizard whose job is to report absence cannot fail because of it."""

    class _Settings:
        models_dir = tmp_path

    monkeypatch.setattr("sidecar.config.get_settings", lambda: _Settings())
    report = await setup.state()

    assert report["voice"]["present"] is False
    assert "kokoro-v1.0.onnx" in report["voice"]["missing"]
    assert report["wake_word"]["present"] is False
    assert report["voice"]["approx_bytes"] > 0
