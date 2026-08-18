"""Browser control: the checkout/banking hard block, password refusal, and
element resolution (BUILD_SPEC §9 Phase 7, §9:943).

No real Chrome runs here — `scripts/gate_browser.py` is where a real,
CDP-attached Chrome gets exercised live. What is tested here does not need
one: `_looks_like_checkout`, `_refuse_password_field` and `_locate` are pure
(or near-pure) functions, and the tool bodies are exercised against small
fake `Page`/`Locator` doubles that implement only what `browser.py` actually
calls — the same "stub, don't mock the world" style `test_research.py`
already uses for its own network layer.
"""

from __future__ import annotations

import base64
from collections.abc import Awaitable, Callable

import pytest

from sidecar.tools import browser as browser_module
from sidecar.tools.browser import (
    LAUNCH_HINT,
    BrowserUnavailable,
    _dom_confirms_checkout,
    _escalate_click_risk,
    _escalate_current_page,
    _escalate_fill_risk,
    _escalate_navigate_target,
    _locate,
    _looks_like_a_commit_action,
    _looks_like_checkout,
    _refuse_password_field,
    _role_name,
    browser_click,
    browser_fill,
    browser_navigate,
    browser_read,
    browser_screenshot,
    browser_tabs,
)
from sidecar.tools.registry import Tier, ToolContext

CTX = ToolContext(session_id="s_test", turn_id="t_test")


class FakeLocator:
    def __init__(
        self,
        matches: int = 0,
        text: str = "",
        aria_label: str = "",
        is_submit: bool = False,
    ) -> None:
        self.matches = matches
        self.text = text
        self.aria_label = aria_label
        self.is_submit = is_submit
        self.clicked = False
        self.filled: str | None = None
        self.fill_raises: Exception | None = None
        self.click_raises: Exception | None = None

    async def count(self) -> int:
        return self.matches

    @property
    def first(self) -> FakeLocator:
        return self

    async def inner_text(self) -> str:
        return self.text

    async def get_attribute(self, name: str) -> str | None:
        return self.aria_label if name == "aria-label" else None

    async def evaluate(self, expression: str, arg: object = None) -> object:
        # The real expression checks `type === 'submit'`; the fake just
        # reports what the test asked it to report, not the JS itself.
        return self.is_submit

    async def click(self, timeout: int | None = None) -> None:  # noqa: ASYNC109
        if self.click_raises:
            raise self.click_raises
        self.clicked = True

    async def fill(self, value: str, timeout: int | None = None) -> None:  # noqa: ASYNC109
        if self.fill_raises:
            raise self.fill_raises
        self.filled = value


class FakePage:
    """Implements exactly the `Page` surface `browser.py` calls."""

    def __init__(
        self,
        url: str = "https://example.com",
        title: str = "Example",
        html: str = "<p>Hello.</p>",
        match: FakeLocator | None = None,
        checkout_fields: int = 0,
    ) -> None:
        self.url = url
        self._title = title
        self._html = html
        self._match = match
        self._empty = FakeLocator(matches=0)
        self._checkout_fields = checkout_fields
        self.navigated_to: list[str] = []
        self.screenshot_calls = 0
        self.brought_to_front = False

    async def content(self) -> str:
        return self._html

    async def title(self) -> str:
        return self._title

    async def goto(self, url: str, wait_until: str | None = None) -> None:
        self.navigated_to.append(url)
        self.url = url

    def get_by_role(self, role: str, name: str = "", exact: bool = False) -> FakeLocator:
        return self._match if self._match is not None else self._empty

    def get_by_label(self, text: str, exact: bool = False) -> FakeLocator:
        return self._empty

    def get_by_placeholder(self, text: str, exact: bool = False) -> FakeLocator:
        return self._empty

    def get_by_text(self, text: str, exact: bool = False) -> FakeLocator:
        return self._empty

    def locator(self, selector: str) -> FakeLocator:
        return FakeLocator(matches=self._checkout_fields)

    async def screenshot(self, type: str | None = None, quality: int | None = None) -> bytes:
        self.screenshot_calls += 1
        return b"\xff\xd8fake-jpeg"

    async def bring_to_front(self) -> None:
        self.brought_to_front = True


