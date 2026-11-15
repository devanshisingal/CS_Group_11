from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class LoginRequest(BaseModel):
    username: str = Field(min_length=1, max_length=50)
    password: str = Field(min_length=1, max_length=128)


class TransferRequest(BaseModel):
    recipient: str = Field(min_length=1, max_length=50)
    amount: Decimal = Field(gt=0, max_digits=10, decimal_places=2)


class AccountResponse(BaseModel):
    username: str
    balance_paise: int


class TransactionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    direction: str
    other_party: str
    amount_paise: int
    created_at: str
