"""Web search, and turning a page into something a model can read.

BUILD_SPEC §9 Phase 7 reaches the web through Playwright over a real Chrome.
This is the narrower half of that phase — §7's `research(query)` composite —
built over `httpx` instead, on Eyaas's call:

- **Playwright ships browser binaries**, several hundred megabytes of them,
  against §2.3's packaging constraint and the same instinct that keeps `torch`
  out (rule 3). The one dependency this file needs is already here.
- **Live data does not need a browser.** "What is the RTX 5090 going for" needs
  a search index and three pages of text. Driving a logged-in Gmail does, and
  that is the part of Phase 7 still unbuilt — see CLAUDE.md.

**Two providers rather than a choice**, because neither is obviously right and
whichever key the user has is the one that matters:

- **Tavily** is built for this and returns extracted page text in the search
  response, so a whole class of parsing failure never happens.
- **Brave** is a real independent index with a generous free tier and returns
  descriptions only, so pages have to be fetched and stripped here.

Whichever key is present is used; both present prefers Tavily, for the reason
above. Neither present is not an error — it is the state the app ships in, and
`research` says so with the fix in it.
"""

from __future__ import annotations

import asyncio
import re
from dataclasses import dataclass
from html import unescape
from html.parser import HTMLParser
from typing import Any

import httpx
import structlog

from sidecar.providers.credentials import CredentialKey, get_key

log = structlog.get_logger(__name__)

BRAVE_URL = "https://api.search.brave.com/res/v1/web/search"
TAVILY_URL = "https://api.tavily.com/search"

#: A search that has not answered in this long is not going to help a
#: conversation. §10's budget is ~1000ms for voice; this is a tool call the
#: user is explicitly waiting on, so it may cost more — but not unboundedly.
SEARCH_TIMEOUT_S = 12.0
FETCH_TIMEOUT_S = 8.0
#: Pages opened per query. §7: "search → open top 3 → extract → synthesize".
DEFAULT_SOURCES = 3
#: Per page, after stripping. Enough for a model to answer from, small enough
#: that three of them do not blow the context budget §8.2 is guarding.
EXTRACT_MAX_CHARS = 4000
#: Anything past this is a download, not an article.
FETCH_MAX_BYTES = 2_000_000

#: Sent on fetches. A blank or scripted-looking agent is refused by a
#: meaningful share of sites, which reads as "research never works".
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36 ARIA/0.1"
)


class SearchUnavailable(RuntimeError):
    """No usable search key, or the provider refused. Carries the fix."""


@dataclass(frozen=True)
class Source:
    """One result, and whatever text could be got out of it."""

    title: str
    url: str
    snippet: str
    text: str = ""

    @property
    def body(self) -> str:
        """The best text available, preferring the fetched page."""
        return self.text or self.snippet


# ── turning HTML into text, without a dependency ──────────────────────


class _Reader(HTMLParser):
    """Strip a page to its readable text.

    Not readability, not an article extractor, and not trying to be: it drops
    `script`/`style`/`nav`/`footer`, keeps the text, and collapses whitespace.
    A proper extractor is `trafilatura` or `beautifulsoup4`, and neither is
    worth a dependency for a model that is about to summarise the result
    anyway — the failure mode here is a bit of navigation text in the middle,
    which a model handles and a packaging step does not.
    """

    _SKIP = frozenset({"script", "style", "nav", "footer", "header", "form", "svg"})
    _BREAK = frozenset({"p", "div", "br", "li", "tr", "h1", "h2", "h3", "h4", "section"})

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._parts: list[str] = []
        self._depth = 0

    def handle_starttag(self, tag: str, attrs: object) -> None:
        if tag in self._SKIP:
            self._depth += 1
        elif tag in self._BREAK:
            self._parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if tag in self._SKIP and self._depth:
            self._depth -= 1

    def handle_data(self, data: str) -> None:
        if self._depth == 0 and data.strip():
            self._parts.append(data)

    def text(self) -> str:
        joined = "".join(self._parts)
        # Collapse runs of blank lines and of spaces, separately: paragraph
        # breaks are worth keeping, a hundred of them are not.
        #
        # The class is spelled as "whitespace that is not a newline" rather
        # than listed out, because pages are full of non-breaking spaces and a
        # literal one inside brackets is invisible in a diff.
        joined = re.sub(r"[^\S\n]+", " ", joined)
        joined = re.sub(r"\n\s*\n\s*", "\n\n", joined)
        return joined.strip()


def to_text(html: str, limit: int = EXTRACT_MAX_CHARS) -> str:
    """Readable text from a page, truncated on a word boundary."""
    reader = _Reader()
    try:
        reader.feed(html)
        reader.close()
    except Exception:  # noqa: BLE001 — malformed HTML is the normal case
        return unescape(re.sub(r"<[^>]+>", " ", html))[:limit]
    text = reader.text()
    if len(text) <= limit:
        return text
    return text[:limit].rsplit(" ", 1)[0] + "…"


