from __future__ import annotations

from typing import Dict

from fused._auth import CREDENTIALS
from fused.api.api import FusedAPI


def context_get_user_email() -> str:
    api = FusedAPI()
    return api._whoami()["email"]


def context_get_auth_header(*, missing_ok: bool = False) -> Dict[str, str]:
    if CREDENTIALS.has_credentials() or not missing_ok:
        return {"Authorization": f"Bearer {CREDENTIALS.credentials.access_token}"}
    else:
        # Not logged in and that's OK
        return {}
