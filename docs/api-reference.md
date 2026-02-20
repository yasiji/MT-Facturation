# MT-Facturation API Reference (v1)

Last Updated: 2026-02-20 12:06 UTC
Base Prefix: `/api/v1`

## Global Conventions

### Authentication Model
- Public endpoints:
  - `GET /api/v1/health`
  - All `/api/v1/landing/*` endpoints
  - OpenAPI/docs routes
- Protected endpoints:
  - All other `/api/v1/*` routes
- Accepted auth headers:
  - `Authorization: Bearer <actor_id[:role1,role2]>` (local dev format)
  - or `X-Actor-Id` with optional `X-Actor-Roles`

### Pagination Pattern
- List endpoints generally accept:
  - `page` (default `1`)
  - `size` (default `20`, max `100`)
  - optional `sort`, `filters`
- Paginated response format:
  - `data`: array
  - `meta`: `{ page, size, total, sort, filters }`

### Idempotency Pattern
- Critical write endpoints require header:
  - `Idempotency-Key` (minimum length: 8)
- Reusing same key with different payload returns `409 idempotency_key_payload_conflict`.

### Error Envelope
- Errors follow: `{ "error": { "code": "...", "message": "...", "details": { ... }, "trace_id": "..." } }`

## Health and Auth Endpoints

### GET `/api/v1/health`
- What it does: service health probe.
- Auth: public.
- Input: none.
- Response: `{ "status": "ok" }`.

### GET `/api/v1/me`
- What it does: returns caller identity extracted by middleware.
- Auth: required.
- Input: auth headers.
- Response: `{ "actor_id": "...", "roles": [...] }`.

### GET `/api/v1/admin/ping`
- What it does: admin-only authorization check endpoint.
- Auth: required with `admin` role.
- Input: auth headers.
- Response: `{ "status": "ok", "actor_id": "..." }`.

### GET `/api/v1/conventions/sample`
- What it does: sample endpoint showing standard paginated envelope format.
- Auth: required.
- Input: pagination query params.
- Response: paginated sample item list.

## Customer and Subscriber Endpoints

### POST `/api/v1/customers`
- What it does: creates a new client.
- Auth: required.
- Input body (`ClientCreate`):
  - `client_type`, `full_name` required.
  - optional `cin`, `address`, `email`, `phone`, `status`.
- Important behavior:
  - CIN is normalized to uppercase.
  - CIN must be unique; duplicates return `409 client_cin_conflict`.
- Response: created `ClientRead`.

### GET `/api/v1/customers`
- What it does: lists clients in reverse creation order.
- Auth: required.
- Input: pagination query params.
- Response: paginated `ClientRead` list.

### GET `/api/v1/customers/{client_id}`
- What it does: fetches one client by ID.
- Auth: required.
- Input: path `client_id`.
- Response: `ClientRead`.
- Errors: `404 client_not_found`.

### PUT `/api/v1/customers/{client_id}`
- What it does: updates mutable client fields.
- Auth: required.
- Input:
  - path `client_id`
  - body (`ClientUpdate`)
- Important behavior:
  - CIN uniqueness is re-checked if changed.
- Response: updated `ClientRead`.

### DELETE `/api/v1/customers/{client_id}`
- What it does: deletes a client record.
- Auth: required.
- Input: path `client_id`.
- Important behavior:
  - deletion is blocked if any contract, invoice, payment, or collection history exists.
  - blocked case returns `409 client_delete_blocked`.
- Response: `204 No Content`.

### POST `/api/v1/customers/{client_id}/subscribers`
- What it does: creates a subscriber line/device record for a client.
- Auth: required.
- Input:
  - path `client_id`
  - body (`SubscriberCreate`): `service_type`, `service_identifier`, optional `status`
- Important behavior:
  - `service_identifier` must be globally unique; conflicts return `409 subscriber_identifier_conflict`.
- Response: created `SubscriberRead`.

### GET `/api/v1/customers/{client_id}/subscribers`
- What it does: lists subscribers for one client.
- Auth: required.
- Input: path `client_id` + pagination query params.
- Response: paginated `SubscriberRead` list.

### GET `/api/v1/subscribers/{subscriber_id}`
- What it does: gets a subscriber by ID.
- Auth: required.
- Input: path `subscriber_id`.
- Response: `SubscriberRead`.

### PUT `/api/v1/subscribers/{subscriber_id}`
- What it does: updates subscriber fields (primarily lifecycle status).
- Auth: required.
- Input:
  - path `subscriber_id`
  - body (`SubscriberUpdate`)
- Response: updated `SubscriberRead`.

## Catalog (Offers) Endpoints

