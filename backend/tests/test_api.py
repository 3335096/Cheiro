import uuid
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

from app.core.database import get_db
from app.main import app
from app.models.analysis import JobStatus
from tests.test_telegram_auth import sign_init_data

ADMIN = {"X-Admin-Token": "test-admin-token"}


class FakeResult:
    def __init__(self, value):
        self.value = value

    def scalar_one_or_none(self):
        return self.value


class FakeSession:
    def __init__(self, job=None):
        self.job = job

    async def execute(self, _stmt):
        return FakeResult(self.job)


def make_job(owner: str):
    return SimpleNamespace(
        id=uuid.uuid4(),
        telegram_user_id=owner,
        status=JobStatus.done,
        teaser="Short teaser",
        full_report="PRIVATE FULL REPORT",
        error_message=None,
    )


@pytest.fixture
def client_for():
    def factory(job=None) -> TestClient:
        app.dependency_overrides[get_db] = lambda: FakeSession(job)
        # No context manager: the lifespan would try to reach a real database.
        return TestClient(app)

    yield factory
    app.dependency_overrides.clear()


def test_health(client_for):
    response = client_for().get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_admin_routes_require_token(client_for):
    client = client_for()

    assert client.get("/api/admin/sources").status_code == 401
    assert client.get("/api/admin/sources", headers={"X-Admin-Token": "wrong"}).status_code == 401
    assert client.post("/api/admin/rag/query", json={"query": "x"}).status_code == 401


def test_analysis_status_hides_full_report_from_mini_app(client_for):
    job = make_job(owner="dev-user")

    response = client_for(job).get(f"/api/analysis/{job.id}")

    assert response.status_code == 200
    body = response.json()
    assert body["teaser"] == "Short teaser"
    assert "full_report" not in body


def test_analysis_status_is_private_to_owner(client_for):
    job = make_job(owner="someone-else")

    response = client_for(job).get(f"/api/analysis/{job.id}")

    assert response.status_code == 404


def test_analysis_status_accepts_valid_telegram_identity(client_for):
    job = make_job(owner="42")
    init_data = sign_init_data({"user": '{"id": 42}', "auth_date": "1700000000"}, "123456:TEST-TOKEN")

    response = client_for(job).get(f"/api/analysis/{job.id}", headers={"X-Telegram-Init-Data": init_data})

    assert response.status_code == 200


def test_analysis_status_rejects_forged_telegram_identity(client_for):
    job = make_job(owner="42")

    response = client_for(job).get(
        f"/api/analysis/{job.id}", headers={"X-Telegram-Init-Data": "user=%7B%22id%22%3A42%7D&hash=bad"}
    )

    assert response.status_code == 401


def test_unknown_or_malformed_job_id_returns_404(client_for):
    assert client_for(None).get(f"/api/analysis/{uuid.uuid4()}").status_code == 404
    assert client_for(None).get("/api/analysis/not-a-uuid").status_code == 404
