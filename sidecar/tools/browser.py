"""Real browser control over a real, logged-in Chrome (BUILD_SPEC §9 Phase 7).

`research(query)` already answers "what is the RTX 5090 going for" over a
search API — that half of Phase 7 shipped without a browser at all (see
CLAUDE.md, and `providers/search.py`'s own docstring for why). What only a
real browser can do is anything that needs to be *logged in*: "check my
email and summarise anything urgent" needs a real Gmail session, not a
search index.

**Connects to a Chrome the user already has running, over CDP — it does not
launch or bundle one.** `playwright.chromium.launch()` would start a fresh,
logged-out browser with Playwright's own bundled Chromium (several hundred
megabytes, and none of the user's cookies); `connect_over_cdp` attaches to
whatever is already open, real profile and all. `browser.setup` (in
`rpc/handlers.py`) writes the shortcut that starts Chrome with
`--remote-debugging-port=9222 --user-data-dir=<the real profile>`.

**Lazy, not at startup.** Chrome usually is not running in debug mode yet,
and a retry-happy connection attempt at boot is wasted work for a feature
most turns never touch.

**Element targeting is accessibility-tree-based, not CSS.** A model was never
going to produce a working CSS selector for a page it cannot see the DOM of;
`get_by_role`/`get_by_label`/`get_by_text` resolve a plain-English
description ("the Send button") against the page's own accessibility tree,
which is what BUILD_SPEC asks for in as many words ("not brittle CSS
selectors").

**§11's checkout/banking hard block** (BUILD_SPEC §9:943): "any page whose
URL or DOM matches banking, payment, or checkout patterns requires T2
confirmation regardless of tool tier." Built on the same `Tool.escalate` hook
`registry.py` grew for this file specifically — reused, not duplicated,
because the mechanics (force the effective tier to CONFIRM, bypass trust,
label the dialog) are identical to §11's untrusted-content escalation; only
the *trigger* differs. `browser_fill` additionally refuses a password field
outright via `Tool.refuse`, before any confirmation would even fire —
approving a fill without knowing it targets a password field is not a choice
anyone should be asked to make.

**`browser_click`/`browser_fill` are SAFE here, not BUILD_SPEC's blanket
CONFIRM (2026-08-13, at Eyaas's request — friction on ordinary browsing,
e.g. clicking a search result while searching for something, cost the same
dialog as clicking "Buy now").** CLAUDE.md rule 5 names specific actions —
*"delete, overwrite, send, purchase, post"* — not "every DOM interaction",
and asking about a routine click the same way as a purchase was asking about
the wrong thing. `_escalate_click_risk`/`_escalate_fill_risk` generalise the
checkout detector above to the *element being acted on*: still runs
`_escalate_current_page` first (nothing about that coverage shrinks), and
additionally judges whether the click looks like it commits to something
(rule 5's own words, plus a structural `type=submit` check) or the field
being filled is payment-shaped. DANGER tier is untouched by any of this —
only these two tools move, and only between SAFE and CONFIRM. The honest
gap: a custom JS button with no telltale wording, no aria-label, and no form
semantics (an ambiguous "Continue") will not escalate — the same shape of
trade-off already accepted for the checkout URL/DOM list, and the failure
direction is asking less than an ideal detector would for an obscure case,
not asking about everything, which would defeat the point.
"""

from __future__ import annotations

import base64
from typing import Any

import structlog
from playwright.async_api import Browser, Locator, Page, Playwright, async_playwright

from sidecar.providers.search import to_text
from sidecar.tools.registry import Tier, ToolContext, ToolResult, tool

log = structlog.get_logger(__name__)

CDP_URL = "http://localhost:9222"
#: How the browser needs to be started for this to reach it. Printed in every
#: refusal, because "isn't running in debug mode" with no fix is a dead end —
#: the exact BUILD_SPEC §9 acceptance line.
#:
#: **Deliberately says "your browser", not "Chrome".** CDP is a protocol every
#: Chromium-based browser exposes the same way — Chrome, Brave, Edge — and
#: `browser.setup` detects which one is actually the user's default (the same
#: `UserChoice` lookup `open_app`'s "browser" category already uses) rather
#: than assuming Chrome. Naming Chrome here when the user's real browser is
#: Brave, say, would be actively wrong advice, not just imprecise — the flag
#: is the same, but the exe is not.
LAUNCH_HINT = (
    'Open Settings and use "Write launcher" under Browser control — it detects '
    "your actual default browser and writes a script for it — or start it "
    'yourself with --remote-debugging-port=9222 --user-data-dir="<its existing profile>".'
)

