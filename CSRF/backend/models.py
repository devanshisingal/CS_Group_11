from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database import Base


class Account(Base):
    __tablename__ = "accounts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(256), nullable=False)
    balance_paise: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    sent_transactions: Mapped[list["Transaction"]] = relationship(
        back_populates="sender",
        foreign_keys="Transaction.sender_id",
    )
    received_transactions: Mapped[list["Transaction"]] = relationship(
        back_populates="recipient",
        foreign_keys="Transaction.recipient_id",
    )


class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    sender_id: Mapped[int] = mapped_column(ForeignKey("accounts.id"), nullable=False)
    recipient_id: Mapped[int] = mapped_column(ForeignKey("accounts.id"), nullable=False)
    amount_paise: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    sender: Mapped[Account] = relationship(
        back_populates="sent_transactions",
        foreign_keys=[sender_id],
    )
    recipient: Mapped[Account] = relationship(
        back_populates="received_transactions",
        foreign_keys=[recipient_id],
    )
