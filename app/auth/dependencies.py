from dataclasses import dataclass

from fastapi import Depends, Header, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.auth.jwt import verify_supabase_jwt
from app.core.config import settings

security = HTTPBearer(auto_error=False)


@dataclass(frozen=True)
class CurrentUser:
    user_id: str
    tenant_id: str | None = None
    email: str | None = None


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    lead_intelligence_key: str | None = Header(default=None, alias="x-lead-intelligence-key"),
) -> CurrentUser:
    if (
        settings.lead_intelligence_api_key
        and lead_intelligence_key
        and lead_intelligence_key == settings.lead_intelligence_api_key
    ):
        return CurrentUser(user_id="service:lead-intelligence", tenant_id="local-test")

    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing bearer token")

    claims = verify_supabase_jwt(credentials.credentials)
    return CurrentUser(
        user_id=claims["sub"],
        tenant_id=claims.get("app_metadata", {}).get("tenant_id"),
        email=claims.get("email"),
    )