#: Truncated the same way `research.py` truncates a fetched page — enough for
#: a model to work from, small enough not to blow the context budget §8.2
#: guards.
READ_MAX_CHARS = 4000
#: Downscaled for the same reason `screen.py`'s thumbnail is: a fast
#: round-trip, not a second full-resolution copy of the frame.
SCREENSHOT_MAX_PX = 1280


class BrowserUnavailable(RuntimeError):
    """The browser is not reachable over CDP. Carries the fix, same shape as
    `providers.search.SearchUnavailable`.

    **Says "your browser", not "Chrome", for the same reason `LAUNCH_HINT`
    above does** — and this half was missed when that one was fixed. Eyaas's
    default is Brave; telling a Brave user that "Chrome isn't running" sends
    them to install a browser they do not use, which is worse than saying
    nothing. BUILD_SPEC §9's acceptance line quotes the Chrome wording
    because it was written before `browser.setup` learned to detect the real
    default; the requirement it is actually making — a clear error with the
    fix, never a stack trace — is met either way.
    """

    def __init__(self, detail: str = "") -> None:
        lead = (
            "Your browser isn't running with remote debugging turned on."
            f"{(' ' + detail) if detail else ''}"
        )
        super().__init__(f"{lead} {LAUNCH_HINT}")


# ── the connection ────────────────────────────────────────────────────
#
# Module-level and lazy: nothing here runs until the first browser_* call.
# `_playwright`/`_browser` are held for the life of the process — closing and
# reconnecting per call would pay CDP's handshake cost on every single tool
# use, and Chrome does not mind one long-lived remote-debugging client.

_playwright: Playwright | None = None
_browser: Browser | None = None


async def _connect() -> Browser:
    """The live `Browser`, connecting on first use. Raises `BrowserUnavailable`."""
    global _playwright, _browser
    if _browser is not None and _browser.is_connected():
        return _browser

    if _playwright is None:
        _playwright = await async_playwright().start()
    try:
        _browser = await _playwright.chromium.connect_over_cdp(CDP_URL)
    except Exception as exc:
        raise BrowserUnavailable(str(exc)) from exc
    return _browser


async def _get_page() -> Page:
    """The active tab — the last one focused, or the first one open."""
    browser = await _connect()
    contexts = browser.contexts
    if not contexts:
        raise BrowserUnavailable("It is running, but no window is open.")
    context = contexts[0]
    pages = context.pages
    if not pages:
        raise BrowserUnavailable("It is running, but no tab is open.")
    # Playwright does not expose "which tab has focus" directly; the most
    # recently opened tab is the best available proxy for "the one the user
    # is looking at" — better than always defaulting to the first tab ever
    # opened, which is often a stale one left behind hours ago.
    return pages[-1]


async def aclose() -> None:
    """Release the CDP connection. For shutdown and for tests."""
    global _playwright, _browser
    if _browser is not None:
        with _suppress_close_errors():
            await _browser.close()
        _browser = None
    if _playwright is not None:
        with _suppress_close_errors():
            await _playwright.stop()
        _playwright = None


class _suppress_close_errors:
    """A closed CDP connection raising on its own teardown is not worth a
    traceback in the log — the goal was to be disconnected, and it is."""

    def __enter__(self) -> None:
        return None

    def __exit__(self, *exc: object) -> bool:
        return True


# ── §11's checkout / banking hard block ────────────────────────────────

#: Not a cleverer alternative to a blocklist — CLAUDE.md's "blocklists on a
#: shell always lose" is about `run_powershell`'s arbitrary-command surface,
#: a different shape of problem. Matching known payment domains and checkout
#: URL segments is the industry-standard approach here, and it is literally
#: what BUILD_SPEC §9:943 asks for.
_CHECKOUT_DOMAINS = (
    "checkout.shopify.com",
    "stripe.com",
    "paypal.com",
    "checkout.stripe.com",
    "pay.google.com",
    "checkout.google.com",
    "amazon.com/gp/buy",
    "amazon.com/checkout",
)
_BANKING_DOMAINS = (
    "chase.com",
    "bankofamerica.com",
    "wellsfargo.com",
    "citibank.com",
    "capitalone.com",
    "americanexpress.com",
    "paypal.com/myaccount",
)
_URL_KEYWORDS = ("/checkout", "/payment", "/billing", "/order/confirm", "/pay/")


