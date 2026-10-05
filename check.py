from playwright.sync_api import sync_playwright
import naukri_selectors as S

with sync_playwright() as p:
    b = p.chromium.launch(headless=False)
    ctx = b.new_context(storage_state="state.json")
    page = ctx.new_page()
    page.goto(S.PROFILE_URL)
    page.wait_for_timeout(6000)
    print("URL:", page.url)
    for name in ["NAME_DISPLAY", "NAME_EDIT_BUTTON"]:
        sel = getattr(S, name)
        n = page.locator(sel).count()
        print(f"{name}: {n} match(es)")
        if n:
            print("   first text:", page.locator(sel).first.inner_text()[:60])
    input("Press Enter to close the browser...")
    b.close()