### POST `/api/v1/offers`
- What it does: creates an offer.
- Auth: required.
- Input body (`OfferCreate`):
  - commercial fields: `name`, `monthly_fee`, `activation_fee`, validity dates.
  - service model fields vary by `service_category`.
- Important behavior:
  - uniqueness by `(name, service_category, version)`.
  - strict service-component validation:
    - mobile needs data and/or calls component.
    - internet must choose exactly one access type (`fiber` or `adsl`) and auto-includes landline.
    - landline requires at least one landline component.
- Response: created `OfferRead`.

### GET `/api/v1/offers`
- What it does: lists offers.
- Auth: required.
- Input: pagination query params.
- Response: paginated `OfferRead` list.

### GET `/api/v1/offer-categories`
- What it does: grouped catalog view by service category.
- Auth: required.
- Input: none.
- Response: `OfferCategoryRead[]`.

### GET `/api/v1/offer-families` (Deprecated)
- What it does: backward-compatible alias for grouped categories.
- Auth: required.
- Input: none.
- Response: same as `/offer-categories`.

### GET `/api/v1/offers/{offer_id}`
- What it does: fetches an offer by ID.
- Auth: required.
- Input: path `offer_id`.
- Response: `OfferRead`.

### PUT `/api/v1/offers/{offer_id}`
- What it does: updates offer fields.
- Auth: required.
- Input:
  - path `offer_id`
  - body (`OfferUpdate`)
- Important behavior:
  - merged payload is revalidated against full `OfferCreate` rules before saving.
- Response: updated `OfferRead`.

### DELETE `/api/v1/offers/{offer_id}`
- What it does: deletes an offer.
- Auth: required.
- Input: path `offer_id`.
- Important behavior:
  - blocked if contract history exists for the offer (`409 offer_delete_blocked`).
- Response: `204 No Content`.

## Contract Endpoints

### POST `/api/v1/contracts/provision`
- What it does: orchestrated contract provisioning (new contract or upgrade).
- Auth: required.
- Input body (`ContractProvisionRequest`):
  - always includes `offer_id`, `contract_start_date`, and client reference (`client_id` or `client` payload).
  - optional subscriber reference/payload depending on intent.
  - `provisioning_intent`: `auto`, `upgrade`, `new_line`.
- Important behavior:
  - validates offer active/validity window.
  - auto mode can detect upgrade vs new contract.
  - handles disambiguation errors when multiple upgrade candidates exist.
  - upgrades now apply selected `contract_start_date` to target contract start date.
  - writes contract audit events.
- Response (`ContractProvisionResult`): contract plus flags `created_client`, `created_subscriber`, and `provisioning_mode`.

### POST `/api/v1/contracts`
- What it does: manual direct contract creation (without auto orchestration decisions).
- Auth: required.
- Input body (`ContractCreate`): `client_id`, `subscriber_id`, `offer_id`, dates/status.
- Important behavior:
  - enforces subscriber ownership and offer/subscriber compatibility.
  - blocks if subscriber already has open contract.
  - writes `contract_created` audit event.
- Response: created `ContractRead`.

### GET `/api/v1/contracts`
- What it does: lists contracts.
- Auth: required.
- Input: pagination query params.
- Response: paginated `ContractRead` list.

### GET `/api/v1/contracts/{contract_id}`
- What it does: gets one contract.
- Auth: required.
- Input: path `contract_id`.
- Response: `ContractRead`.

### PUT `/api/v1/contracts/{contract_id}/status`
- What it does: changes contract lifecycle status.
- Auth: required.
- Input:
  - path `contract_id`
  - body (`ContractStatusUpdate`)
- Important behavior:
  - enforces transition matrix (`draft/active/suspended/terminated`).
  - writes `contract_status_changed` audit event.
- Response: updated `ContractRead`.

### PUT `/api/v1/contracts/{contract_id}/offer`
- What it does: changes contract offer.
- Auth: required.
- Input:
  - path `contract_id`
  - body (`ContractOfferUpdate`)
- Important behavior:
  - validates subscriber-offer compatibility.
  - writes `contract_offer_changed` audit event.
- Response: updated `ContractRead`.

### GET `/api/v1/contracts/{contract_id}/audit`
- What it does: returns chronological contract audit trail.
- Auth: required.
- Input: path `contract_id`.
- Response: `ContractAuditEventRead[]`.

## Landing (Client-Facing Public) Endpoints

### GET `/api/v1/landing/bootstrap`
- What it does: returns landing entry metadata.
- Auth: public.
- Input: none.
- Response (`LandingBootstrapResponse`):
  - available flow options
  - service list
  - active offers grouped by `mobile`, `internet`, `landline`.

