from __future__ import annotations

import hmac
from datetime import datetime, timedelta, timezone
from typing import Optional

from authlib.integrations.starlette_client import OAuth
from authlib.jose import JsonWebToken
from fastapi import Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from podcast_generator.web.db import get_user, get_user_by_email, create_user

security = HTTPBearer(auto_error=False)

_jwt = JsonWebToken(["HS256"])
_oauth = OAuth()


def init_oauth(cfg):
    if cfg.oauth_google_client_id and cfg.oauth_google_client_secret:
        _oauth.register(
            name="google",
            client_id=cfg.oauth_google_client_id,
            client_secret=cfg.oauth_google_client_secret,
            server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
            client_kwargs={"scope": "openid email profile"},
        )
    if cfg.oauth_github_client_id and cfg.oauth_github_client_secret:
        _oauth.register(
            name="github",
            client_id=cfg.oauth_github_client_id,
            client_secret=cfg.oauth_github_client_secret,
            access_token_url="https://github.com/login/oauth/access_token",
            authorize_url="https://github.com/login/oauth/authorize",
            client_kwargs={"scope": "user:email"},
        )


def create_session_token(user: dict, jwt_secret: str) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": user["id"],
        "email": user["email"],
        "name": user["name"],
        "picture": user["picture"],
        "iat": now,
        "exp": now + timedelta(days=7),
    }
    return _jwt.encode({"alg": "HS256"}, payload, jwt_secret).decode()


def decode_session_token(token: str, jwt_secret: str) -> Optional[dict]:
    try:
        return _jwt.decode(token, jwt_secret)
    except Exception:
        return None


async def get_user_from_session(request: Request, cfg) -> Optional[dict]:
    token = request.cookies.get("session")
    if not token:
        return None
    payload = decode_session_token(token, cfg.jwt_secret)
    if not payload:
        return None
    user = get_user(payload["sub"])
    if not user:
        return None
    user["_authenticated"] = True
    return user


async def get_current_user(request: Request) -> dict:
    from podcast_generator.web.app import _cfg

    if not _cfg.oauth_google_client_id and not _cfg.oauth_github_client_id:
        if _cfg.web_password:
            token = request.cookies.get("auth_token")
            if token and hmac.compare_digest(token, _cfg.web_password):
                return {"_authenticated": True, "name": "Admin", "email": ""}
            raise HTTPException(status_code=302, headers={"Location": "/login"})
        return {"_authenticated": True, "name": "Sviluppo", "email": ""}

    user = await get_user_from_session(request, _cfg)
    if not user:
        raise HTTPException(status_code=302, headers={"Location": "/login"})
    return user


async def verify_api_token(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> bool:
    from podcast_generator.web.app import _cfg

    if not _cfg.api_token:
        return True
    if credentials is None:
        raise HTTPException(
            status_code=401,
            detail="Missing Authorization header. Use: Authorization: Bearer <token>",
        )
    if not hmac.compare_digest(credentials.credentials, _cfg.api_token):
        raise HTTPException(status_code=401, detail="Invalid API token")
    return True
