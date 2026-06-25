"""
api_client.py — Lightweight HTTP client for API-level operations.
Used for test data setup/teardown without going through the UI.
All credentials loaded from environment — never hardcoded.
"""
import os
import logging
import requests
from typing import Any

logger = logging.getLogger(__name__)

BASE_URL = os.environ.get("BASE_URL", "")
API_BASE = BASE_URL.rstrip("/") + "/api"


class KESEFApiClient:
    def __init__(self, email: str, password: str):
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        self._token: str | None = None
        self._email    = email
        self._password = password

    # ── Auth ───────────────────────────────────────────────────────────────
    def login(self) -> "KESEFApiClient":
        resp = self.session.post(f"{API_BASE}/auth/login", json={
            "email":    self._email,
            "password": self._password,
        })
        resp.raise_for_status()
        self._token = resp.json().get("token")
        self.session.headers["Authorization"] = f"Bearer {self._token}"
        logger.info("API login successful for %s", self._email)
        return self

    # ── Deals ──────────────────────────────────────────────────────────────
    def create_deal(self, payload: dict) -> dict:
        return self._post("/deals", payload)

    def fund_deal(self, deal_id: str) -> dict:
        return self._post(f"/deals/{deal_id}/fund", {})

    def get_deal(self, deal_id: str) -> dict:
        return self._get(f"/deals/{deal_id}")

    def delete_deal(self, deal_id: str) -> None:
        """Test cleanup only — removes test data after test run."""
        self._delete(f"/deals/{deal_id}")

    # ── Payments ───────────────────────────────────────────────────────────
    def approve_payment(self, payment_id: str) -> dict:
        return self._post(f"/payments/{payment_id}/approve", {})

    def mark_nsf(self, payment_id: str, reason: str) -> dict:
        return self._post(f"/payments/{payment_id}/nsf", {"reason": reason})

    # ── Clients ────────────────────────────────────────────────────────────
    def get_clients(self, filters: dict | None = None) -> dict:
        return self._get("/clients", params=filters)

    # ── Reports ────────────────────────────────────────────────────────────
    def generate_report(self, report_type: str, from_date: str, to_date: str) -> dict:
        return self._post("/reports/generate", {
            "reportType": report_type,
            "fromDate":   from_date,
            "toDate":     to_date,
        })

    # ── Internal ──────────────────────────────────────────────────────────
    def _get(self, path: str, params: dict | None = None) -> Any:
        resp = self.session.get(f"{API_BASE}{path}", params=params)
        self._log_response(resp)
        resp.raise_for_status()
        return resp.json()

    def _post(self, path: str, payload: dict) -> Any:
        resp = self.session.post(f"{API_BASE}{path}", json=payload)
        self._log_response(resp)
        resp.raise_for_status()
        return resp.json()

    def _delete(self, path: str) -> None:
        resp = self.session.delete(f"{API_BASE}{path}")
        self._log_response(resp)
        resp.raise_for_status()

    def _log_response(self, resp: requests.Response):
        # Log status + URL only — never log response body (may contain sensitive data)
        logger.info("[API] %s %s → %s", resp.request.method, resp.url, resp.status_code)
