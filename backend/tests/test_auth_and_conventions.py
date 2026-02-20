from fastapi.testclient import TestClient


def test_me_requires_authentication(client: TestClient) -> None:
    response = client.get("/api/v1/me")
    assert response.status_code == 401
    payload = response.json()
    assert payload["error"]["code"] == "unauthorized"
    assert payload["error"]["trace_id"]


def test_me_with_user_headers(client: TestClient, auth_headers_user: dict[str, str]) -> None:
    response = client.get("/api/v1/me", headers=auth_headers_user)
    assert response.status_code == 200
    assert response.json() == {"actor_id": "user-1", "roles": ["user"]}


def test_admin_ping_requires_admin_role(
    client: TestClient,
    auth_headers_user: dict[str, str],
) -> None:
    response = client.get("/api/v1/admin/ping", headers=auth_headers_user)
    assert response.status_code == 403
    payload = response.json()
    assert payload["error"]["code"] == "forbidden"


def test_admin_ping_with_admin_role(
    client: TestClient,
    auth_headers_admin: dict[str, str],
) -> None:
    response = client.get("/api/v1/admin/ping", headers=auth_headers_admin)
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "actor_id": "admin-1"}


def test_sample_conventions_pagination(
    client: TestClient,
    auth_headers_user: dict[str, str],
) -> None:
    response = client.get(
        "/api/v1/conventions/sample?page=2&size=10&sort=name&filters=active",
        headers=auth_headers_user,
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["meta"] == {
        "page": 2,
        "size": 10,
        "total": 1,
        "sort": "name",
        "filters": "active",
    }


def test_validation_error_uses_standard_error_envelope(
    client: TestClient,
    auth_headers_user: dict[str, str],
) -> None:
    response = client.get("/api/v1/conventions/sample?page=0", headers=auth_headers_user)
    assert response.status_code == 422
    payload = response.json()
    assert payload["error"]["code"] == "validation_error"
    assert isinstance(payload["error"]["details"]["errors"], list)


def test_cors_preflight_is_not_blocked_by_auth(client: TestClient) -> None:
    response = client.options(
        "/api/v1/customers?page=1&size=100",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "content-type,x-actor-id,x-actor-roles",
        },
    )
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == "http://localhost:5173"
