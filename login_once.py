"""Run this ONCE on your own machine. Log in manually (solve CAPTCHA/OTP), then
press Enter. Your session is saved to state.json and reused by the agent."""
import os
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

load_dotenv()
STATE_FILE = os.getenv("NAUKRI_STATE_FILE", "state.json")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    ctx = browser.new_context()
    page = ctx.new_page()
    page.goto("https://www.naukri.com/nlogin/login")
    input("Log in in the browser window, wait until you see your profile/home, then press Enter here... ")
    ctx.storage_state(path=STATE_FILE)
    browser.close()
print(f"Saved session to {STATE_FILE}")
