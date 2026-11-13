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


def _read(path):
    try:
        with open(path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        if path == USERS_FILE:
            if not ADMIN_USERNAME or not ADMIN_PASSWORD:
                raise RuntimeError(
                    "Set ADMIN_USERNAME and ADMIN_PASSWORD to initialize the admin account."
                )
            data = {
                "users": [{
                    "id": "u1",
                    "username": ADMIN_USERNAME,
                    "password": ADMIN_PASSWORD,
                    "name": ADMIN_NAME,
                    "created_at": datetime.utcnow().isoformat(),
                }]
            }
        elif path == REPORTS_FILE:
            demo_reports_file = os.path.join(
                os.path.dirname(path), "demo_reports.json"
            )
            try:
                with open(demo_reports_file, "r") as f:
                    data = json.load(f)
            except FileNotFoundError:
                data = {"reports": []}
        else:
            raise
        _write(path, data)
        return data


def _write(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2, default=str)


# ---------- Users ----------
def get_user(username: str, password: str):
    data = _read(USERS_FILE)
    for u in data["users"]:
        if u["username"] == username and u["password"] == password:
            return u
    return None


# ---------- Reports ----------
def save_report(report: dict) -> str:
    data = _read(REPORTS_FILE)
    report["id"] = str(uuid.uuid4())
    report["created_at"] = datetime.utcnow().isoformat()
    data["reports"].append(report)
    _write(REPORTS_FILE, data)
    return report["id"]


def get_reports(user_id: str = None):
    data = _read(REPORTS_FILE)
    reports = data["reports"]
    if user_id:
        reports = [r for r in reports if r.get("user_id") == user_id]
    return sorted(reports, key=lambda x: x.get("created_at", ""), reverse=True)


def get_report(report_id: str):
    data = _read(REPORTS_FILE)
    for r in data["reports"]:
        if r["id"] == report_id:
            return r
    return None


def delete_report(report_id: str):
    data = _read(REPORTS_FILE)
    data["reports"] = [r for r in data["reports"] if r["id"] != report_id]
    _write(REPORTS_FILE, data)

