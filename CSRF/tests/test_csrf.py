from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select

from backend.database import initialize_database, make_engine, make_session_factory
from backend.main import create_app
from backend.models import Account, Transaction
from reset_db import main as reset_database


@pytest.fixture
def client(tmp_path) -> Iterator[TestClient]:
    database_path = tmp_path / "test.sqlite3"
    engine = make_engine(f"sqlite:///{database_path.as_posix()}")
    session_factory = make_session_factory(engine)
    initialize_database(engine, session_factory)
    app = create_app(f"sqlite:///{database_path.as_posix()}")
    with TestClient(app) as test_client:
        yield test_client
    engine.dispose()


def login_as_alice(client: TestClient) -> str:
    response = client.post(
        "/api/auth/login",
        json={"username": "alice", "password": "password123"},
    )
    assert response.status_code == 200
    return response.json()["csrf_token"]


def account_balance(client: TestClient, username: str) -> int:
    session_factory = client.app.state.session_factory
    with session_factory() as db:
        account = db.scalar(select(Account).where(Account.username == username))
        assert account is not None
        return account.balance_paise


def test_reset_database_restores_demo_balances_and_clears_transactions(
    tmp_path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    database_path = tmp_path / "reset.sqlite3"
    database_url = f"sqlite:///{database_path.as_posix()}"
    engine = make_engine(database_url)
    session_factory = make_session_factory(engine)
    initialize_database(engine, session_factory)

    with session_factory() as db:
        alice = db.scalar(select(Account).where(Account.username == "alice"))
        attacker = db.scalar(select(Account).where(Account.username == "attacker"))
        assert alice is not None
        assert attacker is not None
        alice.balance_paise = 500_000
        attacker.balance_paise = 500_000
        db.add(
            Transaction(
                sender_id=alice.id,
                recipient_id=attacker.id,
                amount_paise=500_000,
            )
        )
        db.commit()
    engine.dispose()

    monkeypatch.setenv("SECUREBANK_DATABASE_URL", database_url)
    reset_database()

    reset_engine = make_engine(database_url)
    reset_session_factory = make_session_factory(reset_engine)
    with reset_session_factory() as db:
        assert db.scalar(select(Account.balance_paise).where(Account.username == "alice")) == 1_000_000
        assert db.scalar(select(Account.balance_paise).where(Account.username == "attacker")) == 0
        assert db.scalar(select(Transaction)) is None
    reset_engine.dispose()


def test_get_transfer_is_rejected_without_changing_balances_or_history(client: TestClient) -> None:
    csrf_token = login_as_alice(client)
    assert client.get("/api/account").json()["balance_paise"] == 1_000_000

    response = client.get("/transfer?to=attacker&amount=1000")

    assert response.status_code == 405
    assert response.headers["allow"] == "POST"
    assert account_balance(client, "alice") == 1_000_000
    assert account_balance(client, "attacker") == 0
    assert client.get("/api/transactions").json() == []
    assert csrf_token


def test_legitimate_post_transfer_updates_balances_and_history(client: TestClient) -> None:
    csrf_token = login_as_alice(client)

    response = client.post(
        "/transfer",
        json={"recipient": "attacker", "amount": "1000.00"},
        headers={"X-CSRF-Token": csrf_token},
    )

    assert response.status_code == 201
    assert account_balance(client, "alice") == 900_000
    assert account_balance(client, "attacker") == 100_000
    history = client.get("/api/transactions").json()
    assert len(history) == 1
    assert history[0]["direction"] == "sent"
    assert history[0]["other_party"] == "attacker"
    assert history[0]["amount_paise"] == 100_000


def test_post_transfer_requires_csrf_token(client: TestClient) -> None:
    login_as_alice(client)

    response = client.post("/transfer", json={"recipient": "attacker", "amount": "10.00"})

    assert response.status_code == 403
    assert account_balance(client, "alice") == 1_000_000


def test_logout_requires_csrf_token(client: TestClient) -> None:
    csrf_token = login_as_alice(client)

    rejected = client.post("/api/auth/logout")
    accepted = client.post(
        "/api/auth/logout",
        headers={"X-CSRF-Token": csrf_token},
    )

    assert rejected.status_code == 403
    assert accepted.status_code == 200
    assert client.get("/api/account").status_code == 401


@pytest.mark.parametrize(
    ("amount", "expected_status"),
    [("0", 422), ("-1", 422), ("10000.01", 400)],
)
def test_invalid_or_unaffordable_transfer_is_rejected(
    client: TestClient,
    amount: str,
    expected_status: int,
) -> None:
    csrf_token = login_as_alice(client)

    response = client.post(
        "/transfer",
        json={"recipient": "attacker", "amount": amount},
        headers={"X-CSRF-Token": csrf_token},
    )

    assert response.status_code == expected_status
    assert account_balance(client, "alice") == 1_000_000
    assert account_balance(client, "attacker") == 0
    with client.app.state.session_factory() as db:
        assert db.scalar(select(Transaction)) is None


def test_unknown_and_self_recipients_are_rejected(client: TestClient) -> None:
    csrf_token = login_as_alice(client)
    headers = {"X-CSRF-Token": csrf_token}

    unknown = client.post(
        "/transfer",
        json={"recipient": "nobody", "amount": "1.00"},
        headers=headers,
    )
    self_transfer = client.post(
        "/transfer",
        json={"recipient": "alice", "amount": "1.00"},
        headers=headers,
    )

    assert unknown.status_code == 404
    assert self_transfer.status_code == 400
    assert account_balance(client, "alice") == 1_000_000
