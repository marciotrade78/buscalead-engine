import pytest
from fastapi import HTTPException

from app.auth import dependencies


@pytest.mark.asyncio
async def test_get_current_user_allows_local_fallback_when_enabled(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(dependencies.settings, "allow_dev_auth_fallback", True)

    current_user = await dependencies.get_current_user(
        credentials=None,
        lead_intelligence_key=None,
        lead_user_id=None,
        lead_tenant_id=None,
        lead_user_email=None,
    )

    assert current_user.user_id == "local-dev-user"


@pytest.mark.asyncio
async def test_get_current_user_requires_auth_when_local_fallback_disabled(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(dependencies.settings, "allow_dev_auth_fallback", False)

    with pytest.raises(HTTPException) as exc_info:
        await dependencies.get_current_user(
            credentials=None,
            lead_intelligence_key=None,
            lead_user_id=None,
            lead_tenant_id=None,
            lead_user_email=None,
        )

    assert exc_info.value.status_code == 401


@pytest.mark.asyncio
async def test_get_current_user_uses_trusted_headers_with_service_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(dependencies.settings, "lead_intelligence_api_key", "secret")

    current_user = await dependencies.get_current_user(
        credentials=None,
        lead_intelligence_key="secret",
        lead_user_id="user-123",
        lead_tenant_id="tenant-456",
        lead_user_email="user@example.com",
    )

    assert current_user.user_id == "user-123"
    assert current_user.tenant_id == "tenant-456"
    assert current_user.email == "user@example.com"


@pytest.mark.asyncio
async def test_get_current_user_service_key_falls_back_to_service_identity(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(dependencies.settings, "lead_intelligence_api_key", "secret")

    current_user = await dependencies.get_current_user(
        credentials=None,
        lead_intelligence_key="secret",
        lead_user_id=None,
        lead_tenant_id=None,
        lead_user_email=None,
    )

    assert current_user.user_id == "service:lead-intelligence"
    assert current_user.tenant_id == "service"
