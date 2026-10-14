"""Plain Playwright helpers. No LangGraph in here, so selector fixes stay isolated."""
import os
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path

from playwright.sync_api import sync_playwright

import naukri_selectors as S

STATE_FILE = os.getenv("NAUKRI_STATE_FILE", "state.json")
SHOT_DIR = Path("screenshots")


class SessionExpired(Exception):
    pass


class BlockedBySite(Exception):
    pass


@contextmanager
def naukri_page():
    """Open a browser with the saved session. Saves the refreshed session on exit."""
    if not Path(STATE_FILE).exists():
        raise SessionExpired(f"{STATE_FILE} not found. Run `python login_once.py` first.")
    headless = os.getenv("HEADLESS", "1") != "0"
    channel = os.getenv("BROWSER_CHANNEL", "chrome").strip().lower() or "chrome"
    if channel in ("bundled", "chromium", "playwright", "none", "0"):
        channel = None
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=headless,
            channel=channel,
            args=["--disable-blink-features=AutomationControlled"],
        )
        ctx_kwargs = {
            "storage_state": STATE_FILE,
            "viewport": {"width": 1366, "height": 850},
            "locale": "en-IN",
        }
        if headless:
            # Naukri's CDN (Akamai) 403s any UA containing "HeadlessChrome".
            # Mask it with a normal UA matching the real browser version.
            ver = browser.version or "0.0.0.0"
            ctx_kwargs["user_agent"] = (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                f"(KHTML, like Gecko) Chrome/{ver} Safari/537.36"
            )
        context = browser.new_context(**ctx_kwargs)
        page = context.new_page()
        page.set_default_timeout(20_000)
        try:
            yield page
        finally:
            try:
                context.storage_state(path=STATE_FILE)
            except Exception:
                pass
            browser.close()


def screenshot(page, tag: str) -> str:
    SHOT_DIR.mkdir(exist_ok=True)
    path = SHOT_DIR / f"{datetime.now():%Y%m%d-%H%M%S}-{tag}.png"
    try:
        page.screenshot(path=str(path), full_page=True)
    except Exception:
        pass
    return str(path)


def open_profile(page):
    page.goto(S.PROFILE_URL, wait_until="domcontentloaded")
    page.wait_for_load_state("networkidle")
    if "login" in page.url.lower() or page.locator(S.LOGIN_MARKER).count() > 0:
        raise SessionExpired("Naukri session expired. Re-run `python login_once.py`.")
    try:
        body = page.locator("body").first.inner_text(timeout=5_000)
    except Exception:
        body = ""
    if "errors_edgesuite.net" in body or "Access Denied" in body:
        screenshot(page, "blocked")
        raise BlockedBySite(
            "Naukri's CDN (Akamai) returned an Access Denied page. "
            "This browser/IP is blocked - retrying now makes it worse. "
            "Wait a while, switch network, or run `python login_once.py` from a normal browser session."
        )


def read_name(page) -> str:
    open_profile(page)
    loc = page.locator(S.NAME_DISPLAY).first
    try:
        loc.wait_for(state="visible")
    except Exception:
        screenshot(page, "read-fail")
        raise
    return loc.inner_text().strip()


def set_name(page, new_name: str) -> None:
    open_profile(page)
    page.locator(S.NAME_EDIT_BUTTON).first.click()
    field = page.locator(S.NAME_INPUT).first
    field.wait_for(state="visible")
    field.fill(new_name)
    page.locator(S.SAVE_BUTTON).first.click()
    page.wait_for_load_state("networkidle")
