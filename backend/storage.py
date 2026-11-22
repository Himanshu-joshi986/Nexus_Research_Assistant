import os
import json
import uuid
from datetime import datetime
from config import (
    ADMIN_NAME,
    ADMIN_PASSWORD,
    ADMIN_USERNAME,
    REPORTS_FILE,
    USERS_FILE,
)


def _default_data(path):
    if path == USERS_FILE:
        if not ADMIN_USERNAME or not ADMIN_PASSWORD:
            raise RuntimeError(
                "Set ADMIN_USERNAME and ADMIN_PASSWORD to initialize the admin account."
            )
        return {
            "users": [{
                "id": "u1",
                "username": ADMIN_USERNAME,
                "password": ADMIN_PASSWORD,
                "name": ADMIN_NAME,
                "created_at": datetime.utcnow().isoformat(),
            }]
        }
    demo_reports_file = os.path.join(os.path.dirname(path), "demo_reports.json")
    try:
        with open(demo_reports_file, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"reports": []}


def _read(path):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        data = _default_data(path)
        _write(path, data)
        return data


def _write(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, default=str)


# ---------- Users ----------
def get_user(username: str, password: str):
    users = _read(USERS_FILE)["users"]
    return next((u for u in users if u["username"] == username and u["password"] == password), None)


# ---------- Reports ----------
def save_report(report: dict) -> str:
    data = _read(REPORTS_FILE)
    report["id"] = str(uuid.uuid4())
    report["created_at"] = datetime.utcnow().isoformat()
    data["reports"].append(report)
    _write(REPORTS_FILE, data)
    return report["id"]


def get_reports(user_id: str = None):
    reports = _read(REPORTS_FILE)["reports"]
    if user_id:
        reports = [r for r in reports if r.get("user_id") == user_id]
    return sorted(reports, key=lambda x: x.get("created_at", ""), reverse=True)


def get_report(report_id: str):
    return next((r for r in _read(REPORTS_FILE)["reports"] if r["id"] == report_id), None)


def delete_report(report_id: str):
    """Remove a report and return it (or None if it did not exist)."""
    data = _read(REPORTS_FILE)
    removed = next((r for r in data["reports"] if r["id"] == report_id), None)
    data["reports"] = [r for r in data["reports"] if r["id"] != report_id]
    _write(REPORTS_FILE, data)
    return removed