def _looks_like_checkout(url: str) -> bool:
    lowered = url.lower()
    if any(domain in lowered for domain in _CHECKOUT_DOMAINS + _BANKING_DOMAINS):
        return True
    return any(keyword in lowered for keyword in _URL_KEYWORDS)


async def _dom_confirms_checkout(page: Page) -> bool:
    """A light scan, not a crawl: does the page carry a payment field?

    Checked in addition to the URL because plenty of checkout flows sit on a
    generic-looking domain (an embedded payment iframe, a subdomain not in
    the list above) — the URL check catches the common case cheaply, this
    catches what it misses.
    """
    try:
        count = await page.locator(
            '[autocomplete="cc-number"], [autocomplete="cc-csc"], '
            'input[name*="card" i], input[name*="cvv" i], input[name*="cvc" i]'
        ).count()
    except Exception:  # noqa: BLE001 — a scan that cannot run is not evidence either way
        return False
    return count > 0


async def _escalate_current_page(**_kwargs: object) -> bool:
    """§11's checkout gate for the tools with no URL argument of their own —
    `browser_read`, `browser_click`, `browser_fill`, `browser_screenshot`,
    `browser_tabs`. Whatever page is currently open is what these would act
    on or reveal."""
    page = await _get_page()
    if _looks_like_checkout(page.url):
        return True
    return await _dom_confirms_checkout(page)


async def _escalate_navigate_target(url: str = "", **_kwargs: object) -> bool:
    """`browser_navigate`'s own variant: the page has not loaded yet, so
    there is no DOM to scan — only the URL being navigated *to*."""
    return _looks_like_checkout(url)


# ── judging the action itself, not just the page (browser_click/browser_fill) ──
#
# Rule 5 names specific actions — "delete, overwrite, send, purchase, post" —
# not "every DOM interaction." BUILD_SPEC's own tier table put every click and
# fill at CONFIRM regardless, presumably because telling a routine click from
# a purchase looked hard to automate safely. The checkout/banking detector
# above already does exactly this kind of judgment for one page-level case;
# this generalises it to the *element* being acted on, which is what lets
# `browser_click`/`browser_fill` drop to SAFE below instead of asking on
# every call — see the module docstring for the tier decision itself.

#: Rule 5's own words, plus the everyday synonyms a real page uses for them.
#: Checked against an element's visible text *and* its aria-label, because an
#: icon-only button ("🛒") can carry the meaning in the label with no visible
#: text at all.
_COMMIT_WORDS = (
    "buy",
    "purchase",
    "pay",
    "checkout",
    "place order",
    "confirm order",
    "submit",
    "send",
    "post",
    "publish",
    "donate",
    "transfer",
    "delete",
    "remove",
    "cancel subscription",
    "unsubscribe",
    "deactivate",
)


async def _looks_like_a_commit_action(locator: Locator) -> bool:
    """Does the resolved element itself look like it *does* something —
    submits a form, buys, sends, deletes — rather than just navigating or
    revealing more of the page? A "next page" link or a search result is
    none of rule 5's named actions; a button reading "Buy now" is exactly one
    of them.

    Two independent checks, not one — each catches what the other misses.
    Text/aria-label catches a JS-driven "Buy Now" `<div>` with no form
    semantics at all; the structural `type=submit` check catches an
    icon-only button with no telltale wording. Every failure here is read as
    "no signal found", the same as `_dom_confirms_checkout`'s own scan — a
    check that cannot run is not evidence either way.
    """
    try:
        text = (await locator.inner_text()).strip().lower()
    except Exception:  # noqa: BLE001
        text = ""
    try:
        aria_label = (await locator.get_attribute("aria-label")) or ""
    except Exception:  # noqa: BLE001
        aria_label = ""
    combined = f"{text} {aria_label}".lower()
    if any(word in combined for word in _COMMIT_WORDS):
        return True

    try:
        is_submit = await locator.evaluate(
            "el => el.type === 'submit' || el.getAttribute('type') === 'submit'"
        )
    except Exception:  # noqa: BLE001
        is_submit = False
    return bool(is_submit)


