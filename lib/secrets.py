import os
from functools import cache
from pathlib import Path
from typing import Any

import hvac

from globals import files_dir

CA_CERT = files_dir / "house-ca.crt"


@cache
def get_vault_client() -> hvac.Client:
    client = hvac.Client(
        url=os.environ.get("VAULT_ADDR", "http://127.0.0.1:8200"),
        token=os.environ.get("VAULT_TOKEN"),
        verify=str(CA_CERT),
    )
    if not client.is_authenticated():
        raise RuntimeError(
            "Vault authentication failed. Check VAULT_ADDR and VAULT_TOKEN."
        )
    return client


@cache
def get_vault_secret(path: str, mount_point: str = "secrets") -> dict[str, Any]:
    client = get_vault_client()
    # Assumes KV v2 secrets engine
    response = client.secrets.kv.v2.read_secret_version(
        path=path,
        mount_point=mount_point,
    )
    return response["data"]["data"]


def read_secret(path: str, key: str | None = None):
    _path = Path(path)
    mount_point, secret_path = _path.parts[0], Path(*_path.parts[1:])
    res = get_vault_secret(secret_path, mount_point=mount_point)
    return res[key] if key is not None else res
