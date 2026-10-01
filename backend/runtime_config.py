"""Runtime settings shared by the FutBud API deployment."""

import os


LOCAL_FRONTEND_ORIGINS = (
    "http://localhost:5173",
    "http://127.0.0.1:5173",
)


def get_allowed_origins() -> list[str]:
    """Return local origins plus configured production frontend origins."""

    configured = os.getenv("FRONTEND_ORIGIN", "")
    production_origins = [
        origin.strip().rstrip("/")
        for origin in configured.split(",")
        if origin.strip()
    ]

    if "*" in production_origins:
        raise RuntimeError(
            "FRONTEND_ORIGIN cannot contain '*' when CORS credentials are enabled."
        )

    return list(dict.fromkeys((*LOCAL_FRONTEND_ORIGINS, *production_origins)))