@pytest.fixture(autouse=True)
def _reset_connection() -> None:
    """`_get_page`/`_connect` are monkeypatched per test; nothing here should
    carry a real (or fake) connection over to the next test."""
    browser_module._playwright = None  # noqa: SLF001
    browser_module._browser = None  # noqa: SLF001


# ── the checkout / banking hard block (§9:943) ──────────────────────────


@pytest.mark.parametrize(
    "url",
    [
        "https://checkout.stripe.com/pay/cs_test_123",
        "https://www.paypal.com/checkout",
        "https://chase.com/login",
        "https://shop.example.com/checkout/payment",
        "https://shop.example.com/order/confirm",
    ],
)
async def test_known_checkout_and_banking_urls_are_recognised(url: str) -> None:
    assert _looks_like_checkout(url)


@pytest.mark.parametrize(
    "url",
    [
        "https://example.com",
        "https://en.wikipedia.org/wiki/Checkout_(disambiguation)".replace("Checkout", "Chess"),
        "https://news.ycombinator.com",
        "https://github.com/anthropics",
    ],
)
async def test_ordinary_urls_are_not_flagged(url: str) -> None:
    assert not _looks_like_checkout(url)


async def test_a_generic_domain_can_still_be_caught_by_its_dom() -> None:
    """The URL check catches the common case; a card-number field on an
    unlisted domain (an embedded payment iframe, e.g.) is what the DOM scan
    is for."""
    page = FakePage(url="https://shop.example.com/step-3", checkout_fields=1)
    assert not _looks_like_checkout(page.url)
    assert await _dom_confirms_checkout(page)  # type: ignore[arg-type]


async def test_no_checkout_fields_means_no_dom_match() -> None:
    page = FakePage(url="https://shop.example.com/step-3", checkout_fields=0)
    assert not await _dom_confirms_checkout(page)  # type: ignore[arg-type]


async def test_navigate_escalates_on_the_target_url_before_loading_it() -> None:
    """No page has loaded yet at this point — only the URL being navigated
    *to* is available, and that has to be enough."""
    assert await _escalate_navigate_target(url="https://checkout.stripe.com/x")
    assert not await _escalate_navigate_target(url="https://example.com")