# ── the providers ─────────────────────────────────────────────────────


def available() -> str | None:
    """Which search backend can run, or None. Never raises, never blocks."""
    if get_key(CredentialKey.TAVILY):
        return "tavily"
    if get_key(CredentialKey.BRAVE):
        return "brave"
    return None


class WebSearch:
    """Search, then read the results. One client, closed on shutdown."""

    def __init__(self, client: httpx.AsyncClient | None = None) -> None:
        self._client = client or httpx.AsyncClient(
            timeout=httpx.Timeout(SEARCH_TIMEOUT_S, connect=5.0),
            follow_redirects=True,
            headers={"User-Agent": USER_AGENT},
        )

    async def aclose(self) -> None:
        await self._client.aclose()

    async def search(self, query: str, limit: int = DEFAULT_SOURCES) -> list[Source]:
        """Top results for `query`. Raises `SearchUnavailable` with the fix."""
        backend = available()
        if backend == "tavily":
            return await self._tavily(query, limit)
        if backend == "brave":
            return await self._brave(query, limit)
        raise SearchUnavailable(
            "No web search key is set. Add a free Tavily key "
            "(tavily.com) or Brave Search key (brave.com/search/api) in Settings."
        )

    async def _tavily(self, query: str, limit: int) -> list[Source]:
        key = get_key(CredentialKey.TAVILY) or ""
        payload = {
            "api_key": key,
            "query": query,
            "max_results": limit,
            # Tavily extracts the page itself, which is the whole reason to
            # prefer it: no fetch, no parse, no site blocking a bare client.
            "include_raw_content": True,
            "search_depth": "basic",
        }
        data = await self._post_json(TAVILY_URL, payload, "Tavily")
        results = data.get("results") or []
        return [
            Source(
                title=str(r.get("title") or r.get("url") or "").strip(),
                url=str(r.get("url") or "").strip(),
                snippet=str(r.get("content") or "").strip(),
                text=to_text(str(r.get("raw_content") or ""))
                if r.get("raw_content")
                else "",
            )
            for r in results[:limit]
            if r.get("url")
        ]

    async def _brave(self, query: str, limit: int) -> list[Source]:
        key = get_key(CredentialKey.BRAVE) or ""
        try:
            response = await self._client.get(
                BRAVE_URL,
                params={"q": query, "count": limit},
                headers={"X-Subscription-Token": key, "Accept": "application/json"},
            )
        except httpx.HTTPError as exc:
            raise SearchUnavailable(f"Brave Search could not be reached: {exc}") from exc
        self._check(response, "Brave Search")

        web = (response.json().get("web") or {}).get("results") or []
        return [
            Source(
                title=str(r.get("title") or "").strip(),
                url=str(r.get("url") or "").strip(),
                snippet=to_text(str(r.get("description") or ""), limit=400),
            )
            for r in web[:limit]
            if r.get("url")
        ]

    async def _post_json(
        self, url: str, payload: dict[str, Any], label: str
    ) -> dict[str, Any]:
        try:
            response = await self._client.post(url, json=payload)
        except httpx.HTTPError as exc:
            raise SearchUnavailable(f"{label} could not be reached: {exc}") from exc
        self._check(response, label)
        return dict(response.json())

    @staticmethod
    def _check(response: httpx.Response, label: str) -> None:
        if response.status_code in (401, 403):
            raise SearchUnavailable(
                f"{label} rejected the key. Check it in Settings."
            )
        if response.status_code == 429:
            raise SearchUnavailable(
                f"{label} is rate limited — the free tier has a monthly cap. "
                "Try again later."
            )
        if response.status_code >= 400:
            raise SearchUnavailable(
                f"{label} returned HTTP {response.status_code}."
            )

    async def read(self, sources: list[Source]) -> list[Source]:
        """Fetch and strip anything that arrived without text.

        Concurrently, and failures are kept rather than dropped: a source whose
        page would not load still has a title, a URL and a snippet, and citing
        it is better than pretending the search did not find it.
        """
        need = [s for s in sources if not s.text]
        if not need:
            return sources

        fetched = await asyncio.gather(
            *(self._read_one(s) for s in need), return_exceptions=True
        )
        by_url = {s.url: s for s in fetched if isinstance(s, Source)}
        return [by_url.get(s.url, s) for s in sources]

    async def _read_one(self, source: Source) -> Source:
        try:
            response = await self._client.get(
                source.url, timeout=httpx.Timeout(FETCH_TIMEOUT_S, connect=4.0)
            )
            content_type = response.headers.get("content-type", "")
            if response.status_code >= 400 or "html" not in content_type:
                return source
            if len(response.content) > FETCH_MAX_BYTES:
                return source
            return Source(
                title=source.title,
                url=source.url,
                snippet=source.snippet,
                text=to_text(response.text),
            )
        except (httpx.HTTPError, UnicodeDecodeError) as exc:
            log.info("search.fetch_failed", url=source.url, error=str(exc))
            return source
