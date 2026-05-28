import pytest
from fastapi import HTTPException

from app.auth import dependencies


@pytest.mark.asyncio
async def test_get_current_user_allows_local_fallback_when_enabled(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(dependencies.settings, "allow_dev_auth_fallback", True)

    current_user = await dependencies.get_current_user(credentials=None, lead_intelligence_key=None)

    assert current_user.user_id == "local-dev-user"


@pytest.mark.asyncio
async def test_get_current_user_requires_auth_when_local_fallback_disabled(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(dependencies.settings, "allow_dev_auth_fallback", False)

    with pytest.raises(HTTPException) as exc_info:
        await dependencies.get_current_user(credentials=None, lead_intelligence_key=None)

    assert exc_info.value.status_code == 401
