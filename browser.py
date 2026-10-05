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


@contextmanager
def naukri_page():
    """Open a browser with the saved session. Saves the refreshed session on exit."""
    if not Path(STATE_FILE).exists():
        raise SessionExpired(f"{STATE_FILE} not found. Run `python login_once.py` first.")
    headless = os.getenv("HEADLESS", "1") != "0"
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        context = browser.new_context(
            storage_state=STATE_FILE,
            viewport={"width": 1366, "height": 850},
        )
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


def read_name(page) -> str:
    open_profile(page)
    loc = page.locator(S.NAME_DISPLAY).first
    loc.wait_for(state="visible")
    return loc.inner_text().strip()


def set_name(page, new_name: str) -> None:
    open_profile(page)
    page.locator(S.NAME_EDIT_BUTTON).first.click()
    field = page.locator(S.NAME_INPUT).first
    field.wait_for(state="visible")
    field.fill(new_name)
    page.locator(S.SAVE_BUTTON).first.click()
    page.wait_for_load_state("networkidle")
