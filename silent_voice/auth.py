"""Firebase email/password authentication over the Identity Toolkit REST API.

The firebase-admin SDK is server-side only: it has no
``sign_in_with_email_and_password`` and cannot act as a user on the client.
The desktop app therefore talks to the same endpoint the Firebase JS SDK uses,
which keeps the behaviour (login, sign-up, error codes) intact.

Credentials come from ``.env``; nothing is hardcoded here.
"""

from __future__ import annotations

from dataclasses import dataclass

import requests

from silent_voice import config

SIGN_IN_URL = "https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword"
SIGN_UP_URL = "https://identitytoolkit.googleapis.com/v1/accounts:signUp"


class AuthError(Exception):
    """Raised with a human-readable message when Firebase rejects a request."""

    FRIENDLY = {
        "EMAIL_NOT_FOUND": "No account found for that email address.",
        "INVALID_PASSWORD": "That password is incorrect.",
        "INVALID_LOGIN_CREDENTIALS": "Email or password is incorrect.",
        "EMAIL_EXISTS": "An account with that email already exists.",
        "INVALID_EMAIL": "That email address is not valid.",
        "WEAK_PASSWORD": "Please use at least 6 characters for the password.",
        "MISSING_PASSWORD": "Please enter a password.",
        "TOO_MANY_ATTEMPTS_TRY_LATER": "Too many attempts. Try again in a few minutes.",
        "OPERATION_NOT_ALLOWED": "Email sign-in is disabled for this project.",
        "API_KEY_INVALID": "The Firebase API key is missing or invalid.",
    }

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


@dataclass(frozen=True)
class Session:
    """What the UI needs to know about a signed-in user."""

    email: str
    id_token: str
    refresh_token: str
    local_id: str


def is_configured() -> bool:
    return bool(config.FIREBASE_CONFIG["api_key"])


def _require_config() -> None:
    if not is_configured():
        raise AuthError(
            "Firebase is not configured. Copy .env.example to .env and set "
            "FIREBASE_API_KEY, then restart the app."
        )


def _post(url: str, email: str, password: str) -> Session:
    _require_config()

    payload = {
        "email": email.strip(),
        "password": password,
        "returnSecureToken": True,
    }
    try:
        response = requests.post(
            url,
            json=payload,
            params={"key": config.FIREBASE_CONFIG["api_key"]},
            timeout=15,
        )
    except requests.RequestException as exc:
        raise AuthError("Cannot reach Firebase. Check your connection.") from exc

    body = response.json() if response.content else {}

    if response.status_code != 200:
        reason = (
            body.get("error", {})
            .get("message", "UNKNOWN")
            .split(" :")[0]
        )
        raise AuthError(
            AuthError.FRIENDLY.get(reason, f"Firebase rejected the request ({reason}).")
        )

    return Session(
        email=body.get("email", email),
        id_token=body.get("idToken", ""),
        refresh_token=body.get("refreshToken", ""),
        local_id=body.get("localId", ""),
    )


def sign_in(email: str, password: str) -> Session:
    """Sign an existing user in."""
    if not email.strip() or not password:
        raise AuthError("Please enter both email and password.")
    return _post(SIGN_IN_URL, email, password)


def sign_up(email: str, password: str) -> Session:
    """Create an account and sign it in."""
    if not email.strip() or not password:
        raise AuthError("Please enter both email and password.")
    return _post(SIGN_UP_URL, email, password)