### POST `/api/v1/landing/drafts`
- What it does: stores an in-progress landing draft.
- Auth: public.
- Input body (`LandingDraftCreate`): flow type, step, optional CIN, arbitrary payload, status.
- Response: `LandingDraftRead`.

### GET `/api/v1/landing/drafts/{draft_id}`
- What it does: retrieves a stored draft.
- Auth: public.
- Input: path `draft_id`.
- Response: `LandingDraftRead`.
- Errors: `404 landing_draft_not_found`.

### PUT `/api/v1/landing/drafts/{draft_id}`
- What it does: partially updates draft step/CIN/payload/status.
- Auth: public.
- Input:
  - path `draft_id`
  - body (`LandingDraftUpdate`)
- Response: updated `LandingDraftRead`.

### POST `/api/v1/landing/clients/verify-cin`
- What it does: CIN-only verification bootstrap for self-service lookup.
- Auth: public.
- Input body (`LandingCinLookupRequest`): `cin`.
- Response (`LandingLookupVerificationResponse`):
  - normalized `cin`
  - masked reference (`masked_contact`)
  - signed short-lived `lookup_token`
  - `expires_at`
- Important behavior:
  - client must exist by CIN (`404 landing_client_not_found` otherwise).

### GET `/api/v1/landing/clients/{cin}/subscriptions?lookup_token=...`
- What it does: returns active subscriptions for a verified CIN.
- Auth: public with valid lookup token.
- Input:
  - path `cin`
  - query `lookup_token`
- Response (`LandingClientLookupResponse`):
  - masked client summary
  - current active subscriptions
  - eligible target offers in same service.
- Important behavior:
  - token CIN must match path CIN; mismatch returns `403 landing_lookup_token_mismatch`.

### GET `/api/v1/landing/clients/{cin}/invoices?lookup_token=...`
- What it does: returns invoice history for verified CIN.
- Auth: public with valid lookup token.
- Input: path `cin` + query `lookup_token`.
- Response (`LandingInvoiceLookupResponse`):
  - masked client summary
  - invoices with signed invoice document URLs.

### POST `/api/v1/landing/submit/new`
- What it does: final submit for new subscription flow.
- Auth: public.
- Required header: `Idempotency-Key`.
- Input body (`LandingNewSubscriptionSubmitRequest`):
  - identity: `cin`, `full_name`
  - subscription choice: `service_category`, `offer_id`
  - dates: `contract_start_date`, optional `commitment_months`
  - service-specific identifier fields:
    - mobile: `mobile_number_mode` plus existing/requested mobile number logic
    - internet/landline: required `home_landline_local_number`
- Important behavior:
  - CIN reconciliation decides create client or reuse existing client.
  - backend normalizes Moroccan phone/landline formats.
  - identifier uniqueness is enforced.
  - triggers provisioning orchestration and contract PDF generation.
  - idempotent replay supported.
- Response (`LandingSubmitResult`): contract info, CIN, service identifier, creation flags, provisioning mode, and document URL.

### POST `/api/v1/landing/submit/plan-change`
- What it does: final submit for upgrade/downgrade flow.
- Auth: public.
- Required header: `Idempotency-Key`.
- Input body (`LandingPlanChangeSubmitRequest`):
  - `cin`, `source_contract_id`, `target_offer_id`, `contract_start_date`, optional `commitment_months`.
- Important behavior:
  - source contract must belong to CIN client.
  - target offer must be in same service category.
  - executes upgrade provisioning mode.
  - selected `contract_start_date` is applied as upgraded contract effective start date.
  - generates/returns contract PDF link.
- Response: `LandingSubmitResult`.

### POST `/api/v1/landing/contracts/{contract_id}/document-link`
- What it does: returns (or regenerates) a downloadable contract PDF URL for a CIN-owned contract.
- Auth: public.
- Input:
  - path `contract_id`
  - body (`LandingContractDocumentLinkRequest`): `cin`
- Important behavior:
  - CIN must match contract owner (`403 landing_contract_client_mismatch` on mismatch).
  - if PDF missing, system generates it and stores metadata.
- Response (`LandingContractDocumentLinkResponse`): `contract_id`, `document_download_url`.

### GET `/api/v1/landing/contracts/{contract_id}/document?token=...`
- What it does: downloads contract PDF.
- Auth: public with signed document token.
- Input:
  - path `contract_id`
  - query `token`
- Response: file stream (`application/pdf`).
- Important behavior:
  - token is validated for purpose, CIN ownership, and contract match.

