# Naukri Profile Auto-Update Agent

This project automates a small but useful Naukri profile activity check: it updates your profile name by toggling a trailing period (for example, `jangir` -> `jangir.` -> `jangir`) so the profile looks recently updated.

It uses a LangGraph workflow, Playwright browser automation, and optional Telegram notifications.

## What the agent does

- Reads the current name from your Naukri profile
- Verifies the name matches an expected format before editing
- Toggles the profile name between two states
- Validates that the change was applied
- Retries automatically on failures
- Sends a Telegram message when it succeeds or fails
- Saves browser screenshot artifacts when an update attempt fails

## Why this exists

Naukri profile activity can matter for visibility and freshness. This project is a personal automation helper for keeping a profile in a recently updated state without manually editing it every day.

## Project structure

- `main.py` — single-run entry point
- `loop.py` — periodic runner for repeated automation loops
- `graph.py` — LangGraph workflow that controls the update process
- `browser.py` — Playwright browser helpers and session management
- `naukri_selectors.py` — selectors used to locate name fields on the Naukri profile page
- `login_once.py` — one-time login flow to save a browser session
- `notify.py` — Telegram notification helper
- `.env.example` — environment variable template
- `requirements.txt` — Python dependencies
- `state.json` — saved browser session generated after login

## Requirements

- Python 3.10+
- Chromium/Playwright browser support
- A valid Naukri account session

## Setup

1. Create and activate a virtual environment (optional but recommended):

```bash
python -m venv .venv
. .venv\Scripts\activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Install the Playwright browser runtime:

```bash
playwright install chromium
```

4. Copy the sample environment file:

```bash
copy .env.example .env
```

5. Log in once to save a browser session:

```bash
python login_once.py
```

This opens a browser window for manual login and saves the session into `state.json`.

## Configuration

Edit `.env` and update the values as needed:

```env
NAUKRI_STATE_FILE=state.json
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=
MAX_RANDOM_DELAY_MIN=30
MAX_ATTEMPTS=3
HEADLESS=1
```

### Environment variables

- `NAUKRI_STATE_FILE` — path to the saved browser session file
- `TELEGRAM_BOT_TOKEN` — Telegram bot token for notifications
- `TELEGRAM_CHAT_ID` — Telegram chat ID for sending alerts
- `MAX_RANDOM_DELAY_MIN` — random delay before each run, in minutes
- `MAX_ATTEMPTS` — retry count for failed update attempts
- `HEADLESS` — set to `0` for visible browser debugging

## Required selector setup

Open `naukri_selectors.py` and confirm the selectors match your current Naukri profile page. The file contains the selectors used for:

- profile URL
- name display element
- edit button
- name input field
- save button
- login detection marker

If Naukri changes its page structure, update these selectors before running the agent.

## Running the bot

### One-time test run

```bash
HEADLESS=0 MAX_RANDOM_DELAY_MIN=0 python main.py
```

Run it twice to confirm the profile name toggles correctly.

### Repeated loop

```bash
python loop.py
```

This runs the workflow in a loop with a delay between attempts.

## Workflow behavior

The graph is structured like this:

```text
read_current_name -> decide_next -> update_name -> verify -> notify_success
                                        ^----- retry ------|
                                                     \-> notify_failure
```

## Troubleshooting

### Session expired

If the browser session is no longer valid:

```bash
python login_once.py
```

Then refresh the saved session in your environment or secret manager if you are using automation in GitHub Actions.

### Selector errors

- Check the screenshot in the `screenshots` folder
- Update selectors in `naukri_selectors.py`
- Re-run the script after fixing the selectors

### Name toggle rejected by Naukri

Some Naukri flows may reject a trailing `.` in a name. If that happens, modify the `next_name()` function in `graph.py` to use a different change pattern such as capitalization or another safe variation.

## GitHub Actions usage

This project can be scheduled in a private repository.

1. Export the browser session:

```bash
base64 -w0 state.json
```

On macOS/Linux:

```bash
base64 state.json
```

2. Add the resulting value as a GitHub Actions secret named `NAUKRI_STATE_B64`.
3. Optionally add `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID`.
4. Trigger the workflow manually to validate it.

## Notes

- This project is designed for personal automation and should be used in compliance with the platform's terms and your own account policies.
- Use a private repository or a secured environment when storing session data.
- Keep selectors and automation logic updated if Naukri changes its UI.

## License

This project does not currently declare a license. Use it responsibly and confirm compliance with your local laws and the Naukri platform terms before deploying it in production or shared environments.

$env:HEADLESS="0"; $env:MAX_RANDOM_DELAY_MIN="0"; python main.py

$env:HEADLESS="1"; $env:INTERVAL_MINUTES="5"; $env:MAX_RANDOM_DELAY_MIN="0"; python loop.py