async def test_current_page_escalation_checks_the_live_page(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    page = FakePage(url="https://chase.com/accounts")
    monkeypatch.setattr(browser_module, "_get_page", _returning(page))

    assert await _escalate_current_page()


async def test_current_page_escalation_is_quiet_on_an_ordinary_page(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    page = FakePage(url="https://example.com")
    monkeypatch.setattr(browser_module, "_get_page", _returning(page))

    assert not await _escalate_current_page()


# ── judging the action, not just the page (2026-08-13) ─────────────────


async def test_commit_wording_in_the_visible_text_is_caught() -> None:
    locator = FakeLocator(text="Buy now")
    assert await _looks_like_a_commit_action(locator)  # type: ignore[arg-type]


async def test_commit_wording_in_the_aria_label_alone_is_caught() -> None:
    """An icon-only button ("🛒") can carry the meaning in its label with no
    visible text at all — checked independently of `inner_text`."""
    locator = FakeLocator(text="", aria_label="Complete purchase")
    assert await _looks_like_a_commit_action(locator)  # type: ignore[arg-type]


async def test_a_bare_submit_button_is_caught_structurally() -> None:
    """No telltale wording anywhere — only `type="submit"` says what it
    does. The wording check alone would miss this."""
    locator = FakeLocator(text="Continue", aria_label="", is_submit=True)
    assert await _looks_like_a_commit_action(locator)  # type: ignore[arg-type]


async def test_an_ordinary_link_is_not_a_commit_action() -> None:
    locator = FakeLocator(text="Next page", aria_label="", is_submit=False)
    assert not await _looks_like_a_commit_action(locator)  # type: ignore[arg-type]


async def test_click_risk_still_escalates_on_a_checkout_page(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The page-level check runs first, and an ordinary-looking "OK" button
    on a checkout page still escalates — nothing about that coverage
    shrank when the base tier dropped to SAFE."""
    match = FakeLocator(matches=1, text="OK")
    page = FakePage(url="https://checkout.stripe.com/pay/x", match=match)
    monkeypatch.setattr(browser_module, "_get_page", _returning(page))

    assert await _escalate_click_risk(target="OK")


async def test_click_risk_escalates_on_the_elements_own_wording(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    match = FakeLocator(matches=1, text="Delete my account")
    page = FakePage(url="https://example.com/settings", match=match)
    monkeypatch.setattr(browser_module, "_get_page", _returning(page))

    assert await _escalate_click_risk(target="Delete my account")


async def test_click_risk_is_quiet_for_an_ordinary_click(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The actual point of this whole change: a routine click on an ordinary
    page stops asking entirely."""
    match = FakeLocator(matches=1, text="Coldplay - Official Site")
    page = FakePage(url="https://google.com/search?q=coldplay", match=match)
    monkeypatch.setattr(browser_module, "_get_page", _returning(page))

    assert not await _escalate_click_risk(target="the first search result")


async def test_click_risk_is_quiet_when_nothing_resolved(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A target that does not exist is the tool's "not found" to report, not
    a reason to escalate a click that will never happen."""
    page = FakePage(url="https://example.com", match=None)
    monkeypatch.setattr(browser_module, "_get_page", _returning(page))

    assert not await _escalate_click_risk(target="nothing like this")


async def test_fill_risk_escalates_on_a_payment_shaped_field(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    page = FakePage(url="https://example.com")
    monkeypatch.setattr(browser_module, "_get_page", _returning(page))

    assert await _escalate_fill_risk(target="Card number", value="4242")


async def test_fill_risk_is_quiet_for_an_ordinary_field(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    page = FakePage(url="https://example.com")
    monkeypatch.setattr(browser_module, "_get_page", _returning(page))

    assert not await _escalate_fill_risk(target="the search box", value="coldplay")


async def test_fill_risk_still_escalates_on_a_checkout_page(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    page = FakePage(url="https://checkout.stripe.com/pay/x")
    monkeypatch.setattr(browser_module, "_get_page", _returning(page))

    assert await _escalate_fill_risk(target="notes", value="anything")


# ── the password-field refusal ───────────────────────────────────────


@pytest.mark.parametrize(
    "target",
    [
        "the password field",
        "Password",
        "CVV",
        "cvc code",
        "your PIN code",
        "Social Security Number",
    ],
)
async def test_password_shaped_targets_are_refused(target: str) -> None:
    assert await _refuse_password_field(target=target) is not None


@pytest.mark.parametrize("target", ["the email field", "search box", "the Send button", "username"])
async def test_ordinary_targets_are_not_refused(target: str) -> None:
    assert await _refuse_password_field(target=target) is None


# ── element resolution ───────────────────────────────────────────────


@pytest.mark.parametrize(
    ("said", "expected"),
    [
        ("the Send button", "Send"),
        ("the email field", "email"),
        ("Submit", "Submit"),
        ("the search box", "search"),
    ],
)
def test_role_name_strips_the_leading_article_and_trailing_noun(said: str, expected: str) -> None:
    assert _role_name(said) == expected


async def test_locate_finds_a_single_role_match() -> None:
    match = FakeLocator(matches=1, text="Send")
    page = FakePage(match=match)

    located = await _locate(page, "the Send button")  # type: ignore[arg-type]

    assert located is match  # type: ignore[comparison-overlap]


async def test_locate_returns_none_when_nothing_matches() -> None:
    page = FakePage(match=None)

    assert await _locate(page, "nothing like this exists") is None  # type: ignore[arg-type]


async def test_locate_takes_the_first_of_several_ambiguous_matches() -> None:
    """Refusing to act on an ambiguous-but-real description is worse than
    picking the first of several near-identical matches."""
    match = FakeLocator(matches=3, text="Add to cart")
    page = FakePage(match=match)

    located = await _locate(page, "Add to cart")  # type: ignore[arg-type]

    assert located is match  # type: ignore[comparison-overlap]


# ── the tools themselves ─────────────────────────────────────────────


def _returning(value: object) -> Callable[..., Awaitable[object]]:
    async def fn(*_a: object, **_k: object) -> object:
        return value

    return fn


def _raising(exc: Exception) -> Callable[..., Awaitable[object]]:
    async def fn(*_a: object, **_k: object) -> object:
        raise exc

    return fn


async def test_tiers_deviate_from_build_specs_blanket_confirm_by_design() -> None:
    """BUILD_SPEC §9:476 puts browser_click/browser_fill at CONFIRM
    unconditionally. They ship SAFE here instead (2026-08-13, at Eyaas's
    request) — rule 5 names specific actions ("delete, overwrite, send,
    purchase, post"), not every DOM interaction, and a routine click paying
    the same confirmation as a purchase was asking about the wrong thing.
    `_escalate_click_risk`/`_escalate_fill_risk` reach CONFIRM for the calls
    that actually warrant it — see the tests below."""
    from sidecar.tools import registry

    snapshot = registry.snapshot()
    assert snapshot["browser_navigate"].tier is Tier.SAFE
    assert snapshot["browser_read"].tier is Tier.AUTO
    assert snapshot["browser_click"].tier is Tier.SAFE
    assert snapshot["browser_fill"].tier is Tier.SAFE
    assert snapshot["browser_screenshot"].tier is Tier.AUTO
    assert snapshot["browser_tabs"].tier is Tier.AUTO


async def test_every_browser_tool_carries_the_checkout_escalation() -> None:
    """§9:943 says "regardless of tool tier" — that only means something if
    *every* tool has the hook, not only the ones already at CONFIRM."""
    from sidecar.tools import registry

    snapshot = registry.snapshot()
    for name in (
        "browser_navigate",
        "browser_read",
        "browser_click",
        "browser_fill",
        "browser_screenshot",
        "browser_tabs",
    ):
        assert snapshot[name].escalate is not None, name


async def test_only_fill_carries_the_password_refusal() -> None:
    from sidecar.tools import registry

    snapshot = registry.snapshot()
    assert snapshot["browser_fill"].refuse is not None
    assert snapshot["browser_click"].refuse is None


async def test_navigate_reports_browser_unavailable_plainly(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        browser_module, "_get_page", _raising(BrowserUnavailable("It is not open."))
    )

    result = await browser_navigate(CTX, "example.com")

    assert not result.ok
    assert result.error == "browser_unavailable"
    assert LAUNCH_HINT in result.summary


def test_no_user_facing_browser_error_names_chrome() -> None:
    """`LAUNCH_HINT` was made browser-agnostic when Eyaas's real default
    turned out to be Brave; `BrowserUnavailable`'s own lead was missed and
    still said "Chrome isn't running in debug mode." Telling a Brave user to
    start Chrome is worse advice than none — CDP is the same protocol on
    every Chromium browser, and `browser.setup` detects which one is
    actually his.
    """
    assert "Chrome" not in LAUNCH_HINT
    assert "Chrome" not in str(BrowserUnavailable())
    assert "Chrome" not in str(BrowserUnavailable("It is running, but no tab is open."))


async def test_navigate_adds_a_scheme_when_none_was_given(monkeypatch: pytest.MonkeyPatch) -> None:
    page = FakePage()
    monkeypatch.setattr(browser_module, "_get_page", _returning(page))

    await browser_navigate(CTX, "example.com")

    assert page.navigated_to == ["https://example.com"]


async def test_read_returns_cleaned_text_with_the_url(monkeypatch: pytest.MonkeyPatch) -> None:
    page = FakePage(
        url="https://example.com/article", html="<p>Real content.</p><script>x</script>"
    )
    monkeypatch.setattr(browser_module, "_get_page", _returning(page))

    result = await browser_read(CTX)

    assert result.ok
    assert "Real content." in result.summary
    assert "https://example.com/article" in result.summary
    assert "<script>" not in result.summary


async def test_read_is_named_as_an_untrusted_source() -> None:
    """§11: the *next* tool call after this one is force-escalated by the
    agent loop — `core/agent.py`'s `LoopState.should_escalate` reads this
    set, not anything local to this file."""
    from sidecar.tools.registry import UNTRUSTED_SOURCE_TOOLS

    assert "browser_read" in UNTRUSTED_SOURCE_TOOLS
    assert "browser_navigate" in UNTRUSTED_SOURCE_TOOLS


async def test_click_runs_the_match_it_finds(monkeypatch: pytest.MonkeyPatch) -> None:
    match = FakeLocator(matches=1)
    page = FakePage(match=match)
    monkeypatch.setattr(browser_module, "_get_page", _returning(page))

    result = await browser_click(CTX, "the Send button")

    assert result.ok
    assert match.clicked


async def test_click_names_what_it_could_not_find(monkeypatch: pytest.MonkeyPatch) -> None:
    page = FakePage(match=None)
    monkeypatch.setattr(browser_module, "_get_page", _returning(page))

    result = await browser_click(CTX, "the Launch Missiles button")

    assert not result.ok
    assert result.error == "not_found"
    assert "Launch Missiles" in result.summary


async def test_fill_types_the_value_into_the_match(monkeypatch: pytest.MonkeyPatch) -> None:
    match = FakeLocator(matches=1)
    page = FakePage(match=match)
    monkeypatch.setattr(browser_module, "_get_page", _returning(page))

    result = await browser_fill(CTX, "the email field", "eyaas@example.com")

    assert result.ok
    assert match.filled == "eyaas@example.com"


async def test_screenshot_returns_a_base64_image(monkeypatch: pytest.MonkeyPatch) -> None:
    page = FakePage(url="https://example.com")
    monkeypatch.setattr(browser_module, "_get_page", _returning(page))

    result = await browser_screenshot(CTX)

    assert result.ok
    assert page.screenshot_calls == 1
    display = result.display or {}
    assert base64.b64decode(display["image_b64"]) == b"\xff\xd8fake-jpeg"


async def test_tabs_lists_every_open_page(monkeypatch: pytest.MonkeyPatch) -> None:
    pages = [FakePage(url="https://a.test", title="A"), FakePage(url="https://b.test", title="B")]

    class FakeContext:
        def __init__(self, pages: list[FakePage]) -> None:
            self.pages = pages

    class FakeBrowser:
        def __init__(self, pages: list[FakePage]) -> None:
            self.contexts = [FakeContext(pages)]

    monkeypatch.setattr(browser_module, "_connect", _returning(FakeBrowser(pages)))

    result = await browser_tabs(CTX, action="list")

    assert result.ok
    display = result.display or {}
    assert [t["url"] for t in display["tabs"]] == ["https://a.test", "https://b.test"]


async def test_tabs_switches_by_index(monkeypatch: pytest.MonkeyPatch) -> None:
    pages = [FakePage(url="https://a.test"), FakePage(url="https://b.test")]

    class FakeContext:
        def __init__(self, pages: list[FakePage]) -> None:
            self.pages = pages

    class FakeBrowser:
        def __init__(self, pages: list[FakePage]) -> None:
            self.contexts = [FakeContext(pages)]

    monkeypatch.setattr(browser_module, "_connect", _returning(FakeBrowser(pages)))

    result = await browser_tabs(CTX, action="switch", index=1)

    assert result.ok
    assert pages[1].brought_to_front


async def test_tabs_refuses_an_out_of_range_switch(monkeypatch: pytest.MonkeyPatch) -> None:
    pages = [FakePage(url="https://a.test")]

    class FakeContext:
        def __init__(self, pages: list[FakePage]) -> None:
            self.pages = pages

    class FakeBrowser:
        def __init__(self, pages: list[FakePage]) -> None:
            self.contexts = [FakeContext(pages)]

    monkeypatch.setattr(browser_module, "_connect", _returning(FakeBrowser(pages)))

    result = await browser_tabs(CTX, action="switch", index=7)

    assert not result.ok
    assert result.error == "bad_index"
