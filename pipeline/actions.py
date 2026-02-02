import os
import json
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ACTIONS_DIR = os.path.join(BASE_DIR, "data", "actions")
os.makedirs(ACTIONS_DIR, exist_ok=True)

ACTIONS_LOG = os.path.join(ACTIONS_DIR, "actions_log.jsonl")


def log_action(payload: dict) -> None:
    payload = dict(payload)
    payload["logged_at"] = datetime.utcnow().isoformat()
    with open(ACTIONS_LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=False) + "\n")


def simulate_action(action_name: str, context: dict) -> dict:
    """Safe demo: does not execute anything, only logs."""
    result = {
        "action": action_name,
        "status": "simulated",
        "context": context,
    }
    log_action(result)
    return result


def create_incident_report(alert: dict, assistant: dict) -> str:
    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    path = os.path.join(ACTIONS_DIR, f"incident_{ts}.json")
    report = {
        "created_at": datetime.utcnow().isoformat(),
        "alert": alert,
        "assistant": assistant,
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    log_action({"action": "create_incident_report", "status": "created", "path": path})
    return path
