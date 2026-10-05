import os
import random
import sys
import time

from dotenv import load_dotenv

load_dotenv()

import graph  # noqa: E402  (after load_dotenv so env vars are visible)


def main() -> int:
    max_delay = int(os.getenv("MAX_RANDOM_DELAY_MIN", "0"))
    if max_delay > 0:
        wait = random.randint(0, max_delay * 60)
        print(f"Sleeping {wait}s before running...")
        time.sleep(wait)

    result = graph.build().invoke({})
    return 0 if result.get("status") == "ok" else 1


if __name__ == "__main__":
    sys.exit(main())
