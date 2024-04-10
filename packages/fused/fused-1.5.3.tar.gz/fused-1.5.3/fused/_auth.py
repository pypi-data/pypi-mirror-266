from __future__ import annotations

import base64
import hashlib
import json
import secrets
import webbrowser
from datetime import datetime, timedelta, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from textwrap import dedent
from threading import RLock
from typing import Dict, Optional
from urllib.parse import parse_qs, urlencode, urlparse

import requests
from pydantic import BaseModel

from fused._options import options as OPTIONS

# The authorize URL is used for the initial login flow. This is intended to be opened in
# the user's web browser for them to sign in.
AUTHORIZE_URL = "https://dev-tjcykxcetrz6bps6.us.auth0.com/authorize"

# The token url is used for programmatic access to generate access and refresh tokens
OAUTH_TOKEN_URL = "https://dev-tjcykxcetrz6bps6.us.auth0.com/oauth/token"

LOGOUT_URL = "https://dev-tjcykxcetrz6bps6.us.auth0.com/oidc/logout"

# The client id, client secret, and audience identifies a specific application and API
CLIENT_ID = "CXiwKZQmmyo0rqXZY7pzBgfsF7AL2A9l"
CLIENT_SECRET = "FVNz012KgNmqITYnCCOM8Q1Nt81W_DO4SeCRgVsftREKTWpzZU522nia5TdSNv8h"
AUDIENCE = "fused-python-api"

# This redirect uri is passed to the authorize URL as a url parameter. This localhost
# uri is used to intercept the "code" generated from the authorization
LOCAL_REDIRECT_URI = "http://localhost:3000"

# The offline_access scope is necessary to be able to fetch refresh tokens
# The other scopes are useful to access identifying information in the retrieved JWT
SCOPES = ["openid", "email", "name", "offline_access"]

# The path where the refresh token is saved on disk
CREDENTIALS_PATH = Path("~/.fused/credentials").expanduser()


_refresh_token_lock = RLock()


class Credentials(BaseModel):
    """A dataclass representation of OAuth2 credentials"""

    access_token: str
    refresh_token: str
    id_token: str
    scope: str
    expires_in: int
    token_type: str
    expires_at: datetime

    @classmethod
    def authenticate(cls) -> Credentials:
        token_dict = authenticate()
        credentials = cls(**token_dict)
        credentials.save_to_disk()
        return credentials

    @classmethod
    def from_disk(cls) -> Credentials:
        if CREDENTIALS_PATH.exists():
            return Credentials.parse_file(CREDENTIALS_PATH, content_type="json")

        raise ValueError()

    @classmethod
    def from_disk_or_authenticate(cls) -> Credentials:
        try:
            return cls.from_disk()
        except ValueError:
            return cls.authenticate()

    def save_to_disk(self) -> None:
        if OPTIONS.save_user_settings:
            CREDENTIALS_PATH.parent.mkdir(parents=True, exist_ok=True)
            with open(CREDENTIALS_PATH, "w") as f:
                f.write(self.json())

    @classmethod
    def from_token_response(cls, token_dict: Dict) -> Credentials:
        # Add an expires_at field in the dictionary for next time it's loaded
        token_dict["expires_at"] = (
            datetime.now(timezone.utc) + timedelta(seconds=token_dict["expires_in"] - 1)
        ).isoformat()

        credentials = cls(**token_dict)
        credentials.save_to_disk()

        return credentials

    def refresh_if_needed(self) -> Credentials:
        # Do not call the refresh token from multiple threads at once. If this happens,
        # the rate limit can accidentally be exceeded.
        # This could be optimized with double-checked locking, but the Wikipedia page
        # points out there could be an issue with the object being in a partially updated
        # state.
        # https://en.wikipedia.org/wiki/Double-checked_locking
        with _refresh_token_lock:
            if self.expires_at < datetime.now(timezone.utc):
                # Credentials are expired; we need to refresh
                token_dict = refresh_token(self.refresh_token)
                new_credentials = Credentials(**token_dict)
                self.__dict__.update(new_credentials.__dict__)

        return self


class MaybeInitializedCredentials:
    """OAuth2 credentials that may or may not have been initialized."""

    _credentials: Optional[Credentials] = None

    def __init__(self) -> None:
        try:
            self._credentials = Credentials.from_disk()
        except ValueError:
            auth_msg = """\
                Credentials not found on disk. Authenticate with:

                from fused import NotebookCredentials
                credentials = NotebookCredentials()
            """
            print(dedent(auth_msg))

    def initialize(self) -> None:
        """Force initialization of credentials."""
        _ = self.credentials

    @property
    def credentials(self) -> Credentials:
        """
        Retrieve valid credentials, initializing them or authenticating from scratch if needed.
        """
        credentials = self._credentials or Credentials.from_disk_or_authenticate()
        credentials = credentials.refresh_if_needed()
        self._credentials = credentials
        return credentials

    def set_credentials(self, credentials: Credentials) -> None:
        assert isinstance(credentials, Credentials)
        self._credentials = credentials

    def has_credentials(self) -> bool:
        credentials = None
        try:
            credentials = self._credentials or Credentials.from_disk()
        except ValueError:
            pass
        return credentials is not None

    @property
    def _authorization_header(self):
        """Access the Authorization HTTP header of these credentials."""
        credentials = self.credentials
        return {"Authorization": f"Bearer {credentials.access_token}"}


