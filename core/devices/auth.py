import jwt
from datetime import datetime, timedelta, timezone
import secrets
from typing import Optional
import uuid

# In a real app this should be securely loaded/generated and persisted
# We keep it ephemeral for V2 sandbox context.
_JWT_SECRET = secrets.token_urlsafe(32)

def issue_device_token(device_id: str, session_id: str, duration_hours: int = 24) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": device_id,
        "sid": session_id,
        "jti": str(uuid.uuid4()),
        "aud": "mark_v2_core",
        "iat": now,
        "exp": now + timedelta(hours=duration_hours),
        "iss": "mark_v2_core"
    }
    return jwt.encode(payload, _JWT_SECRET, algorithm="HS256")

def validate_device_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(
            token, 
            _JWT_SECRET, 
            algorithms=["HS256"], 
            issuer="mark_v2_core", 
            audience="mark_v2_core"
        )
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
