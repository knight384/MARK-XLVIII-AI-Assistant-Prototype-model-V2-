import jwt
from datetime import datetime, timedelta, timezone
import secrets
from typing import Optional

# In a real app this should be securely loaded/generated and persisted
_JWT_SECRET = secrets.token_urlsafe(32)

def issue_device_token(device_id: str, duration_hours: int = 24) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": device_id,
        "iat": now,
        "exp": now + timedelta(hours=duration_hours),
        "iss": "mark_xlviii_v2"
    }
    return jwt.encode(payload, _JWT_SECRET, algorithm="HS256")

def validate_device_token(token: str) -> Optional[str]:
    try:
        payload = jwt.decode(token, _JWT_SECRET, algorithms=["HS256"], issuer="mark_xlviii_v2")
        return payload.get("sub")
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
