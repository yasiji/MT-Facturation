import json
from datetime import date

from fastapi.testclient import TestClient


def _create_offer(
    client: TestClient,
    auth_headers_user: dict[str, str],
    *,
    name: str,
    service_type: str = "mobile",
) -> str:
    payload: dict[str, object] = {
        "name": name,
        "version": 1,
        "monthly_fee": "49.90",
        "status": "active",
        "valid_from": "2026-01-01",
        "valid_to": None,
    }
    if service_type == "mobile":
        payload.update(
            {
                "service_category": "mobile",
                "mobile_data_gb": 10,
                "mobile_calls_hours": 10,
            },
        )
    elif service_type in {"fiber", "adsl"}:
        payload["service_category"] = "internet"
        payload["internet_access_type"] = service_type
        if service_type == "fiber":
            payload["internet_fiber_speed_mbps"] = 200
        else:
            payload["internet_adsl_speed_mbps"] = 20
    elif service_type == "landline":
        payload.update(
            {
                "service_category": "landline",
                "landline_national_included": True,
                "landline_international_hours": 5,
            },
        )
    else:
        raise AssertionError(f"Unsupported service_type for test payload: {service_type}")

    response = client.post(
        "/api/v1/offers",
        headers=auth_headers_user,
        json=payload,
    )
    assert response.status_code == 200
    return response.json()["id"]


def _create_client(client: TestClient, auth_headers_user: dict[str, str], *, full_name: str) -> str:
    response = client.post(
        "/api/v1/customers",
        headers=auth_headers_user,
        json={
            "client_type": "individual",
            "full_name": full_name,
            "email": f"{full_name.lower().replace(' ', '')}@example.com",
            "phone": "+12125550111",
            "status": "active",
        },
    )
    assert response.status_code == 200
    return response.json()["id"]


def _create_subscriber(
    client: TestClient,
    auth_headers_user: dict[str, str],
    *,
    client_id: str,
    identifier: str,
    service_type: str = "mobile",
) -> str:
    response = client.post(
        f"/api/v1/customers/{client_id}/subscribers",
        headers=auth_headers_user,
        json={
            "service_type": service_type,
            "service_identifier": identifier,
            "status": "active",
        },
    )
    assert response.status_code == 200
    return response.json()["id"]


def _create_contract(
    client: TestClient,
    auth_headers_user: dict[str, str],
    *,
    client_id: str,
    subscriber_id: str,
    offer_id: str,
    status: str = "active",
) -> str:
    response = client.post(
        "/api/v1/contracts",
        headers=auth_headers_user,
        json={
            "client_id": client_id,
            "subscriber_id": subscriber_id,
            "offer_id": offer_id,
            "contract_start_date": "2026-02-16",
            "status": status,
        },
    )
    assert response.status_code == 200
    return response.json()["id"]


