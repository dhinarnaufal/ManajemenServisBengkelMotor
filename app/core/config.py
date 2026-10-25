import os

DEFAULT_API_KEY = "bengkel-dev-key"
DEFAULT_MAX_ACTIVE_SERVICES = 3


def get_api_key() -> str:
    """API key bisa diganti lewat environment variable BENGKEL_API_KEY."""
    return os.getenv("BENGKEL_API_KEY", DEFAULT_API_KEY)


def get_max_active_services() -> int:
    """Batas N servis aktif per mekanik (env: BENGKEL_MAX_ACTIVE_SERVICES)."""
    raw = os.getenv("BENGKEL_MAX_ACTIVE_SERVICES")
    if raw is None:
        return DEFAULT_MAX_ACTIVE_SERVICES
    try:
        value = int(raw)
    except ValueError:
        return DEFAULT_MAX_ACTIVE_SERVICES
    return value if value >= 1 else DEFAULT_MAX_ACTIVE_SERVICES
