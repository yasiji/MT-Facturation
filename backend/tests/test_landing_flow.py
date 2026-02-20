from datetime import date

from fastapi.testclient import TestClient
from pytest import MonkeyPatch

from app.services import landing_service


def _create_offer(
    client: TestClient,
    auth_headers_user: dict[str, str],
    *,
    name: str,
    service_category: str,
    service_type: str | None = None,
    status: str = "active",
) -> str:
    payload: dict[str, object] = {
        "name": name,
        "service_category": service_category,
        "version": 1,
        "monthly_fee": "49.90",
        "activation_fee": "10.00",
        "status": status,
        "valid_from": "2026-01-01",
        "valid_to": None,
    }
    if service_category == "mobile":
        payload["mobile_data_gb"] = 10
        payload["mobile_calls_hours"] = 10
    elif service_category == "internet":
        access = service_type or "fiber"
        payload["internet_access_type"] = access
        if access == "fiber":
            payload["internet_fiber_speed_mbps"] = 200
        else:
            payload["internet_adsl_speed_mbps"] = 20
        payload["internet_tv_included"] = True
    elif service_category == "landline":
        payload["landline_national_included"] = True
        payload["landline_international_hours"] = 5
    else:
        raise AssertionError("Unsupported service_category")

    response = client.post("/api/v1/offers", headers=auth_headers_user, json=payload)
    assert response.status_code == 200
    return response.json()["id"]


