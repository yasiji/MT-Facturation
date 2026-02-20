from fastapi.testclient import TestClient


def _mobile_offer_payload(name: str) -> dict[str, object]:
    return {
        "name": name,
        "service_category": "mobile",
        "mobile_data_gb": 30,
        "mobile_calls_hours": 15,
        "version": 1,
        "monthly_fee": "89.90",
        "status": "active",
        "valid_from": "2026-01-01",
        "valid_to": None,
    }


def test_customer_and_subscriber_contract_flow(
    client: TestClient,
    auth_headers_user: dict[str, str],
) -> None:
    create_client_response = client.post(
        "/api/v1/customers",
        headers=auth_headers_user,
        json={
            "client_type": "individual",
            "full_name": "Alice Martin",
            "email": "alice@example.com",
            "phone": "+12125550000",
            "status": "active",
        },
    )
    assert create_client_response.status_code == 200
    created_client = create_client_response.json()
    client_id = created_client["id"]

    list_clients_response = client.get(
        "/api/v1/customers?page=1&size=10",
        headers=auth_headers_user,
    )
    assert list_clients_response.status_code == 200
    assert list_clients_response.json()["meta"]["total"] == 1

    get_client_response = client.get(f"/api/v1/customers/{client_id}", headers=auth_headers_user)
    assert get_client_response.status_code == 200
    assert get_client_response.json()["full_name"] == "Alice Martin"

    update_client_response = client.put(
        f"/api/v1/customers/{client_id}",
        headers=auth_headers_user,
        json={"status": "suspended"},
    )
    assert update_client_response.status_code == 200
    assert update_client_response.json()["status"] == "suspended"

    create_subscriber_response = client.post(
        f"/api/v1/customers/{client_id}/subscribers",
        headers=auth_headers_user,
        json={
            "service_type": "mobile",
            "service_identifier": " 21655123456 ",
            "status": "active",
        },
    )
    assert create_subscriber_response.status_code == 200
    assert create_subscriber_response.json()["service_identifier"] == "21655123456"
    subscriber_id = create_subscriber_response.json()["id"]

    list_subscribers_response = client.get(
        f"/api/v1/customers/{client_id}/subscribers?page=1&size=10",
        headers=auth_headers_user,
    )
    assert list_subscribers_response.status_code == 200
    assert list_subscribers_response.json()["meta"]["total"] == 1

    get_subscriber_response = client.get(
        f"/api/v1/subscribers/{subscriber_id}",
        headers=auth_headers_user,
    )
    assert get_subscriber_response.status_code == 200
    assert get_subscriber_response.json()["service_type"] == "mobile"


def test_create_subscriber_rejects_short_identifier(
    client: TestClient,
    auth_headers_user: dict[str, str],
) -> None:
    create_client_response = client.post(
        "/api/v1/customers",
        headers=auth_headers_user,
        json={
            "client_type": "individual",
            "full_name": "Short Identifier Test",
            "email": "short@example.com",
            "phone": "+12125550001",
            "status": "active",
        },
    )
    assert create_client_response.status_code == 200
    client_id = create_client_response.json()["id"]

    create_subscriber_response = client.post(
        f"/api/v1/customers/{client_id}/subscribers",
        headers=auth_headers_user,
        json={
            "service_type": "mobile",
            "service_identifier": " a ",
            "status": "active",
        },
    )
    assert create_subscriber_response.status_code == 422
    response_body = create_subscriber_response.json()
    assert response_body["error"]["code"] == "validation_error"
    assert response_body["error"]["details"]["errors"][0]["loc"] == ["body", "service_identifier"]