CREDENTIALS: MaybeInitializedCredentials = MaybeInitializedCredentials()
"""Global credentials."""


# TODO: remove some of these functions below
def authenticate():
    print(
        "Existing credentials not found on disk: Please check your browser to log in."
    )
    code_verifier = secrets.token_urlsafe(48)
    code_challenge = get_code_challenge(code_verifier)

    params = {
        "audience": AUDIENCE,
        "scope": " ".join(SCOPES),
        "response_type": "code",
        "client_id": CLIENT_ID,
        "redirect_uri": LOCAL_REDIRECT_URI,
        "code_challenge_method": "S256",
        "code_challenge": code_challenge,
    }
    url = f"{AUTHORIZE_URL}?{urlencode(params)}"
    code = handle_redirect(url)

    token_data = {
        "client_id": CLIENT_ID,
        "grant_type": "authorization_code",
        "audience": AUDIENCE,
        "client_secret": CLIENT_SECRET,
        "code": code,
        "redirect_uri": LOCAL_REDIRECT_URI,
        "code_verifier": code_verifier,
    }
    token_response = requests.post(
        OAUTH_TOKEN_URL, json=token_data, timeout=OPTIONS.request_timeout
    )
    token_response.raise_for_status()
    token_dict = token_response.json()

    # Add an expires_at field in the dictionary for next time it's loaded
    token_dict["expires_at"] = (
        datetime.now(timezone.utc) + timedelta(seconds=token_dict["expires_in"] - 1)
    ).isoformat()

    save_token_to_disk(token_dict)
    return token_dict


def logout():
    """Open the user's browser to the Auth0 logout page."""
    webbrowser.open(LOGOUT_URL)


def save_token_to_disk(token: dict):
    if OPTIONS.save_user_settings:
        CREDENTIALS_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(CREDENTIALS_PATH, "w") as f:
            json.dump(token, f)


def delete_token_from_disk():
    CREDENTIALS_PATH.unlink(missing_ok=True)


def get_code_challenge(code_verifier: str) -> str:
    """Take an input string and hash it to generate a challenge string

    Refer to https://auth0.com/docs/get-started/authentication-and-authorization-flow/call-your-api-using-the-authorization-code-flow-with-pkce
    """
    code_challenge_digest = hashlib.sha256(code_verifier.encode("utf-8")).digest()
    code_challenge = base64.urlsafe_b64encode(code_challenge_digest).decode("utf-8")
    return code_challenge.replace("=", "")


def handle_redirect(authorize_url: str) -> str:
    """Open the authorization url and intercept its redirect

    The redirection from the `/authorize` endpoint includes a code that can be used
    against the `/oauth/token` endpoint to fetch a refresh and access token.
    """
    code: Optional[str] = None

    # TODO: this request handler should also support when a user declines the auth flow
    class RequestHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            nonlocal code

            query_string = urlparse(self.path).query
            parsed_qs = parse_qs(query_string)

            assert len(parsed_qs["code"]) == 1
            code = parsed_qs["code"][0]

            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()

            text = "Success! You can now close this tab and return to Python."
            self.wfile.write(text.encode())

        def log_message(self, format, *args):
            # This is overwritten to prevent the server from logging requests to the
            # console
            return

    # TODO: support other ports if 3000 is already taken?
    server = HTTPServer(("localhost", 3000), RequestHandler)
    webbrowser.open(authorize_url)

    # Note that this only handles _one_ request, but that's all it should need
    server.handle_request()

    assert code is not None
    return code


def refresh_token(refresh_token: str):
    """Generate a new access_token using a refresh token"""
    token_data = {
        "client_id": CLIENT_ID,
        "grant_type": "refresh_token",
        "client_secret": CLIENT_SECRET,
        # TODO: Is this needed? This won't be right for notebook
        "redirect_uri": LOCAL_REDIRECT_URI,
        "refresh_token": refresh_token,
    }
    token_response = requests.post(
        OAUTH_TOKEN_URL, json=token_data, timeout=OPTIONS.request_timeout
    )
    token_response.raise_for_status()
    token_dict = token_response.json()

    # Add an expires_at field in the dictionary for next time it's loaded
    token_dict["expires_at"] = (
        datetime.now(timezone.utc) + timedelta(seconds=token_dict["expires_in"] - 1)
    ).isoformat()
    token_dict["refresh_token"] = refresh_token

    save_token_to_disk(token_dict)
    return token_dict
