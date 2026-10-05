import os
import random
import time

from dotenv import load_dotenv

load_dotenv()

import graph  # noqa: E402

INTERVAL = float(os.getenv("INTERVAL_MINUTES", "5"))
MAX_FAILS = int(os.getenv("MAX_CONSECUTIVE_FAILS", "3"))

app = graph.build()
fails = 0
run = 0

while True:
    run += 1
    print(f"\n--- run {run} ---")
    result = app.invoke({})
    if result.get("status") == "ok":
        fails = 0
    else:
        fails += 1
        if fails >= MAX_FAILS:
            print(f"Stopping after {fails} failed runs in a row.")
            break
    wait = INTERVAL * 60 + random.randint(0, 20)
    print(f"Next run in {wait:.0f}s (Ctrl+C to stop)")
    time.sleep(wait)