def test_contract_provisioning_creates_client_and_subscriber_automatically(
    client: TestClient,
    auth_headers_user: dict[str, str],
) -> None:
    offer_id = _create_offer(client, auth_headers_user, name="Mobile Gold")
    response = client.post(
        "/api/v1/contracts/provision",
        headers=auth_headers_user,
        json={
            "offer_id": offer_id,
            "contract_start_date": date.today().isoformat(),
            "commitment_months": 12,
            "auto_activate": True,
            "client": {
                "client_type": "individual",
                "full_name": "Provision Auto Client",
                "email": "provision-auto@example.com",
                "phone": "+12125550112",
            },
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["created_client"] is True
    assert payload["created_subscriber"] is True
    assert payload["contract"]["status"] == "active"

    contract_id = payload["contract"]["id"]
    audit_response = client.get(f"/api/v1/contracts/{contract_id}/audit", headers=auth_headers_user)
    assert audit_response.status_code == 200
    assert audit_response.json()[0]["event_type"] == "contract_provisioned"


def test_contract_provisioning_new_line_creates_new_subscriber(
    client: TestClient,
    auth_headers_user: dict[str, str],
) -> None:
    offer_id = _create_offer(client, auth_headers_user, name="Fiber Home", service_type="fiber")
    client_id = _create_client(client, auth_headers_user, full_name="Provision Existing Client")
    existing_subscriber_id = _create_subscriber(
        client,
        auth_headers_user,
        client_id=client_id,
        identifier="FIB-998877",
        service_type="fiber",
    )
    _create_contract(
        client,
        auth_headers_user,
        client_id=client_id,
        subscriber_id=existing_subscriber_id,
        offer_id=offer_id,
        status="active",
    )

    response = client.post(
        "/api/v1/contracts/provision",
        headers=auth_headers_user,
        json={
            "offer_id": offer_id,
            "client_id": client_id,
            "provisioning_intent": "new_line",
            "subscriber": {"service_identifier": "FIB-NEW-778899"},
            "contract_start_date": date.today().isoformat(),
            "auto_activate": False,
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["created_client"] is False
    assert payload["created_subscriber"] is True
    assert payload["provisioning_mode"] == "new_contract"
    assert payload["contract"]["subscriber_id"] != existing_subscriber_id
    assert payload["contract"]["status"] == "draft"


def test_contract_provisioning_upgrade_updates_existing_contract_offer(
    client: TestClient,
    auth_headers_user: dict[str, str],
) -> None:
    base_offer_id = _create_offer(client, auth_headers_user, name="Mobile 10GB")
    upgraded_offer_id = _create_offer(client, auth_headers_user, name="Mobile 20GB")
    client_id = _create_client(client, auth_headers_user, full_name="Upgrade Client")
    subscriber_id = _create_subscriber(
        client,
        auth_headers_user,
        client_id=client_id,
        identifier="MOB-UP-001",
        service_type="mobile",
    )
    contract_id = _create_contract(
        client,
        auth_headers_user,
        client_id=client_id,
        subscriber_id=subscriber_id,
        offer_id=base_offer_id,
        status="active",
    )

    response = client.post(
        "/api/v1/contracts/provision",
        headers=auth_headers_user,
        json={
            "offer_id": upgraded_offer_id,
            "client_id": client_id,
            "contract_start_date": date.today().isoformat(),
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["created_client"] is False
    assert payload["created_subscriber"] is False
    assert payload["provisioning_mode"] == "upgrade_existing_contract"
    assert payload["contract"]["id"] == contract_id
    assert payload["contract"]["offer_id"] == upgraded_offer_id


def test_contract_provisioning_upgrade_requires_disambiguation(
    client: TestClient,
    auth_headers_user: dict[str, str],
) -> None:
    base_offer_id = _create_offer(client, auth_headers_user, name="Mobile Base")
    upgraded_offer_id = _create_offer(client, auth_headers_user, name="Mobile Plus")
    client_id = _create_client(client, auth_headers_user, full_name="Disambiguation Client")
    subscriber_a = _create_subscriber(
        client,
        auth_headers_user,
        client_id=client_id,
        identifier="MOB-DIS-001",
        service_type="mobile",
    )
    subscriber_b = _create_subscriber(
        client,
        auth_headers_user,
        client_id=client_id,
        identifier="MOB-DIS-002",
        service_type="mobile",
    )
    contract_a = _create_contract(
        client,
        auth_headers_user,
        client_id=client_id,
        subscriber_id=subscriber_a,
        offer_id=base_offer_id,
        status="active",
    )
    contract_b = _create_contract(
        client,
        auth_headers_user,
        client_id=client_id,
        subscriber_id=subscriber_b,
        offer_id=base_offer_id,
        status="active",
    )

    response = client.post(
        "/api/v1/contracts/provision",
        headers=auth_headers_user,
        json={
            "offer_id": upgraded_offer_id,
            "client_id": client_id,
            "contract_start_date": date.today().isoformat(),
        },
    )
    assert response.status_code == 409
    assert response.json()["error"]["code"] == "contract_upgrade_disambiguation_required"
    candidate_ids = response.json()["error"]["details"]["candidate_contract_ids"]
    assert set(candidate_ids) == {contract_a, contract_b}

    targeted_response = client.post(
        "/api/v1/contracts/provision",
        headers=auth_headers_user,
        json={
            "offer_id": upgraded_offer_id,
            "client_id": client_id,
            "target_contract_id": contract_a,
            "contract_start_date": date.today().isoformat(),
        },
    )
    assert targeted_response.status_code == 200
    assert targeted_response.json()["contract"]["id"] == contract_a
    assert targeted_response.json()["contract"]["offer_id"] == upgraded_offer_id


def test_contract_provisioning_auto_new_line_with_identifier_even_if_upgrade_exists(
    client: TestClient,
    auth_headers_user: dict[str, str],
) -> None:
    offer_id = _create_offer(client, auth_headers_user, name="Mobile Core")
    client_id = _create_client(client, auth_headers_user, full_name="Auto New Line Client")
    existing_subscriber_id = _create_subscriber(
        client,
        auth_headers_user,
        client_id=client_id,
        identifier="MOB-AUTO-001",
        service_type="mobile",
    )
    _create_contract(
        client,
        auth_headers_user,
        client_id=client_id,
        subscriber_id=existing_subscriber_id,
        offer_id=offer_id,
        status="active",
    )

    response = client.post(
        "/api/v1/contracts/provision",
        headers=auth_headers_user,
        json={
            "offer_id": offer_id,
            "client_id": client_id,
            "contract_start_date": date.today().isoformat(),
            "subscriber": {"service_identifier": "MOB-AUTO-NEW-LINE"},
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["provisioning_mode"] == "new_contract"
    assert payload["created_subscriber"] is True
    assert payload["contract"]["subscriber_id"] != existing_subscriber_id


def test_contract_status_transition_and_offer_change_audit(
    client: TestClient,
    auth_headers_user: dict[str, str],
) -> None:
    base_offer_id = _create_offer(client, auth_headers_user, name="Mobile Basic")
    upgraded_offer_id = _create_offer(client, auth_headers_user, name="Mobile Premium")
    client_id = _create_client(client, auth_headers_user, full_name="Status Flow Client")
    subscriber_id = _create_subscriber(
        client,
        auth_headers_user,
        client_id=client_id,
        identifier="MOB-001122",
    )

    create_contract_response = client.post(
        "/api/v1/contracts",
        headers=auth_headers_user,
        json={
            "client_id": client_id,
            "subscriber_id": subscriber_id,
            "offer_id": base_offer_id,
            "contract_start_date": "2026-02-16",
            "status": "draft",
        },
    )
    assert create_contract_response.status_code == 200
    contract_id = create_contract_response.json()["id"]

    activate_response = client.put(
        f"/api/v1/contracts/{contract_id}/status",
        headers=auth_headers_user,
        json={"status": "active"},
    )
    assert activate_response.status_code == 200
    assert activate_response.json()["status"] == "active"

    suspend_response = client.put(
        f"/api/v1/contracts/{contract_id}/status",
        headers=auth_headers_user,
        json={"status": "suspended"},
    )
    assert suspend_response.status_code == 200
    assert suspend_response.json()["status"] == "suspended"

    offer_change_response = client.put(
        f"/api/v1/contracts/{contract_id}/offer",
        headers=auth_headers_user,
        json={"offer_id": upgraded_offer_id},
    )
    assert offer_change_response.status_code == 200
    assert offer_change_response.json()["offer_id"] == upgraded_offer_id

    terminate_response = client.put(
        f"/api/v1/contracts/{contract_id}/status",
        headers=auth_headers_user,
        json={"status": "terminated"},
    )
    assert terminate_response.status_code == 200
    assert terminate_response.json()["status"] == "terminated"
    assert terminate_response.json()["end_date"] is not None

    invalid_transition_response = client.put(
        f"/api/v1/contracts/{contract_id}/status",
        headers=auth_headers_user,
        json={"status": "active"},
    )
    assert invalid_transition_response.status_code == 409
    assert (
        invalid_transition_response.json()["error"]["code"]
        == "contract_status_transition_invalid"
    )

    audit_response = client.get(f"/api/v1/contracts/{contract_id}/audit", headers=auth_headers_user)
    assert audit_response.status_code == 200
    audit_event_types = [event["event_type"] for event in audit_response.json()]
    assert "contract_created" in audit_event_types
    assert "contract_status_changed" in audit_event_types
    assert "contract_offer_changed" in audit_event_types
    offer_change_event = next(
        event for event in audit_response.json() if event["event_type"] == "contract_offer_changed"
    )
    details = json.loads(offer_change_event["details"])
    assert details["from_offer_id"] == base_offer_id
    assert details["to_offer_id"] == upgraded_offer_id
