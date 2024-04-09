import os
import pyqqq.config as c

_api_key = None

def set_api_key(api_key: str):
    global _api_key

    assert api_key is not None, "API key must not be None"
    assert len(api_key) >= 32, "API key must be at least 32 characters long"

    _api_key = api_key


def get_api_key() -> str | None:
    if _api_key:
        return _api_key

    elif c.get_pyqqq_api_key() is not None:
        return c.get_pyqqq_api_key()

    elif os.path.exists(c.get_credential_file_path()):
        with open(c.get_credential_file_path(), "r") as f:
            return f.read().strip()

    return None
