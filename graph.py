"""LangGraph workflow: read name -> toggle trailing '.' -> save -> verify -> notify."""
import os
from typing import Optional, TypedDict

from langgraph.graph import END, START, StateGraph

import browser
import notify

MAX_ATTEMPTS = int(os.getenv("MAX_ATTEMPTS", "3"))


class State(TypedDict, total=False):
    current_name: str
    target_name: str
    verified_name: str
    attempts: int
    error: Optional[str]
    status: str  # "ok" | "failed"


def next_name(current: str) -> str:
    """'jangir' -> 'jangir.'   and   'jangir.' -> 'jangir'"""
    return current.rstrip(".") if current.endswith(".") else current + "."


# ---------- nodes ----------
def read_current_name(state: State) -> State:
    try:
        with browser.naukri_page() as page:
            name = browser.read_name(page)
            return {"current_name": name, "attempts": 0, "error": None}
    except Exception as e:
        return {"error": f"read failed: {e}", "status": "failed", "attempts": MAX_ATTEMPTS}


def decide_next(state: State) -> State:
    return {"target_name": next_name(state["current_name"])}


def update_name(state: State) -> State:
    attempts = state.get("attempts", 0) + 1
    try:
        with browser.naukri_page() as page:
            try:
                browser.set_name(page, state["target_name"])
            except Exception:
                browser.screenshot(page, f"update-fail-{attempts}")
                raise
        return {"attempts": attempts, "error": None}
    except (browser.SessionExpired, browser.BlockedBySite) as e:
        return {"attempts": MAX_ATTEMPTS, "error": str(e)}  # retrying won't help
    except Exception as e:
        return {"attempts": attempts, "error": f"update failed: {e}"}


def verify(state: State) -> State:
    try:
        with browser.naukri_page() as page:
            name = browser.read_name(page)
        ok = name == state["target_name"]
        return {"verified_name": name, "status": "ok" if ok else "pending"}
    except Exception as e:
        return {"error": f"verify failed: {e}", "status": "pending"}


def notify_success(state: State) -> State:
    notify.send(f"✅ Naukri name updated: '{state['current_name']}' → '{state['verified_name']}'")
    return {"status": "ok"}


def notify_failure(state: State) -> State:
    notify.send(f"❌ Naukri update failed after {state.get('attempts', 0)} attempt(s). "
                f"Last error: {state.get('error') or 'name did not change'}")
    return {"status": "failed"}


# ---------- routing ----------
def after_read(state: State) -> str:
    return "failed" if state.get("status") == "failed" else "go"

EXPECTED = os.getenv("EXPECTED_NAME_CONTAINS", "Chetan")


def read_current_name(state: State) -> State:
    try:
        with browser.naukri_page() as page:
            name = browser.read_name(page)
        if EXPECTED.lower() not in name.lower():
            return {"error": f"Unexpected name read: '{name}'. Refusing to edit.",
                    "status": "failed", "attempts": MAX_ATTEMPTS}
        return {"current_name": name, "attempts": 0, "error": None}
    except Exception as e:
        return {"error": f"read failed: {e}", "status": "failed", "attempts": MAX_ATTEMPTS}

def after_verify(state: State) -> str:
    if state.get("status") == "ok":
        return "success"
    return "retry" if state.get("attempts", 0) < MAX_ATTEMPTS else "failure"


def build():
    g = StateGraph(State)
    g.add_node("read_current_name", read_current_name)
    g.add_node("decide_next", decide_next)
    g.add_node("update_name", update_name)
    g.add_node("verify", verify)
    g.add_node("notify_success", notify_success)
    g.add_node("notify_failure", notify_failure)

    g.add_edge(START, "read_current_name")
    g.add_conditional_edges("read_current_name", after_read,
                            {"go": "decide_next", "failed": "notify_failure"})
    g.add_edge("decide_next", "update_name")
    g.add_edge("update_name", "verify")
    g.add_conditional_edges("verify", after_verify,
                            {"success": "notify_success", "retry": "update_name",
                             "failure": "notify_failure"})
    g.add_edge("notify_success", END)
    g.add_edge("notify_failure", END)
    return g.compile()
