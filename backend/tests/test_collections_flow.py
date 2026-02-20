from datetime import date
from decimal import Decimal

from fastapi.testclient import TestClient


def _create_offer(
    client: TestClient,
    headers: dict[str, str],
    *,
    name: str,
    monthly_fee: str = "120.00",
) -> str:
    response = client.post(
        "/api/v1/offers",
        headers=headers,
        json={
            "name": name,
            "service_category": "internet",
            "internet_access_type": "fiber",
            "internet_fiber_speed_mbps": 200,
            "internet_tv_included": True,
            "version": 1,
            "monthly_fee": monthly_fee,
            "activation_fee": "0.00",
            "status": "active",
            "valid_from": "2025-01-01",
            "valid_to": None,
        },
    )
    assert response.status_code == 200
    return response.json()["id"]


def _create_client(client: TestClient, headers: dict[str, str], *, cin: str, name: str) -> str:
    response = client.post(
        "/api/v1/customers",
        headers=headers,
        json={
            "cin": cin,
            "client_type": "individual",
            "full_name": name,
            "email": f"{cin.lower()}@example.com",
            "phone": "+212612345000",
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
) -> str:
    response = client.post(
        f"/api/v1/customers/{client_id}/subscribers",
        headers=headers,
        json={"service_type": "fiber", "service_identifier": identifier, "status": "active"},
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
) -> str:
    response = client.post(
        "/api/v1/contracts",
        headers=headers,
        json={
            "client_id": client_id,
            "subscriber_id": subscriber_id,
            "offer_id": offer_id,
            "contract_start_date": "2025-10-01",
            "status": "active",
        },
    )
    assert response.status_code == 200
    return response.json()["id"]


def _run_billing(
    client: TestClient,
    headers: dict[str, str],
    *,
    key: str,
    period_start: str,
    period_end: str,
    tax_rate: str = "0.10",
) -> str:
    response = client.post(
        "/api/v1/billing/runs",
        headers={**headers, "Idempotency-Key": key},
        json={
            "period_start": period_start,
            "period_end": period_end,
            "due_days": 15,
            "tax_rate": tax_rate,
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["invoice_count"] == 1
    return payload["invoice_ids"][0]


def _setup_overdue_invoice(
    client: TestClient,
    headers: dict[str, str],
    *,
    cin: str,
    invoice_period_start: str = "2025-11-01",
    invoice_period_end: str = "2025-11-30",
) -> tuple[str, str]:
    offer_id = _create_offer(client, headers, name=f"Collections Offer {cin}")
    client_id = _create_client(client, headers, cin=cin, name=f"Collections {cin}")
    subscriber_id = _create_subscriber(
        client,
        headers,
        client_id=client_id,
        identifier=f"+21251234{cin[-4:]}",
    )
    _create_contract(
        client,
        headers,
        client_id=client_id,
        subscriber_id=subscriber_id,
        offer_id=offer_id,
    )
    invoice_id = _run_billing(
        client,
        headers,
        key=f"billing-{cin}",
        period_start=invoice_period_start,
        period_end=invoice_period_end,
    )
    return client_id, invoice_id


def test_collections_partial_then_full_settlement_updates_case_and_client_flag(
    client: TestClient,
    auth_headers_admin: dict[str, str],
) -> None:
    client_id, invoice_id = _setup_overdue_invoice(client, auth_headers_admin, cin="COLL1001")

    cases_response = client.get(
        "/api/v1/collections/cases?page=1&size=20",
        headers=auth_headers_admin,
    )
    assert cases_response.status_code == 200
    cases_payload = cases_response.json()
    assert cases_payload["meta"]["total"] == 1
    case_entry = cases_payload["data"][0]
    assert case_entry["invoice_id"] == invoice_id
    assert case_entry["status"] == "open"
    assert case_entry["aging_bucket"] in {"1_30", "31_60", "61_90", "90_plus"}
    case_id = case_entry["id"]

    client_response = client.get(f"/api/v1/customers/{client_id}", headers=auth_headers_admin)
    assert client_response.status_code == 200
    assert client_response.json()["is_delinquent"] is True

    partial_payment = client.post(
        "/api/v1/collections/payments",
        headers={**auth_headers_admin, "Idempotency-Key": "payment-coll-1001-a"},
        json={
            "invoice_id": invoice_id,
            "amount": "50.00",
            "payment_date": date.today().isoformat(),
            "method": "cash",
        },
    )
    assert partial_payment.status_code == 200
    partial_payload = partial_payment.json()
    assert partial_payload["allocation_state"] == "partial"
    assert partial_payload["invoice_status"] == "overdue"
    assert Decimal(partial_payload["outstanding_amount"]) > Decimal("0.00")

    remaining = partial_payload["outstanding_amount"]
    full_payment = client.post(
        "/api/v1/collections/payments",
        headers={**auth_headers_admin, "Idempotency-Key": "payment-coll-1001-b"},
        json={
            "invoice_id": invoice_id,
            "amount": remaining,
            "payment_date": date.today().isoformat(),
            "method": "bank_transfer",
            "reference": "TRX-1001",
        },
    )
    assert full_payment.status_code == 200
    full_payload = full_payment.json()
    assert full_payload["allocation_state"] == "full"
    assert full_payload["invoice_status"] == "paid"
    assert Decimal(full_payload["outstanding_amount"]) == Decimal("0.00")

    open_cases_response = client.get(
        "/api/v1/collections/cases?page=1&size=20&status=open",
        headers=auth_headers_admin,
    )
    assert open_cases_response.status_code == 200
    assert open_cases_response.json()["meta"]["total"] == 0

    actions_response = client.get(
        f"/api/v1/collections/cases/{case_id}/actions",
        headers=auth_headers_admin,
    )
    assert actions_response.status_code == 200
    action_types = [entry["action_type"] for entry in actions_response.json()]
    assert "case_opened" in action_types
    assert "payment_recorded" in action_types
    assert "case_resolved" in action_types

    client_after_response = client.get(f"/api/v1/customers/{client_id}", headers=auth_headers_admin)
    assert client_after_response.status_code == 200
    assert client_after_response.json()["is_delinquent"] is False


def test_collections_payment_idempotency_replay_and_conflict(
    client: TestClient,
    auth_headers_admin: dict[str, str],
) -> None:
    _, invoice_id = _setup_overdue_invoice(client, auth_headers_admin, cin="COLL1002")

    endpoint = "/api/v1/collections/payments"
    headers = {**auth_headers_admin, "Idempotency-Key": "payment-coll-1002"}
    payload = {
        "invoice_id": invoice_id,
        "amount": "10.00",
        "payment_date": date.today().isoformat(),
        "method": "wallet",
    }

    first = client.post(endpoint, headers=headers, json=payload)
    assert first.status_code == 200
    assert first.json()["idempotency_replayed"] is False

    second = client.post(endpoint, headers=headers, json=payload)
    assert second.status_code == 200
    assert second.json()["idempotency_replayed"] is True
    assert second.json()["payment"]["id"] == first.json()["payment"]["id"]

    conflict = client.post(
        endpoint,
        headers=headers,
        json={**payload, "amount": "12.00"},
    )
    assert conflict.status_code == 409
    assert conflict.json()["error"]["code"] == "idempotency_key_payload_conflict"


def test_collections_reminder_and_warning_actions_emit_hooks(
    client: TestClient,
    auth_headers_admin: dict[str, str],
) -> None:
    _, _ = _setup_overdue_invoice(client, auth_headers_admin, cin="COLL1003")
    cases_response = client.get(
        "/api/v1/collections/cases?page=1&size=20",
        headers=auth_headers_admin,
    )
    assert cases_response.status_code == 200
    case_id = cases_response.json()["data"][0]["id"]

    reminder = client.post(
        f"/api/v1/collections/cases/{case_id}/actions",
        headers=auth_headers_admin,
        json={"action_type": "reminder_sent", "note": "SMS reminder sent"},
    )
    assert reminder.status_code == 200
    assert reminder.json()["action_type"] == "reminder_sent"

    warning = client.post(
        f"/api/v1/collections/cases/{case_id}/actions",
        headers=auth_headers_admin,
        json={"action_type": "warning_sent", "note": "Final warning sent"},
    )
    assert warning.status_code == 200
    assert warning.json()["action_type"] == "warning_sent"

    case_list = client.get(
        "/api/v1/collections/cases?page=1&size=20&status=in_progress",
        headers=auth_headers_admin,
    )
    assert case_list.status_code == 200
    assert case_list.json()["meta"]["total"] == 1


def test_collections_invoice_approve_paid_marks_invoice_settled(
    client: TestClient,
    auth_headers_admin: dict[str, str],
) -> None:
    client_id, invoice_id = _setup_overdue_invoice(client, auth_headers_admin, cin="COLL1004")

    # Trigger overdue sync first to ensure case/delinquency are present before approval.
    sync_response = client.get(
        "/api/v1/collections/cases?page=1&size=20",
        headers=auth_headers_admin,
    )
    assert sync_response.status_code == 200
    assert sync_response.json()["meta"]["total"] == 1

    approval = client.post(
        f"/api/v1/collections/invoices/{invoice_id}/approve-paid",
        headers={**auth_headers_admin, "Idempotency-Key": "approval-coll-1004"},
        json={
            "method": "other",
            "note": "Manual approval of monthly bill",
        },
    )
    assert approval.status_code == 200
    payload = approval.json()
    assert payload["allocation_state"] == "full"
    assert payload["invoice_status"] == "paid"
    assert Decimal(payload["outstanding_amount"]) == Decimal("0.00")
    assert payload["idempotency_replayed"] is False

    replay = client.post(
        f"/api/v1/collections/invoices/{invoice_id}/approve-paid",
        headers={**auth_headers_admin, "Idempotency-Key": "approval-coll-1004"},
        json={},
    )
    assert replay.status_code == 200
    replay_payload = replay.json()
    assert replay_payload["idempotency_replayed"] is True
    assert replay_payload["payment"]["id"] == payload["payment"]["id"]

    invoice_detail = client.get(f"/api/v1/invoices/{invoice_id}", headers=auth_headers_admin)
    assert invoice_detail.status_code == 200
    assert invoice_detail.json()["status"] == "paid"

    client_after_response = client.get(f"/api/v1/customers/{client_id}", headers=auth_headers_admin)
    assert client_after_response.status_code == 200
    assert client_after_response.json()["is_delinquent"] is False
