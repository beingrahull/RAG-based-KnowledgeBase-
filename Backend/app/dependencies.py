from fastapi import Cookie, HTTPException

from app.models.user import User
from app.utils.security import decode_token


async def get_current_user(
    access_token: str | None = Cookie(default=None, alias="Access_Token"),
) -> User:
    if not access_token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        payload = decode_token(access_token)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    user = await User.get(payload["sub"])
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user