def test_offer_catalog_contract_flow(
    client: TestClient,
    auth_headers_user: dict[str, str],
) -> None:
    create_offer_response = client.post(
        "/api/v1/offers",
        headers=auth_headers_user,
        json=_mobile_offer_payload("Data Pass 30Go"),
    )
    assert create_offer_response.status_code == 200
    created_offer = create_offer_response.json()
    offer_id = created_offer["id"]
    assert created_offer["service_category"] == "mobile"
    assert created_offer["service_type"] == "mobile"
    assert created_offer["mobile_data_gb"] == 30
    assert created_offer["mobile_calls_hours"] == 15

    list_offers_response = client.get("/api/v1/offers?page=1&size=10", headers=auth_headers_user)
    assert list_offers_response.status_code == 200
    assert list_offers_response.json()["meta"]["total"] == 1

    get_offer_response = client.get(f"/api/v1/offers/{offer_id}", headers=auth_headers_user)
    assert get_offer_response.status_code == 200
    assert get_offer_response.json()["name"] == "Data Pass 30Go"

    update_offer_response = client.put(
        f"/api/v1/offers/{offer_id}",
        headers=auth_headers_user,
        json={
            "status": "retired",
            "monthly_fee": "79.90",
            "mobile_calls_hours": 20,
        },
    )
    assert update_offer_response.status_code == 200
    assert update_offer_response.json()["status"] == "retired"
    assert update_offer_response.json()["monthly_fee"] == "79.90"
    assert update_offer_response.json()["mobile_calls_hours"] == 20

    delete_offer_response = client.delete(f"/api/v1/offers/{offer_id}", headers=auth_headers_user)
    assert delete_offer_response.status_code == 204


def test_offer_component_validation_rules(
    client: TestClient,
    auth_headers_user: dict[str, str],
) -> None:
    missing_access_response = client.post(
        "/api/v1/offers",
        headers=auth_headers_user,
        json={
            "name": "Internet Invalid",
            "service_category": "internet",
            "internet_tv_included": True,
            "version": 1,
            "monthly_fee": "49.90",
            "status": "active",
            "valid_from": "2026-01-01",
        },
    )
    assert missing_access_response.status_code == 422
    assert missing_access_response.json()["error"]["code"] == "validation_error"

    landline_hours_response = client.post(
        "/api/v1/offers",
        headers=auth_headers_user,
        json={
            "name": "Landline Invalid Decimal",
            "service_category": "landline",
            "landline_national_included": True,
            "landline_international_hours": 1.5,
            "version": 1,
            "monthly_fee": "19.90",
            "status": "active",
            "valid_from": "2026-01-01",
        },
    )
    assert landline_hours_response.status_code == 422
    assert landline_hours_response.json()["error"]["code"] == "validation_error"


def test_offer_categories_grouping_flow(
    client: TestClient,
    auth_headers_user: dict[str, str],
) -> None:
    payloads = [
        {
            "name": "Data Pass",
            "service_category": "mobile",
            "mobile_data_gb": 30,
            "version": 1,
            "monthly_fee": "30.00",
            "status": "active",
            "valid_from": "2026-01-01",
        },
        {
            "name": "Fiber 200 + TV",
            "service_category": "internet",
            "internet_access_type": "fiber",
            "internet_fiber_speed_mbps": 200,
            "internet_tv_included": True,
            "version": 1,
            "monthly_fee": "120.00",
            "status": "active",
            "valid_from": "2026-01-01",
        },
        {
            "name": "Landline Plus",
            "service_category": "landline",
            "landline_national_included": True,
            "landline_international_hours": 10,
            "landline_phone_hours": 5,
            "version": 1,
            "monthly_fee": "25.00",
            "status": "active",
            "valid_from": "2026-01-01",
        },
    ]

    for payload in payloads:
        response = client.post("/api/v1/offers", headers=auth_headers_user, json=payload)
        assert response.status_code == 200
        if payload["service_category"] == "internet":
            assert response.json()["internet_landline_included"] is True

    categories_response = client.get("/api/v1/offer-categories", headers=auth_headers_user)
    assert categories_response.status_code == 200
    categories = categories_response.json()
    assert len(categories) == 3
    categories_index = {item["service_category"]: item for item in categories}
    assert "mobile" in categories_index
    assert "internet" in categories_index
    assert "landline" in categories_index
    assert categories_index["internet"]["offers"][0]["service_type"] in {"fiber", "adsl"}

    compat_response = client.get("/api/v1/offer-families", headers=auth_headers_user)
    assert compat_response.status_code == 200