def _create_client(
    client: TestClient,
    auth_headers_user: dict[str, str],
    *,
    full_name: str,
    cin: str,
) -> str:
    response = client.post(
        "/api/v1/customers",
        headers=auth_headers_user,
        json={
            "cin": cin,
            "client_type": "individual",
            "full_name": full_name,
            "email": f"{full_name.lower().replace(' ', '')}@example.com",
            "phone": "+212612340000",
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
    service_type: str,
    service_identifier: str,
) -> str:
    response = client.post(
        f"/api/v1/customers/{client_id}/subscribers",
        headers=auth_headers_user,
        json={
            "service_type": service_type,
            "service_identifier": service_identifier,
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
) -> str:
    response = client.post(
        "/api/v1/contracts",
        headers=auth_headers_user,
        json={
            "client_id": client_id,
            "subscriber_id": subscriber_id,
            "offer_id": offer_id,
            "contract_start_date": "2026-02-16",
            "status": "active",
        },
    )
    assert response.status_code == 200
    return response.json()["id"]


def _verify_lookup_token(client: TestClient, *, cin: str) -> str:
    response = client.post(
        "/api/v1/landing/clients/verify-cin",
        json={"cin": cin},
    )
    assert response.status_code == 200
    return response.json()["lookup_token"]


def test_landing_bootstrap_is_public_and_lists_categories(
    client: TestClient,
    auth_headers_user: dict[str, str],
) -> None:
    _create_offer(client, auth_headers_user, name="Mobile Basic", service_category="mobile")
    _create_offer(client, auth_headers_user, name="Fiber 200", service_category="internet")
    _create_offer(client, auth_headers_user, name="Landline Plus", service_category="landline")

    response = client.get("/api/v1/landing/bootstrap")
    assert response.status_code == 200
    payload = response.json()
    assert set(payload["flow_options"]) == {
        "subscribe_new_service",
        "upgrade_or_downgrade_existing_service",
        "check_billing_and_download_invoices",
    }
    assert set(payload["services"]) == {"mobile", "internet", "landline"}
    assert len(payload["offer_categories"]) == 3


def test_landing_new_mobile_subscription_creates_client_contract_and_number(
    client: TestClient,
    auth_headers_user: dict[str, str],
) -> None:
    offer_id = _create_offer(
        client,
        auth_headers_user,
        name="Mobile New",
        service_category="mobile",
    )

    response = client.post(
        "/api/v1/landing/submit/new",
        headers={"Idempotency-Key": "landing-new-0001"},
        json={
            "service_category": "mobile",
            "offer_id": offer_id,
            "cin": "AA12345",
            "full_name": "Landing Client",
            "email": "landing-client@example.com",
            "address": "Casablanca",
            "contact_phone": "+21260000000",
            "contract_start_date": date.today().isoformat(),
            "mobile_number_mode": "assign_new",
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["created_client"] is True
    assert payload["created_subscriber"] is True
    assert payload["provisioning_mode"] == "new_contract"
    assert payload["service_identifier"].startswith(("+2126", "+2127"))
    assert len(payload["service_identifier"]) == 13
    assert payload["document_download_url"]

    pdf_response = client.get(payload["document_download_url"])
    assert pdf_response.status_code == 200
    assert "application/pdf" in (pdf_response.headers.get("content-type") or "")
    assert pdf_response.content.startswith(b"%PDF-1.4")

    audit_response = client.get(
        f"/api/v1/contracts/{payload['contract']['id']}/audit",
        headers=auth_headers_user,
    )
    assert audit_response.status_code == 200
    event_types = [event["event_type"] for event in audit_response.json()]
    assert "landing_service_identifier_allocated" in event_types
    assert "contract_document_issued" in event_types

    recovery_response = client.post(
        f"/api/v1/landing/contracts/{payload['contract']['id']}/document-link",
        json={"cin": "AA12345"},
    )
    assert recovery_response.status_code == 200
    assert "document_download_url" in recovery_response.json()

    customers_response = client.get("/api/v1/customers?page=1&size=10", headers=auth_headers_user)
    assert customers_response.status_code == 200
    clients = customers_response.json()["data"]
    assert any(item["cin"] == "AA12345" for item in clients)


def test_landing_existing_mobile_number_can_upgrade_existing_contract(
    client: TestClient,
    auth_headers_user: dict[str, str],
) -> None:
    base_offer_id = _create_offer(
        client,
        auth_headers_user,
        name="Mobile 10",
        service_category="mobile",
    )
    upgrade_offer_id = _create_offer(
        client,
        auth_headers_user,
        name="Mobile 20",
        service_category="mobile",
    )
    client_id = _create_client(
        client,
        auth_headers_user,
        full_name="Upgrade Existing CIN",
        cin="BB12345",
    )
    subscriber_id = _create_subscriber(
        client,
        auth_headers_user,
        client_id=client_id,
        service_type="mobile",
        service_identifier="+212612345678",
    )
    existing_contract_id = _create_contract(
        client,
        auth_headers_user,
        client_id=client_id,
        subscriber_id=subscriber_id,
        offer_id=base_offer_id,
    )

    response = client.post(
        "/api/v1/landing/submit/new",
        headers={"Idempotency-Key": "landing-upgrade-0001"},
        json={
            "service_category": "mobile",
            "offer_id": upgrade_offer_id,
            "cin": "bb12345",
            "full_name": "Upgrade Existing CIN",
            "email": "upgrade-existing@example.com",
            "address": "Rabat",
            "contact_phone": "+21260000001",
            "contract_start_date": date.today().isoformat(),
            "mobile_number_mode": "use_existing",
            "existing_mobile_local_number": "06 12 34 56 78",
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["client_cin"] == "BB12345"
    assert payload["contract"]["id"] == existing_contract_id
    assert payload["provisioning_mode"] == "upgrade_existing_contract"
    assert payload["document_download_url"]


def test_landing_existing_client_new_service_creates_new_contract(
    client: TestClient,
    auth_headers_user: dict[str, str],
) -> None:
    mobile_offer_id = _create_offer(
        client,
        auth_headers_user,
        name="Mobile Existing",
        service_category="mobile",
    )
    internet_offer_id = _create_offer(
        client,
        auth_headers_user,
        name="Fiber New Service",
        service_category="internet",
        service_type="fiber",
    )
    client_id = _create_client(
        client,
        auth_headers_user,
        full_name="Existing New Service",
        cin="EE12345",
    )
    existing_subscriber_id = _create_subscriber(
        client,
        auth_headers_user,
        client_id=client_id,
        service_type="mobile",
        service_identifier="+212677000111",
    )
    previous_contract_id = _create_contract(
        client,
        auth_headers_user,
        client_id=client_id,
        subscriber_id=existing_subscriber_id,
        offer_id=mobile_offer_id,
    )

    response = client.post(
        "/api/v1/landing/submit/new",
        headers={"Idempotency-Key": "landing-existing-new-service-0001"},
        json={
            "service_category": "internet",
            "offer_id": internet_offer_id,
            "cin": "EE12345",
            "full_name": "Existing New Service",
            "email": "existingnewservice@example.com",
            "address": "Fes",
            "contract_start_date": date.today().isoformat(),
            "home_landline_local_number": "05 24 33 44 55",
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["created_client"] is False
    assert payload["created_subscriber"] is True
    assert payload["provisioning_mode"] == "new_contract"
    assert payload["contract"]["id"] != previous_contract_id
    assert payload["service_identifier"].startswith("+2125")


def test_landing_existing_mobile_number_rejects_landline_prefix(
    client: TestClient,
    auth_headers_user: dict[str, str],
) -> None:
    offer_id = _create_offer(
        client,
        auth_headers_user,
        name="Mobile Validation",
        service_category="mobile",
    )

    response = client.post(
        "/api/v1/landing/submit/new",
        headers={"Idempotency-Key": "landing-mobile-invalid-0001"},
        json={
            "service_category": "mobile",
            "offer_id": offer_id,
            "cin": "MV12345",
            "full_name": "Invalid Mobile Prefix",
            "contract_start_date": date.today().isoformat(),
            "mobile_number_mode": "use_existing",
            "existing_mobile_local_number": "05 24 33 44 55",
        },
    )
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "mobile_number_invalid"


def test_landing_lookup_subscriptions_by_cin_returns_eligible_offers(
    client: TestClient,
    auth_headers_user: dict[str, str],
) -> None:
    current_offer_id = _create_offer(
        client,
        auth_headers_user,
        name="Fiber 100",
        service_category="internet",
        service_type="fiber",
    )
    _create_offer(
        client,
        auth_headers_user,
        name="Fiber 300",
        service_category="internet",
        service_type="fiber",
    )
    client_id = _create_client(
        client,
        auth_headers_user,
        full_name="Lookup CIN",
        cin="CC12345",
    )
    subscriber_id = _create_subscriber(
        client,
        auth_headers_user,
        client_id=client_id,
        service_type="fiber",
        service_identifier="+212512345678",
    )
    _create_contract(
        client,
        auth_headers_user,
        client_id=client_id,
        subscriber_id=subscriber_id,
        offer_id=current_offer_id,
    )

    lookup_token = _verify_lookup_token(client, cin="cc12345")
    response = client.get(
        "/api/v1/landing/clients/cc12345/subscriptions",
        params={"lookup_token": lookup_token},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["client"]["cin"] == "CC12345"
    assert payload["client"]["email"] == "l***@example.com"
    assert payload["client"]["phone"].startswith("+******")
    assert len(payload["subscriptions"]) == 1
    subscription = payload["subscriptions"][0]
    assert subscription["service_category"] == "internet"
    assert len(subscription["eligible_offers"]) >= 1


def test_landing_lookup_invoices_by_cin_and_download_pdf(
    client: TestClient,
    auth_headers_user: dict[str, str],
) -> None:
    offer_id = _create_offer(
        client,
        auth_headers_user,
        name="Fiber Billing Lookup",
        service_category="internet",
        service_type="fiber",
    )
    client_id = _create_client(
        client,
        auth_headers_user,
        full_name="Invoice Lookup",
        cin="IV12345",
    )
    subscriber_id = _create_subscriber(
        client,
        auth_headers_user,
        client_id=client_id,
        service_type="fiber",
        service_identifier="+212512340123",
    )
    _create_contract(
        client,
        auth_headers_user,
        client_id=client_id,
        subscriber_id=subscriber_id,
        offer_id=offer_id,
    )

    run_response = client.post(
        "/api/v1/billing/runs",
        headers={**auth_headers_user, "Idempotency-Key": "landing-billing-lookup-0001"},
        json={
            "period_start": "2026-02-01",
            "period_end": "2026-02-28",
            "due_days": 15,
            "tax_rate": "0.10",
        },
    )
    assert run_response.status_code == 200
    assert run_response.json()["invoice_count"] == 1

    lookup_token = _verify_lookup_token(client, cin="IV12345")
    invoices_response = client.get(
        "/api/v1/landing/clients/IV12345/invoices",
        params={"lookup_token": lookup_token},
    )
    assert invoices_response.status_code == 200
    invoices_payload = invoices_response.json()
    assert invoices_payload["client"]["cin"] == "IV12345"
    assert len(invoices_payload["invoices"]) == 1

    invoice_entry = invoices_payload["invoices"][0]
    assert invoice_entry["document_download_url"]
    pdf_response = client.get(invoice_entry["document_download_url"])
    assert pdf_response.status_code == 200
    assert "application/pdf" in (pdf_response.headers.get("content-type") or "")
    assert pdf_response.content.startswith(b"%PDF")


def test_landing_lookup_requires_verification_token(client: TestClient) -> None:
    response = client.get("/api/v1/landing/clients/cc12345/subscriptions")
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "validation_error"


def test_landing_verify_by_cin_returns_lookup_token(
    client: TestClient,
    auth_headers_user: dict[str, str],
) -> None:
    _create_client(client, auth_headers_user, full_name="CIN Lookup", cin="CK12345")
    response = client.post("/api/v1/landing/clients/verify-cin", json={"cin": "CK12345"})
    assert response.status_code == 200
    payload = response.json()
    assert payload["cin"] == "CK12345"
    assert payload["lookup_token"]
    assert payload["masked_contact"]


def test_landing_verify_legacy_endpoint_removed(
    client: TestClient,
    auth_headers_user: dict[str, str],
) -> None:
    _create_client(client, auth_headers_user, full_name="Secure Lookup", cin="LK12345")
    response = client.post(
        "/api/v1/landing/clients/verify",
        json={"cin": "LK12345"},
    )
    assert response.status_code == 404


def test_landing_plan_change_api_journey_with_cin_lookup_and_pdf_download(
    client: TestClient,
    auth_headers_user: dict[str, str],
) -> None:
    current_offer_id = _create_offer(
        client,
        auth_headers_user,
        name="Fiber Current",
        service_category="internet",
        service_type="fiber",
    )
    target_offer_id = _create_offer(
        client,
        auth_headers_user,
        name="Fiber Upgrade",
        service_category="internet",
        service_type="fiber",
    )
    client_id = _create_client(
        client,
        auth_headers_user,
        full_name="Plan Change Journey",
        cin="PJ12345",
    )
    subscriber_id = _create_subscriber(
        client,
        auth_headers_user,
        client_id=client_id,
        service_type="fiber",
        service_identifier="+212512349999",
    )
    contract_id = _create_contract(
        client,
        auth_headers_user,
        client_id=client_id,
        subscriber_id=subscriber_id,
        offer_id=current_offer_id,
    )

    lookup_token = _verify_lookup_token(client, cin="PJ12345")

    lookup = client.get(
        "/api/v1/landing/clients/PJ12345/subscriptions",
        params={"lookup_token": lookup_token},
    )
    assert lookup.status_code == 200
    subscriptions = lookup.json()["subscriptions"]
    assert len(subscriptions) == 1
    assert subscriptions[0]["contract_id"] == contract_id

    plan_change = client.post(
        "/api/v1/landing/submit/plan-change",
        headers={"Idempotency-Key": "landing-plan-journey-0001"},
        json={
            "cin": "PJ12345",
            "source_contract_id": contract_id,
            "target_offer_id": target_offer_id,
            "contract_start_date": "2026-03-01",
            "commitment_months": 12,
        },
    )
    assert plan_change.status_code == 200
    payload = plan_change.json()
    assert payload["contract"]["id"] == contract_id
    assert payload["provisioning_mode"] == "upgrade_existing_contract"
    assert payload["contract"]["start_date"] == "2026-03-01"
    assert payload["document_download_url"]

    pdf_response = client.get(payload["document_download_url"])
    assert pdf_response.status_code == 200
    assert "application/pdf" in (pdf_response.headers.get("content-type") or "")
    assert pdf_response.content.startswith(b"%PDF-1.4")


def test_landing_mobile_number_allocation_retries_on_collision(
    client: TestClient,
    auth_headers_user: dict[str, str],
    monkeypatch: MonkeyPatch,
) -> None:
    offer_id = _create_offer(
        client,
        auth_headers_user,
        name="Mobile Collision",
        service_category="mobile",
    )
    occupied_client_id = _create_client(
        client,
        auth_headers_user,
        full_name="Occupied Number",
        cin="OC12345",
    )
    _create_subscriber(
        client,
        auth_headers_user,
        client_id=occupied_client_id,
        service_type="mobile",
        service_identifier="+212612345678",
    )

    sequence = iter(["612345678", "612345679"])

    def fake_generator(*, kind: str) -> str:
        assert kind == "mobile"
        return next(sequence)

    monkeypatch.setattr(landing_service, "_generate_moroccan_nsn", fake_generator)

    response = client.post(
        "/api/v1/landing/submit/new",
        headers={"Idempotency-Key": "landing-collision-0001"},
        json={
            "service_category": "mobile",
            "offer_id": offer_id,
            "cin": "COL12345",
            "full_name": "Collision Retry",
            "contract_start_date": date.today().isoformat(),
            "mobile_number_mode": "assign_new",
        },
    )
    assert response.status_code == 200
    assert response.json()["service_identifier"] == "+212612345679"


def test_manual_contract_provisioning_api_still_operational(
    client: TestClient,
    auth_headers_user: dict[str, str],
) -> None:
    offer_id = _create_offer(
        client,
        auth_headers_user,
        name="Manual Regression",
        service_category="mobile",
    )
    response = client.post(
        "/api/v1/contracts/provision",
        headers=auth_headers_user,
        json={
            "offer_id": offer_id,
            "contract_start_date": date.today().isoformat(),
            "client": {
                "client_type": "individual",
                "full_name": "Manual Contract Flow",
                "cin": "MC12345",
            },
            "subscriber": {"service_identifier": "+212677123456"},
            "provisioning_intent": "new_line",
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["created_client"] is True
    assert payload["created_subscriber"] is True


def test_landing_new_submit_idempotency_replay_and_payload_conflict(
    client: TestClient,
    auth_headers_user: dict[str, str],
) -> None:
    offer_id = _create_offer(
        client,
        auth_headers_user,
        name="Mobile Replay",
        service_category="mobile",
    )
    endpoint = "/api/v1/landing/submit/new"
    headers = {"Idempotency-Key": "landing-idem-0001"}
    payload = {
        "service_category": "mobile",
        "offer_id": offer_id,
        "cin": "DD12345",
        "full_name": "Replay Client",
        "email": "replay@example.com",
        "address": "Marrakech",
        "contact_phone": "+21260000002",
        "contract_start_date": date.today().isoformat(),
        "mobile_number_mode": "assign_new",
    }

    first = client.post(endpoint, headers=headers, json=payload)
    assert first.status_code == 200
    first_payload = first.json()
    assert first_payload["idempotency_replayed"] is False

    second = client.post(endpoint, headers=headers, json=payload)
    assert second.status_code == 200
    second_payload = second.json()
    assert second_payload["idempotency_replayed"] is True
    assert second_payload["contract"]["id"] == first_payload["contract"]["id"]

    changed_payload = dict(payload)
    changed_payload["full_name"] = "Replay Client Updated"
    conflict = client.post(endpoint, headers=headers, json=changed_payload)
    assert conflict.status_code == 409
    assert conflict.json()["error"]["code"] == "idempotency_key_payload_conflict"
