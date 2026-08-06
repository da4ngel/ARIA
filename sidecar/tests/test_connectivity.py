"""Cached reachability. The point is that reads never touch the network."""

from __future__ import annotations

import httpx
import pytest

from sidecar.providers.connectivity import Connectivity


class _FakeResponse:
    def __init__(self, status_code: int) -> None:
        self.status_code = status_code


def _client_returning(status: int) -> type:
    class Client:
        def __init__(self, *_args: object, **_kwargs: object) -> None: ...
        async def __aenter__(self) -> Client:
            return self
        async def __aexit__(self, *_exc: object) -> None: ...
        async def get(self, _url: str) -> _FakeResponse:
            return _FakeResponse(status)

    return Client


def _client_raising(exc: Exception) -> type:
    class Client:
        def __init__(self, *_args: object, **_kwargs: object) -> None: ...
        async def __aenter__(self) -> Client:
            return self
        async def __aexit__(self, *_exc: object) -> None: ...
        async def get(self, _url: str) -> _FakeResponse:
            raise exc

    return Client


def test_assumes_online_before_the_first_probe() -> None:
    """A turn landing before the first probe must not claim the user is offline
    on a guess. Optimistic is the safer default."""
    assert Connectivity().online is True


def test_reading_never_probes(monkeypatch: pytest.MonkeyPatch) -> None:
    """The property is on the latency path; a network call here would put a
    round-trip in front of every turn, which is what §9.7 forbids."""

    def explode(*_args: object, **_kwargs: object) -> None:
        raise AssertionError("reading `online` must not touch the network")

    monkeypatch.setattr(httpx, "AsyncClient", explode)
    assert Connectivity().online in (True, False)


async def test_a_good_response_reports_online(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(httpx, "AsyncClient", _client_returning(204))
    assert await Connectivity().probe_once() is True


async def test_a_server_error_reports_offline(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(httpx, "AsyncClient", _client_returning(503))
    assert await Connectivity().probe_once() is False


async def test_a_failed_request_reports_offline_rather_than_raising(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """No route to the host is the ordinary case this exists to detect."""
    monkeypatch.setattr(httpx, "AsyncClient", _client_raising(httpx.ConnectError("no route")))
    probe = Connectivity()
    assert await probe.probe_once() is False
    assert probe.online is False


async def test_recovers_when_the_network_comes_back(monkeypatch: pytest.MonkeyPatch) -> None:
    probe = Connectivity()
    monkeypatch.setattr(httpx, "AsyncClient", _client_raising(httpx.ConnectError("down")))
    await probe.probe_once()
    assert probe.online is False

    monkeypatch.setattr(httpx, "AsyncClient", _client_returning(204))
    await probe.probe_once()
    assert probe.online is True


async def test_stop_is_safe_when_never_started() -> None:
    await Connectivity().stop()


async def test_start_is_idempotent(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(httpx, "AsyncClient", _client_returning(204))
    probe = Connectivity(interval_s=0.01)
    try:
        probe.start()
        probe.start()
    finally:
        await probe.stop()