async def _escalate_click_risk(target: str = "", **_kwargs: object) -> bool:
    """`browser_click`'s escalate hook: the checkout/banking page check,
    plus whether *this* click looks like it commits to something."""
    if await _escalate_current_page():
        return True
    page = await _get_page()
    locator = await _locate(page, target)
    if locator is None:
        # Nothing resolved — the tool itself will report "not found" when it
        # runs; that is a reason to fail the call, not a reason to ask about
        # a click that is never going to happen.
        return False
    return await _looks_like_a_commit_action(locator)


#: Filling text rarely sends anything by itself — a subsequent click usually
#: does, and that click carries its own check above. The real fill-time risk
#: is a payment-shaped *field*, which the page-level checkout scan may not
#: always catch (a card field embedded on an otherwise ordinary domain).
_PAYMENT_FIELD_WORDS = (
    "card number",
    "card",
    "cvv",
    "cvc",
    "expiry",
    "expiration",
    "billing",
    "iban",
    "routing number",
    "account number",
)


async def _escalate_fill_risk(target: str = "", value: str = "", **_kwargs: object) -> bool:
    """`browser_fill`'s escalate hook. `_refuse_password_field` (`Tool.refuse`)
    already hard-blocks credential fields before this ever runs — this is the
    separate, softer case of a payment field that is not a password."""
    if await _escalate_current_page():
        return True
    return any(word in target.lower() for word in _PAYMENT_FIELD_WORDS)


# ── the password-field refusal ─────────────────────────────────────────

_PASSWORD_WORDS = (
    "password",
    "passwd",
    "pwd",
    "passcode",
    "pin code",
    "security code",
    "cvv",
    "cvc",
    "ssn",
    "social security",
)


async def _refuse_password_field(
    target: str = "", value: str = "", **_kwargs: object
) -> str | None:
    """A hard block, not a dialog — see the module docstring. Reads only the
    call's own `target` argument (what field the model says it is filling),
    which is why this can run before any confirmation and before the page
    is even touched."""
    lowered = target.lower()
    if any(word in lowered for word in _PASSWORD_WORDS):
        return "that looks like a password or other credential field"
    return None


# ── resolving a plain-English target against the accessibility tree ────

_GENERIC_SUFFIXES = ("button", "field", "box", "link", "input", "option")


def _role_name(target: str) -> str:
    """"the Send button" -> "Send" — a role lookup wants the label, not the
    description of what kind of control it is."""
    words = target.strip().split()
    if words and words[0].lower() == "the":
        words = words[1:]
    if len(words) > 1 and words[-1].lower() in _GENERIC_SUFFIXES:
        words = words[:-1]
    return " ".join(words) or target


async def _locate(page: Page, target: str) -> Locator | None:
    """Best-effort resolution of a natural-language description, tried in
    the order a person would look: what it's *called* (role/label), then
    what it *says* (visible text). Not CSS — see the module docstring."""
    name = _role_name(target)
    for locator in (
        page.get_by_role("button", name=name, exact=False),
        page.get_by_role("link", name=name, exact=False),
        page.get_by_role("textbox", name=name, exact=False),
        page.get_by_label(target, exact=False),
        page.get_by_placeholder(target, exact=False),
        page.get_by_text(target, exact=False),
    ):
        try:
            count = await locator.count()
        except Exception:  # noqa: BLE001 — a bad locator is a miss, not a crash
            continue
        if count >= 1:
            # More than one match takes the first rather than failing — an
            # ambiguous description landing on the wrong one of several
            # near-identical buttons is a smaller cost than refusing to act
            # on an instruction that named something real.
            return locator.first
    return None


# ── the tools ────────────────────────────────────────────────────────


@tool(
    name="browser_navigate",
    tier=Tier.SAFE,
    description=(
        "Go to a URL in the browser. Use before reading, clicking or filling "
        "anything on a page that is not already open."
    ),
    escalate=_escalate_navigate_target,
)
async def browser_navigate(ctx: ToolContext, url: str) -> ToolResult:
    """Open a URL in the current tab.

    Args:
        url: The address to go to, including https://.
    """
    target = url if "://" in url else f"https://{url}"
    try:
        page = await _get_page()
        await page.goto(target, wait_until="domcontentloaded")
    except BrowserUnavailable as exc:
        return ToolResult(ok=False, summary=str(exc), error="browser_unavailable")
    except Exception as exc:  # noqa: BLE001 — a bad URL or a dead page, told plainly
        return ToolResult(
            ok=False, summary=f"Could not open {target}: {exc}", error="navigate_failed"
        )

    log.info("tool.browser_navigate", url=target)
    return ToolResult(
        ok=True,
        data={"url": page.url},
        summary=f"Opened {page.url}.",
        display={"url": page.url, "title": await _safe_title(page)},
    )


