from playwright.sync_api import sync_playwright
import naukri_selectors as S

with sync_playwright() as p:
    b = p.chromium.launch(headless=False)
    ctx = b.new_context(storage_state="state.json")
    page = ctx.new_page()
    page.goto(S.PROFILE_URL)
    page.wait_for_timeout(6000)
    el = page.get_by_text("Chetan Kumar Jangir", exact=False).first
    print("TAG/CLASS:", el.evaluate("e => e.tagName + ' | ' + e.className"))
    print("PARENT HTML:")
    print(el.evaluate("e => e.parentElement.outerHTML")[:1500])
    b.close()