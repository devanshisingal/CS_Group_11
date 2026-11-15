from fastapi import APIRouter, Depends
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from backend.auth import get_current_account
from backend.database import get_db
from backend.models import Account, Transaction


router = APIRouter(prefix="/api", tags=["accounts"])


@router.get("/account")
def account_summary(account: Account = Depends(get_current_account)) -> dict[str, int | str]:
    return {"username": account.username, "balance_paise": account.balance_paise}


@router.get("/transactions")
def transaction_history(
    account: Account = Depends(get_current_account),
    db: Session = Depends(get_db),
) -> list[dict[str, int | str]]:
    transactions = db.scalars(
        select(Transaction)
        .where(or_(Transaction.sender_id == account.id, Transaction.recipient_id == account.id))
        .order_by(Transaction.created_at.desc(), Transaction.id.desc())
    ).all()

    results: list[dict[str, int | str]] = []
    for transaction in transactions:
        outgoing = transaction.sender_id == account.id
        other_account = transaction.recipient if outgoing else transaction.sender
        results.append(
            {
                "id": transaction.id,
                "direction": "sent" if outgoing else "received",
                "other_party": other_account.username,
                "amount_paise": transaction.amount_paise,
                "created_at": transaction.created_at.isoformat(),
            }
        )
    return results