def test_internet_offer_forces_landline_on(
    client: TestClient,
    auth_headers_user: dict[str, str],
) -> None:
    create_response = client.post(
        "/api/v1/offers",
        headers=auth_headers_user,
        json={
            "name": "Fiber 300",
            "service_category": "internet",
            "internet_access_type": "fiber",
            "internet_fiber_speed_mbps": 300,
            "internet_landline_included": False,
            "internet_tv_included": False,
            "version": 1,
            "monthly_fee": "95.00",
            "status": "active",
            "valid_from": "2026-01-01",
        },
    )
    assert create_response.status_code == 200
    created_offer = create_response.json()
    assert created_offer["internet_landline_included"] is True

    update_response = client.put(
        f"/api/v1/offers/{created_offer['id']}",
        headers=auth_headers_user,
        json={"internet_landline_included": False},
    )
    assert update_response.status_code == 200
    assert update_response.json()["internet_landline_included"] is True


def test_client_delete_guardrails(
    client: TestClient,
    auth_headers_user: dict[str, str],
) -> None:
    client_response = client.post(
        "/api/v1/customers",
        headers=auth_headers_user,
        json={
            "client_type": "individual",
            "full_name": "Delete Candidate",
            "email": "delete-candidate@example.com",
            "phone": "+12125550101",
            "status": "active",
        },
    )
    assert client_response.status_code == 200
    deletable_client_id = client_response.json()["id"]

    delete_response = client.delete(
        f"/api/v1/customers/{deletable_client_id}",
        headers=auth_headers_user,
    )
    assert delete_response.status_code == 204

    get_deleted_response = client.get(
        f"/api/v1/customers/{deletable_client_id}",
        headers=auth_headers_user,
    )
    assert get_deleted_response.status_code == 404

    guarded_client_response = client.post(
        "/api/v1/customers",
        headers=auth_headers_user,
        json={
            "client_type": "individual",
            "full_name": "Delete Blocked",
            "email": "delete-blocked@example.com",
            "phone": "+12125550102",
            "status": "active",
        },
    )
    assert guarded_client_response.status_code == 200
    guarded_client_id = guarded_client_response.json()["id"]

    subscriber_response = client.post(
        f"/api/v1/customers/{guarded_client_id}/subscribers",
        headers=auth_headers_user,
        json={
            "service_type": "mobile",
            "service_identifier": "MOB-DEL-001",
            "status": "active",
        },
    )
    assert subscriber_response.status_code == 200
    subscriber_id = subscriber_response.json()["id"]

    offer_response = client.post(
        "/api/v1/offers",
        headers=auth_headers_user,
        json=_mobile_offer_payload("Delete Guard Offer"),
    )
    assert offer_response.status_code == 200
    offer_id = offer_response.json()["id"]

    contract_response = client.post(
        "/api/v1/contracts",
        headers=auth_headers_user,
        json={
            "client_id": guarded_client_id,
            "subscriber_id": subscriber_id,
            "offer_id": offer_id,
            "contract_start_date": "2026-02-16",
            "status": "active",
        },
    )
    assert contract_response.status_code == 200

    blocked_delete_response = client.delete(
        f"/api/v1/customers/{guarded_client_id}",
        headers=auth_headers_user,
    )
    assert blocked_delete_response.status_code == 409
    assert blocked_delete_response.json()["error"]["code"] == "client_delete_blocked"

    blocked_offer_delete_response = client.delete(
        f"/api/v1/offers/{offer_id}",
        headers=auth_headers_user,
    )
    assert blocked_offer_delete_response.status_code == 409
    assert blocked_offer_delete_response.json()["error"]["code"] == "offer_delete_blocked"


def test_new_domain_endpoints_require_authentication(client: TestClient) -> None:
    response = client.get("/api/v1/customers")
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "unauthorized"