### GET `/api/v1/landing/invoices/{invoice_id}/document?token=...`
- What it does: downloads invoice PDF from landing flow.
- Auth: public with signed invoice document token.
- Input: path `invoice_id` + query `token`.
- Response: file stream (`application/pdf`).

## Billing Endpoints

### POST `/api/v1/billing/runs`
- What it does: executes one billing cycle for a given period.
- Auth: required.
- Required header: `Idempotency-Key`.
- Input body (`BillingRunRequest`): `period_start`, `period_end`, `due_days`, `tax_rate`.
- Important behavior:
  - idempotent by key+payload hash.
  - invoices are grouped per client from active contracts billable in the period.
  - generates recurring lines and activation lines (activation only if contract start is within billing period).
  - issues invoice PDFs and stores file metadata.
- Response (`BillingRunResult`): run id, totals, invoice ids, replay flag.

### GET `/api/v1/invoices`
- What it does: lists invoices with optional filters.
- Auth: required.
- Input:
  - pagination query params
  - optional `client_id`
  - optional `service` in `mobile|internet|landline`
  - optional `offer_id`
- Response: paginated `InvoiceRead` list.

### GET `/api/v1/invoices/{invoice_id}`
- What it does: gets invoice header plus line details.
- Auth: required.
- Input: path `invoice_id`.
- Response: `InvoiceDetailRead` (invoice + `lines[]`).

### GET `/api/v1/invoices/{invoice_id}/pdf`
- What it does: downloads invoice PDF.
- Auth: required.
- Input: path `invoice_id`.
- Response: file stream (`application/pdf`).
- Important behavior:
  - if file metadata exists but file missing, system attempts regeneration from invoice lines.

## Collections Endpoints

### POST `/api/v1/collections/payments`
- What it does: records a payment against an invoice and allocates it.
- Auth: required.
- Required header: `Idempotency-Key`.
- Input body (`PaymentCreate`): `invoice_id`, `amount`, `payment_date`, `method`, optional `reference`, `note`.
- Important behavior:
  - prevents overpayment (`422 payment_exceeds_outstanding`).
  - blocks payment on void/already-paid invoice.
  - synchronizes invoice status and collection case lifecycle.
  - marks client delinquency state accordingly.
- Response (`PaymentAllocationResult`): payment record, new invoice status, outstanding amount, allocation state, collection case status.

### POST `/api/v1/collections/invoices/{invoice_id}/approve-paid`
- What it does: operator shortcut to settle full outstanding balance of an invoice.
- Auth: required.
- Required header: `Idempotency-Key`.
- Input:
  - path `invoice_id`
  - body (`InvoicePaymentApprovalRequest`) with optional date/method/reference/note.
- Important behavior:
  - internally creates a full-amount posted payment via same allocation path as standard payment.
- Response: `PaymentAllocationResult`.

### GET `/api/v1/collections/payments`
- What it does: lists posted payments.
- Auth: required.
- Input:
  - pagination query params
  - optional `invoice_id`
  - optional `client_id`
- Response: paginated `PaymentRead` list.

### GET `/api/v1/collections/cases`
- What it does: lists collection cases.
- Auth: required.
- Input:
  - pagination query params
  - optional `status`, `aging_bucket`, `client_id`
- Important behavior:
  - endpoint first synchronizes overdue states before returning results.
- Response: paginated `CollectionCaseRead` list.

### GET `/api/v1/collections/cases/{case_id}/actions`
- What it does: returns action history for one case.
- Auth: required.
- Input: path `case_id`.
- Response: `CollectionCaseActionRead[]` (latest first).

### PUT `/api/v1/collections/cases/{case_id}/status`
- What it does: changes case status manually.
- Auth: required.
- Input:
  - path `case_id`
  - body (`CollectionCaseStatusUpdate`) with optional note.
- Important behavior:
  - writes an action entry `status_updated`.
- Response: updated `CollectionCaseRead`.

### POST `/api/v1/collections/cases/{case_id}/actions`
- What it does: appends a manual action to a collection case.
- Auth: required.
- Input:
  - path `case_id`
  - body (`CollectionCaseActionCreate`): `action_type`, optional note.
- Important behavior:
  - `note` action requires non-empty note.
  - reminder/warning actions can transition case from `open` to `in_progress`.
- Response: created `CollectionCaseActionRead`.

### GET `/api/v1/collections/overview`
- What it does: returns collections KPI snapshot.
- Auth: required.
- Input: none.
- Important behavior:
  - synchronizes overdue states before computing metrics.
- Response (`CollectionOverviewRead`):
  - open and in-progress case counts
  - overdue invoice count
  - total outstanding
  - outstanding totals by aging bucket.

