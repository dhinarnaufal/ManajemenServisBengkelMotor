from typing import Optional

from fastapi import Header, HTTPException, status

from app.core.config import get_api_key


def verify_api_key(x_api_key: Optional[str] = Header(default=None)) -> str:
    if x_api_key != get_api_key():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key tidak ada atau tidak valid.",
        )
    return "authorized-client"