@tool(
    name="browser_read",
    tier=Tier.AUTO,
    description=(
        "Read the visible text of the current browser tab. Use to see what a "
        "page actually says before summarising, clicking or filling it."
    ),
    escalate=_escalate_current_page,
)
async def browser_read(ctx: ToolContext) -> ToolResult:
    """Read the current page as text."""
    try:
        page = await _get_page()
        html = await page.content()
    except BrowserUnavailable as exc:
        return ToolResult(ok=False, summary=str(exc), error="browser_unavailable")

    text = to_text(html, limit=READ_MAX_CHARS)
    if not text:
        return ToolResult(
            ok=True,
            data={"url": page.url},
            summary=f"{page.url} loaded, but there was no readable text on it.",
            display={"url": page.url},
        )

    log.info("tool.browser_read", url=page.url, chars=len(text))
    # §11: this is somebody else's writing, not this machine's own state —
    # `browser_read` is in `UNTRUSTED_SOURCE_TOOLS` (registry.py), so the
    # agent loop force-escalates whatever tool call comes right after this
    # one, the same as `research`'s fetched text already does.
    return ToolResult(
        ok=True,
        data={"url": page.url},
        summary=f"Text from {page.url}:\n{text}",
        display={"url": page.url, "chars": len(text)},
    )


async def _preview_click(target: str) -> dict[str, Any] | None:
    """What would be clicked, resolved before the user is asked — the same
    "show the real thing, not a promise of it" rule `capture_screen`'s
    preview follows."""
    try:
        page = await _get_page()
        locator = await _locate(page, target)
    except BrowserUnavailable:
        return None
    if locator is None:
        return None
    try:
        text = (await locator.inner_text()).strip()[:120]
    except Exception:  # noqa: BLE001 — detail lost, confirmation kept
        text = ""
    return {"kind": "browser_action", "action": "click", "target": target, "matched": text}


@tool(
    name="browser_click",
    # SAFE, not BUILD_SPEC's blanket CONFIRM — see the module docstring.
    # `escalate` still reaches CONFIRM for anything that actually commits to
    # something (§11's checkout gate, plus `_looks_like_a_commit_action`).
    tier=Tier.SAFE,
    description=(
        "Click something on the current page, described in plain words, e.g. "
        "'the Send button' or 'the first search result'. Resolved against the "
        "page's own accessibility structure, not a CSS selector."
    ),
    preview=_preview_click,
    escalate=_escalate_click_risk,
)
async def browser_click(ctx: ToolContext, target: str) -> ToolResult:
    """Click an element on the page.

    Args:
        target: What to click, described the way a person would say it.
    """
    try:
        page = await _get_page()
        locator = await _locate(page, target)
    except BrowserUnavailable as exc:
        return ToolResult(ok=False, summary=str(exc), error="browser_unavailable")

    if locator is None:
        return ToolResult(
            ok=False,
            summary=f"I could not find anything on the page matching {target!r}.",
            error="not_found",
        )

    try:
        await locator.click(timeout=5000)
    except Exception as exc:  # noqa: BLE001 — told plainly rather than a stack trace
        return ToolResult(
            ok=False, summary=f"Clicking {target!r} failed: {exc}", error="click_failed"
        )

    log.info("tool.browser_click", target=target, url=page.url)
    return ToolResult(ok=True, data={"target": target}, summary=f"Clicked {target}.")


async def _preview_fill(target: str, value: str) -> dict[str, Any] | None:
    try:
        page = await _get_page()
        locator = await _locate(page, target)
    except BrowserUnavailable:
        return None
    if locator is None:
        return None
    return {
        "kind": "browser_action",
        "action": "fill",
        "target": target,
        # The value itself, not masked — a fill the user cannot read is not
        # one they can meaningfully approve. Password fields never reach
        # this point at all; `Tool.refuse` stops them before the preview
        # would even run.
        "matched": value[:120],
    }


