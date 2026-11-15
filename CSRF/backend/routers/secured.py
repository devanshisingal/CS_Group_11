from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.auth import get_current_account, require_csrf_token
from backend.database import get_db
from backend.models import Account, Transaction
from backend.schemas import TransferRequest


router = APIRouter(tags=["transfers"])


@router.get("/transfer", status_code=status.HTTP_405_METHOD_NOT_ALLOWED)
def reject_state_changing_get() -> None:
    raise HTTPException(
        status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
        detail="Transfers require POST; state-changing GET requests are disabled.",
        headers={"Allow": "POST"},
    )


@router.post("/transfer", status_code=status.HTTP_201_CREATED)
def transfer(
    payload: TransferRequest,
    request: Request,
    account: Account = Depends(get_current_account),
    db: Session = Depends(get_db),
) -> dict[str, str | int]:
    # State-changing requests require a session-bound CSRF token, not just POST.
    require_csrf_token(request)

    amount_paise = int(payload.amount * Decimal(100))
    if amount_paise <= 0:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Amount must be at least ₹0.01.")
    if payload.recipient == account.username:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Choose a different recipient.")

    recipient = db.scalar(select(Account).where(Account.username == payload.recipient))
    if recipient is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recipient account not found.")
    if account.balance_paise < amount_paise:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Insufficient balance.")

    account.balance_paise -= amount_paise
    recipient.balance_paise += amount_paise
    db.add(
        Transaction(
            sender_id=account.id,
            recipient_id=recipient.id,
            amount_paise=amount_paise,
        )
    )
    db.commit()
    return {
        "message": "Transfer completed.",
        "recipient": recipient.username,
        "amount_paise": amount_paise,
    }
