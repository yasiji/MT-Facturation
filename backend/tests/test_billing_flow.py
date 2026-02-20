from datetime import date

from fastapi.testclient import TestClient


def _create_offer(
    client: TestClient,
    headers: dict[str, str],
    *,
    name: str,
    service_category: str = "internet",
    monthly_fee: str = "99.00",
    activation_fee: str = "20.00",
) -> str:
    payload: dict[str, object] = {
        "name": name,
        "service_category": service_category,
        "version": 1,
        "monthly_fee": monthly_fee,
        "activation_fee": activation_fee,
        "status": "active",
        "valid_from": "2026-01-01",
        "valid_to": None,
    }
    if service_category == "mobile":
        payload["mobile_data_gb"] = 20
        payload["mobile_calls_hours"] = 15
    elif service_category == "internet":
        payload["internet_access_type"] = "fiber"
        payload["internet_fiber_speed_mbps"] = 200
        payload["internet_tv_included"] = True
    else:
        payload["landline_national_included"] = True

    response = client.post(
        "/api/v1/offers",
        headers=headers,
        json=payload,
    )
    assert response.status_code == 200
    return response.json()["id"]


def _create_client(client: TestClient, headers: dict[str, str], *, name: str, cin: str) -> str:
    response = client.post(
        "/api/v1/customers",
        headers=headers,
        json={
            "cin": cin,
            "client_type": "individual",
            "full_name": name,
            "email": f"{name.lower().replace(' ', '')}@example.com",
            "phone": "+212612340010",
            "status": "active",
        },
    )
    assert response.status_code == 200
    return response.json()["id"]


def _create_subscriber(
    client: TestClient,
    headers: dict[str, str],
    *,
    client_id: str,
    identifier: str,
    service_type: str = "fiber",
) -> str:
    response = client.post(
        f"/api/v1/customers/{client_id}/subscribers",
        headers=headers,
        json={"service_type": service_type, "service_identifier": identifier, "status": "active"},
    )
    assert response.status_code == 200
    return response.json()["id"]


def _create_contract(
    client: TestClient,
    headers: dict[str, str],
    *,
    client_id: str,
    subscriber_id: str,
    offer_id: str,
    start_date: str,
    status: str = "active",
) -> str:
    response = client.post(
        "/api/v1/contracts",
        headers=headers,
        json={
            "client_id": client_id,
            "subscriber_id": subscriber_id,
            "offer_id": offer_id,
            "contract_start_date": start_date,
            "status": status,
        },
    )
    assert response.status_code == 200
    return response.json()["id"]


def test_billing_run_generates_invoice_and_pdf(
    client: TestClient,
    auth_headers_admin: dict[str, str],
) -> None:
    offer_id = _create_offer(client, auth_headers_admin, name="Fiber Gold")
    client_id = _create_client(client, auth_headers_admin, name="Billing Client", cin="BILL1001")
    subscriber_id = _create_subscriber(
        client,
        auth_headers_admin,
        client_id=client_id,
        identifier="+212512340010",
    )
    _create_contract(
        client,
        auth_headers_admin,
        client_id=client_id,
        subscriber_id=subscriber_id,
        offer_id=offer_id,
        start_date="2026-02-05",
    )

    run_response = client.post(
        "/api/v1/billing/runs",
        headers={**auth_headers_admin, "Idempotency-Key": "billing-run-0001"},
        json={
            "period_start": "2026-02-01",
            "period_end": "2026-02-28",
            "due_days": 15,
            "tax_rate": "0.10",
        },
    )
    assert run_response.status_code == 200
    run_payload = run_response.json()
    assert run_payload["invoice_count"] == 1
    assert run_payload["idempotency_replayed"] is False
    invoice_id = run_payload["invoice_ids"][0]

    list_response = client.get("/api/v1/invoices?page=1&size=20", headers=auth_headers_admin)
    assert list_response.status_code == 200
    assert list_response.json()["meta"]["total"] == 1

    detail_response = client.get(f"/api/v1/invoices/{invoice_id}", headers=auth_headers_admin)
    assert detail_response.status_code == 200
    detail_payload = detail_response.json()
    assert detail_payload["status"] == "issued"
    assert len(detail_payload["lines"]) >= 1

    pdf_response = client.get(f"/api/v1/invoices/{invoice_id}/pdf", headers=auth_headers_admin)
    assert pdf_response.status_code == 200
    assert "application/pdf" in (pdf_response.headers.get("content-type") or "")
    assert pdf_response.content.startswith(b"%PDF")