@tool(
    name="browser_fill",
    # SAFE, not BUILD_SPEC's blanket CONFIRM — see the module docstring.
    # `refuse` still hard-blocks credential fields before this ever runs, and
    # `escalate` still reaches CONFIRM for a payment-shaped field or a
    # checkout/banking page.
    tier=Tier.SAFE,
    description=(
        "Type into a field on the current page, described in plain words, e.g. "
        "'the email field' or 'the search box'. Refuses password fields "
        "outright — use the browser's own saved-password fill for those."
    ),
    preview=_preview_fill,
    escalate=_escalate_fill_risk,
    refuse=_refuse_password_field,
)
async def browser_fill(ctx: ToolContext, target: str, value: str) -> ToolResult:
    """Fill a field on the page.

    Args:
        target: Which field, described the way a person would say it.
        value: What to type into it.
    """
    try:
        page = await _get_page()
        locator = await _locate(page, target)
    except BrowserUnavailable as exc:
        return ToolResult(ok=False, summary=str(exc), error="browser_unavailable")

    if locator is None:
        return ToolResult(
            ok=False,
            summary=f"I could not find a field on the page matching {target!r}.",
            error="not_found",
        )

    try:
        await locator.fill(value, timeout=5000)
    except Exception as exc:  # noqa: BLE001
        return ToolResult(
            ok=False, summary=f"Filling {target!r} failed: {exc}", error="fill_failed"
        )

    log.info("tool.browser_fill", target=target, url=page.url)
    return ToolResult(ok=True, data={"target": target}, summary=f"Filled {target}.")


@tool(
    name="browser_screenshot",
    tier=Tier.AUTO,
    description="Take a screenshot of the current browser tab.",
    escalate=_escalate_current_page,
)
async def browser_screenshot(ctx: ToolContext) -> ToolResult:
    """Screenshot the current tab. Ephemeral — never written to disk (§11),
    the same rule `tools/screen.py` follows for the whole-desktop capture."""
    try:
        page = await _get_page()
        png = await page.screenshot(type="jpeg", quality=80)
    except BrowserUnavailable as exc:
        return ToolResult(ok=False, summary=str(exc), error="browser_unavailable")
    except Exception as exc:  # noqa: BLE001
        return ToolResult(ok=False, summary=f"Screenshot failed: {exc}", error="screenshot_failed")

    log.info("tool.browser_screenshot", url=page.url, bytes=len(png))
    return ToolResult(
        ok=True,
        data={"url": page.url},
        summary=f"Captured a screenshot of {page.url}.",
        display={"url": page.url, "image_b64": base64.b64encode(png).decode("ascii")},
    )


@tool(
    name="browser_tabs",
    tier=Tier.AUTO,
    description=(
        "List the browser's open tabs, or switch to one by its number from "
        "that list. Use 'list' to see what is open, or 'switch' with an index."
    ),
    escalate=_escalate_current_page,
)
async def browser_tabs(
    ctx: ToolContext, action: str = "list", index: int | None = None
) -> ToolResult:
    """List or switch between open tabs.

    Args:
        action: "list" to see open tabs, or "switch" to bring one forward.
        index: Which tab, from the list "list" returns. Required for "switch".
    """
    try:
        browser = await _connect()
    except BrowserUnavailable as exc:
        return ToolResult(ok=False, summary=str(exc), error="browser_unavailable")

    pages = [p for context in browser.contexts for p in context.pages]
    if not pages:
        return ToolResult(ok=True, data={"tabs": []}, summary="No tabs are open.")

    if action == "switch":
        if index is None or not (0 <= index < len(pages)):
            return ToolResult(
                ok=False,
                summary=f"Give a tab number from 0 to {len(pages) - 1}.",
                error="bad_index",
            )
        await pages[index].bring_to_front()
        log.info("tool.browser_tabs_switch", index=index, url=pages[index].url)
        return ToolResult(
            ok=True, data={"switched_to": index}, summary=f"Switched to {pages[index].url}."
        )

    listing = [
        {"index": i, "url": p.url, "title": await _safe_title(p)} for i, p in enumerate(pages)
    ]
    lines = "\n".join(f"{t['index']}: {t['title']} — {t['url']}" for t in listing)
    return ToolResult(
        ok=True,
        data={"tabs": listing},
        summary=f"{len(listing)} tab(s) open:\n{lines}",
        display={"tabs": listing},
    )


async def _safe_title(page: Page) -> str:
    try:
        return await page.title()
    except Exception:  # noqa: BLE001 — a title is a nicety, not worth failing over
        return ""
