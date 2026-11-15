import secrets

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.auth import get_current_account, require_csrf_token, verify_password
from backend.database import get_db
from backend.models import Account
from backend.schemas import LoginRequest


router = APIRouter(prefix="/api/auth", tags=["authentication"])


@router.post("/login")
def login(
    credentials: LoginRequest,
    request: Request,
    db: Session = Depends(get_db),
) -> dict[str, str]:
    account = db.scalar(select(Account).where(Account.username == credentials.username))
    if account is None or not verify_password(credentials.password, account.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password.",
        )

    request.session.clear()
    request.session["account_id"] = account.id
    request.session["csrf_token"] = secrets.token_urlsafe(32)
    return {"username": account.username, "csrf_token": request.session["csrf_token"]}


@router.post("/logout")
def logout(request: Request) -> dict[str, str]:
    require_csrf_token(request)
    request.session.clear()
    return {"message": "Logged out."}


@router.get("/me")
def current_user(
    request: Request,
    account: Account = Depends(get_current_account),
) -> dict[str, str]:
    csrf_token = request.session.get("csrf_token")
    if not isinstance(csrf_token, str):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="CSRF token is unavailable.")
    return {"username": account.username, "csrf_token": csrf_token}