def test_billing_run_idempotency_replay_and_conflict(
    client: TestClient,
    auth_headers_admin: dict[str, str],
) -> None:
    offer_id = _create_offer(client, auth_headers_admin, name="Fiber Silver")
    client_id = _create_client(client, auth_headers_admin, name="Replay Billing", cin="BILL1002")
    subscriber_id = _create_subscriber(
        client,
        auth_headers_admin,
        client_id=client_id,
        identifier="+212512340011",
    )
    _create_contract(
        client,
        auth_headers_admin,
        client_id=client_id,
        subscriber_id=subscriber_id,
        offer_id=offer_id,
        start_date=date.today().isoformat(),
    )

    payload = {"period_start": "2026-02-01", "period_end": "2026-02-28", "due_days": 10}
    headers = {**auth_headers_admin, "Idempotency-Key": "billing-run-0002"}
    first = client.post("/api/v1/billing/runs", headers=headers, json=payload)
    assert first.status_code == 200
    second = client.post("/api/v1/billing/runs", headers=headers, json=payload)
    assert second.status_code == 200
    assert second.json()["idempotency_replayed"] is True
    assert second.json()["billing_run_id"] == first.json()["billing_run_id"]

    conflict = client.post(
        "/api/v1/billing/runs",
        headers=headers,
        json={"period_start": "2026-03-01", "period_end": "2026-03-31"},
    )
    assert conflict.status_code == 409
    assert conflict.json()["error"]["code"] == "idempotency_key_payload_conflict"


def test_billing_skips_non_active_contracts(
    client: TestClient,
    auth_headers_admin: dict[str, str],
) -> None:
    offer_id = _create_offer(client, auth_headers_admin, name="Fiber Draft Contract")
    client_id = _create_client(client, auth_headers_admin, name="No Bill Client", cin="BILL1003")
    subscriber_id = _create_subscriber(
        client,
        auth_headers_admin,
        client_id=client_id,
        identifier="+212512340012",
    )
    _create_contract(
        client,
        auth_headers_admin,
        client_id=client_id,
        subscriber_id=subscriber_id,
        offer_id=offer_id,
        start_date="2026-02-03",
        status="draft",
    )

    run_response = client.post(
        "/api/v1/billing/runs",
        headers={**auth_headers_admin, "Idempotency-Key": "billing-run-0003"},
        json={"period_start": "2026-02-01", "period_end": "2026-02-28"},
    )
    assert run_response.status_code == 200
    assert run_response.json()["invoice_count"] == 0


def test_invoice_list_filters_by_client_service_and_offer(
    client: TestClient,
    auth_headers_admin: dict[str, str],
) -> None:
    internet_offer_id = _create_offer(
        client,
        auth_headers_admin,
        name="Fiber Filter Plan",
        service_category="internet",
    )
    mobile_offer_id = _create_offer(
        client,
        auth_headers_admin,
        name="Mobile Filter Plan",
        service_category="mobile",
    )

    internet_client_id = _create_client(
        client,
        auth_headers_admin,
        name="Internet Filter Client",
        cin="BILL2001",
    )
    mobile_client_id = _create_client(
        client,
        auth_headers_admin,
        name="Mobile Filter Client",
        cin="BILL2002",
    )

    internet_subscriber_id = _create_subscriber(
        client,
        auth_headers_admin,
        client_id=internet_client_id,
        identifier="+212512340210",
        service_type="fiber",
    )
    mobile_subscriber_id = _create_subscriber(
        client,
        auth_headers_admin,
        client_id=mobile_client_id,
        identifier="+212612340211",
        service_type="mobile",
    )

    _create_contract(
        client,
        auth_headers_admin,
        client_id=internet_client_id,
        subscriber_id=internet_subscriber_id,
        offer_id=internet_offer_id,
        start_date="2026-02-01",
    )
    _create_contract(
        client,
        auth_headers_admin,
        client_id=mobile_client_id,
        subscriber_id=mobile_subscriber_id,
        offer_id=mobile_offer_id,
        start_date="2026-02-01",
    )

    run_response = client.post(
        "/api/v1/billing/runs",
        headers={**auth_headers_admin, "Idempotency-Key": "billing-run-filter-0001"},
        json={"period_start": "2026-02-01", "period_end": "2026-02-28"},
    )
    assert run_response.status_code == 200
    assert run_response.json()["invoice_count"] == 2

    all_invoices = client.get("/api/v1/invoices?page=1&size=20", headers=auth_headers_admin)
    assert all_invoices.status_code == 200
    assert all_invoices.json()["meta"]["total"] == 2

    client_filtered = client.get(
        f"/api/v1/invoices?page=1&size=20&client_id={internet_client_id}",
        headers=auth_headers_admin,
    )
    assert client_filtered.status_code == 200
    client_payload = client_filtered.json()
    assert client_payload["meta"]["total"] == 1
    assert client_payload["data"][0]["client_id"] == internet_client_id

    service_filtered = client.get(
        "/api/v1/invoices?page=1&size=20&service=mobile",
        headers=auth_headers_admin,
    )
    assert service_filtered.status_code == 200
    service_payload = service_filtered.json()
    assert service_payload["meta"]["total"] == 1
    assert service_payload["data"][0]["client_id"] == mobile_client_id

    offer_filtered = client.get(
        f"/api/v1/invoices?page=1&size=20&offer_id={internet_offer_id}",
        headers=auth_headers_admin,
    )
    assert offer_filtered.status_code == 200
    offer_payload = offer_filtered.json()
    assert offer_payload["meta"]["total"] == 1
    assert offer_payload["data"][0]["client_id"] == internet_client_id
