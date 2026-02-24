"""HashiCorp Vault client wrapper for secrets management."""

import logging
import os
from typing import Any

logger = logging.getLogger(__name__)


def get_vault_client():
    """Get configured Vault client, or None if not available."""
    try:
        import hvac
    except ImportError:
        logger.info("hvac not installed, Vault integration disabled")
        return None

    vault_addr = os.getenv("VAULT_ADDR", "")
    vault_token = os.getenv("VAULT_TOKEN", "")

    if not vault_addr or not vault_token:
        logger.info("VAULT_ADDR/VAULT_TOKEN not set, Vault integration disabled")
        return None

    client = hvac.Client(url=vault_addr, token=vault_token)

    try:
        if not client.is_authenticated():
            logger.warning("Vault authentication failed")
            return None
    except Exception as e:
        logger.warning("Vault connection failed: %s", e)
        return None

    return client


def read_vault_secrets(
    path: str = "fleetcore",
    mount_point: str = "secret",
) -> dict[str, Any]:
    """Read secrets from Vault KV v2 engine.

    Returns dict of key-value secrets, or empty dict on failure.
    """
    client = get_vault_client()
    if not client:
        return {}

    try:
        response = client.secrets.kv.v2.read_secret_version(
            path=path,
            mount_point=mount_point,
        )
        secrets = response["data"]["data"]
        logger.info("Loaded %d secrets from Vault (%s/%s)", len(secrets), mount_point, path)
        return secrets
    except Exception as e:
        logger.warning("Failed to read Vault secrets: %s", e)
        return {}


def inject_vault_secrets_to_env() -> int:
    """Load secrets from Vault and inject into environment variables.

    Only sets env vars that are not already defined, preserving
    explicit environment variable overrides.

    Returns the number of secrets injected.
    """
    secrets = read_vault_secrets()
    injected = 0
    for key, value in secrets.items():
        if key not in os.environ:
            os.environ[key] = str(value)
            injected += 1
    if injected:
        logger.info("Injected %d Vault secrets into environment", injected)
    return injected
