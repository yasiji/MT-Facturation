import { FormEvent, useEffect, useMemo, useState } from "react";

import "./LandingPage.css";

type ServiceCategory = "mobile" | "internet" | "landline";
type FlowType =
  | "subscribe_new_service"
  | "upgrade_or_downgrade_existing_service"
  | "check_billing_and_download_invoices";
type MobileMode = "use_existing" | "assign_new";
type NewStep = "offer" | "phone" | "identity" | "preview" | "done";
type PlanStep = "cin" | "offer" | "preview" | "done";
type BillingStep = "verify" | "invoices";

interface OfferSummary {
  id: string;
  name: string;
  service_category: ServiceCategory;
  service_type: string;
  monthly_fee: string;
  activation_fee: string;
}

interface OfferCategory {
  service_category: ServiceCategory;
  offers: OfferSummary[];
}

interface BootstrapResponse {
  offer_categories: OfferCategory[];
}

interface LookupSubscription {
  contract_id: string;
  service_identifier: string;
  service_category: ServiceCategory;
  current_offer: OfferSummary;
  eligible_offers: OfferSummary[];
}

interface LookupResponse {
  client: {
    cin: string;
    full_name: string;
    email: string | null;
    phone: string | null;
    address: string | null;
  };
  subscriptions: LookupSubscription[];
}

interface LookupVerificationResponse {
  cin: string;
  masked_contact: string;
  lookup_token: string;
  expires_at: string;
}

interface BillingInvoiceSummary {
  invoice_id: string;
  period_start: string;
  period_end: string;
  due_date: string;
  issued_at: string;
  status: string;
  currency: string;
  subtotal_amount: string;
  tax_amount: string;
  total_amount: string;
  document_download_url: string;
}

interface BillingLookupResponse {
  client: {
    cin: string;
    full_name: string;
    email: string | null;
    phone: string | null;
    address: string | null;
  };
  invoices: BillingInvoiceSummary[];
}

interface DocumentLinkResponse {
  contract_id: string;
  document_download_url: string;
}

interface SubmitResponse {
  contract: { id: string };
  client_cin: string;
  service_identifier: string;
  provisioning_mode: string;
  document_download_url: string | null;
}

interface ApiErrorEnvelope {
  error?: {
    message?: string;
    details?: {
      errors?: Array<{
        loc?: Array<string | number>;
        msg?: string;
      }>;
    };
  };
}

const DEFAULT_API_BASE_URL = (import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8010").trim();
const API_CANDIDATES = [
  DEFAULT_API_BASE_URL,
  "http://localhost:8010",
  "http://localhost:8000",
  "http://127.0.0.1:8010",
  "http://127.0.0.1:8000",
];

function uniqueCandidates(values: string[]): string[] {
  const unique: string[] = [];
  values.forEach((value) => {
    const normalized = value.trim();
    if (normalized && !unique.includes(normalized)) {
      unique.push(normalized);
    }
  });
  return unique;
}

function formatError(payload: ApiErrorEnvelope | undefined, fallback: string): string {
  const baseMessage = payload?.error?.message?.trim();
  const issue = payload?.error?.details?.errors?.[0];
  const issueMessage = issue?.msg?.trim();
  const issuePath = issue?.loc?.filter((part) => part !== "body").join(".");
  if (issueMessage) {
    return `${baseMessage ?? "Validation failed"}${issuePath ? ` (${issuePath})` : ""}: ${issueMessage}`;
  }
  return baseMessage || fallback;
}

async function resolveBaseUrl(): Promise<string> {
  const candidates = uniqueCandidates(API_CANDIDATES);
  for (const base of candidates) {
    try {
      const health = await fetch(`${base}/api/v1/health`);
      if (!health.ok) {
        continue;
      }
      const openApi = await fetch(`${base}/openapi.json`);
      if (!openApi.ok) {
        continue;
      }
      const payload = (await openApi.json()) as { paths?: Record<string, unknown> };
      if (payload.paths && Object.prototype.hasOwnProperty.call(payload.paths, "/api/v1/landing/bootstrap")) {
        return base;
      }
    } catch (error) {
      void error;
    }
  }
  throw new Error(`Could not connect to backend. Tried: ${candidates.join(", ")}`);
}

async function request<T>(base: string, path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${base}${path}`, init);
  if (!response.ok) {
    let payload: ApiErrorEnvelope | undefined;
    try {
      payload = (await response.json()) as ApiErrorEnvelope;
    } catch (error) {
      void error;
    }
    throw new Error(formatError(payload, `Request failed with status ${response.status}`));
  }
  if (response.status === 204) {
    return undefined as T;
  }
  return (await response.json()) as T;
}

function randomMoroccanNsn(kind: "mobile" | "landline"): string {
  const firstDigitOptions = kind === "mobile" ? ["6", "7"] : ["5", "8"];
  const firstDigit = firstDigitOptions[Math.floor(Math.random() * firstDigitOptions.length)];
  const suffix = Array.from({ length: 8 }, () => Math.floor(Math.random() * 10)).join("");
  return `${firstDigit}${suffix}`;
}

function normalizeMoroccanNumber(
  rawValue: string,
  kind: "mobile" | "landline",
): { canonical: string; nsn: string } | null {
  const digits = rawValue.replace(/\D/g, "");
  let nsn = digits;
  if (digits.startsWith("212")) {
    nsn = digits.slice(3);
  } else if (digits.startsWith("0")) {
    nsn = digits.slice(1);
  }

  if (!/^\d{9}$/.test(nsn)) {
    return null;
  }
  const first = nsn[0];
  const allowed = kind === "mobile" ? new Set(["6", "7"]) : new Set(["5", "8"]);
  if (!allowed.has(first)) {
    return null;
  }
  return { canonical: `+212${nsn}`, nsn };
}

function idempotencyKey(prefix: string): string {
  if (typeof crypto !== "undefined" && typeof crypto.randomUUID === "function") {
    return `${prefix}-${crypto.randomUUID()}`;
  }
  return `${prefix}-${Date.now()}-${Math.random().toString(16).slice(2)}`;
}

function LandingPage() {
  const [apiBaseUrl, setApiBaseUrl] = useState(DEFAULT_API_BASE_URL);
  const [busy, setBusy] = useState(false);
  const [banner, setBanner] = useState<{ kind: "ok" | "error"; text: string } | null>(null);
  const [bootstrap, setBootstrap] = useState<BootstrapResponse | null>(null);
  const [flow, setFlow] = useState<FlowType | null>(null);

  const [service, setService] = useState<ServiceCategory>("mobile");
  const [offerId, setOfferId] = useState("");
  const [newStep, setNewStep] = useState<NewStep>("offer");
  const [mobileMode, setMobileMode] = useState<MobileMode>("assign_new");
  const [existingMobileInput, setExistingMobileInput] = useState("");
  const [generatedMobileNsn, setGeneratedMobileNsn] = useState(() => randomMoroccanNsn("mobile"));
  const [generatedLandlineNsn, setGeneratedLandlineNsn] = useState(() =>
    randomMoroccanNsn("landline"),
  );
  const [cin, setCin] = useState("");
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [address, setAddress] = useState("");
  const [startDate, setStartDate] = useState(new Date().toISOString().slice(0, 10));
  const [commitmentMonths, setCommitmentMonths] = useState("12");
  const [newResult, setNewResult] = useState<SubmitResponse | null>(null);

  const [planStep, setPlanStep] = useState<PlanStep>("cin");
  const [lookupCin, setLookupCin] = useState("");
  const [lookupMaskedContact, setLookupMaskedContact] = useState("");
  const [lookupToken, setLookupToken] = useState("");
  const [lookup, setLookup] = useState<LookupResponse | null>(null);
  const [sourceContractId, setSourceContractId] = useState("");
  const [targetOfferId, setTargetOfferId] = useState("");
  const [planStartDate, setPlanStartDate] = useState(new Date().toISOString().slice(0, 10));
  const [planCommitmentMonths, setPlanCommitmentMonths] = useState("12");
  const [planResult, setPlanResult] = useState<SubmitResponse | null>(null);
  const [billingStep, setBillingStep] = useState<BillingStep>("verify");
  const [billingCin, setBillingCin] = useState("");
  const [billingMaskedContact, setBillingMaskedContact] = useState("");
  const [billingLookupToken, setBillingLookupToken] = useState("");
  const [billingLookup, setBillingLookup] = useState<BillingLookupResponse | null>(null);

  const offersForService = useMemo(
    () => bootstrap?.offer_categories.find((item) => item.service_category === service)?.offers ?? [],
    [bootstrap, service],
  );
  const selectedOffer = useMemo(
    () => offersForService.find((item) => item.id === offerId) ?? null,
    [offersForService, offerId],
  );
  const selectedSource = useMemo(
    () => lookup?.subscriptions.find((item) => item.contract_id === sourceContractId) ?? null,
    [lookup, sourceContractId],
  );
  const selectedTarget = useMemo(
    () => selectedSource?.eligible_offers.find((item) => item.id === targetOfferId) ?? null,
    [selectedSource, targetOfferId],
  );

  const normalizedExistingMobile = useMemo(
    () => normalizeMoroccanNumber(existingMobileInput, "mobile"),
    [existingMobileInput],
  );

  const previewIdentifier = useMemo(() => {
    if (service === "mobile") {
      if (mobileMode === "assign_new") {
        return `+212${generatedMobileNsn}`;
      }
      return normalizedExistingMobile?.canonical ?? existingMobileInput;
    }
    return `+212${generatedLandlineNsn}`;
  }, [
    service,
    mobileMode,
    generatedMobileNsn,
    generatedLandlineNsn,
    normalizedExistingMobile?.canonical,
    existingMobileInput,
  ]);

  async function withGuard(fn: () => Promise<void>) {
    setBusy(true);
    setBanner(null);
    try {
      await fn();
    } catch (error) {
      setBanner({ kind: "error", text: error instanceof Error ? error.message : "Unexpected error" });
    } finally {
      setBusy(false);
    }
  }

  useEffect(() => {
    void withGuard(async () => {
      const resolved = await resolveBaseUrl();
      setApiBaseUrl(resolved);
      setBootstrap(await request<BootstrapResponse>(resolved, "/api/v1/landing/bootstrap"));
      setBanner({ kind: "ok", text: `Connected to landing APIs (${resolved}).` });
    });
  }, []);

  function resetFlow(nextFlow: FlowType) {
    setFlow(nextFlow);
    setNewStep("offer");
    setPlanStep("cin");
    setBillingStep("verify");
    setOfferId("");
    setService("mobile");
    setMobileMode("assign_new");
    setExistingMobileInput("");
    setGeneratedMobileNsn(randomMoroccanNsn("mobile"));
    setGeneratedLandlineNsn(randomMoroccanNsn("landline"));
    setCin("");
    setFullName("");
    setEmail("");
    setAddress("");
    setStartDate(new Date().toISOString().slice(0, 10));
    setCommitmentMonths("12");
    setNewResult(null);
    setLookupCin("");
    setLookupMaskedContact("");
    setLookupToken("");
    setLookup(null);
    setSourceContractId("");
    setTargetOfferId("");
    setPlanStartDate(new Date().toISOString().slice(0, 10));
    setPlanCommitmentMonths("12");
    setPlanResult(null);
    setBillingCin("");
    setBillingMaskedContact("");
    setBillingLookupToken("");
    setBillingLookup(null);
  }

  function continueFromOffer() {
    if (!offerId) {
      setBanner({ kind: "error", text: "Select an offer before continuing." });
      return;
    }
    if (service === "mobile") {
      setNewStep("phone");
      return;
    }
    setNewStep("identity");
  }

  function continueFromPhoneCriteria() {
    setNewStep("identity");
  }

  function continueFromIdentity(event: FormEvent) {
    event.preventDefault();
    if (cin.trim().length < 4 || fullName.trim().length < 2) {
      setBanner({ kind: "error", text: "CIN and full name are required." });
      return;
    }
    if (service === "mobile" && mobileMode === "use_existing" && !normalizedExistingMobile) {
      setBanner({
        kind: "error",
        text: "Please provide a valid Moroccan mobile number in the phone field.",
      });
      return;
    }
    setNewStep("preview");
  }

  async function submitNew(event: FormEvent) {
    event.preventDefault();
    if (!selectedOffer) {
      setBanner({ kind: "error", text: "Selected offer is missing. Go back and reselect." });
      return;
    }

    await withGuard(async () => {
      const contactPhone =
        service === "mobile"
          ? mobileMode === "assign_new"
            ? `+212${generatedMobileNsn}`
            : normalizedExistingMobile?.canonical ?? null
          : `+212${generatedLandlineNsn}`;

      const payload: Record<string, unknown> = {
        service_category: service,
        offer_id: offerId,
        cin: cin.trim().toUpperCase(),
        full_name: fullName.trim(),
        email: email.trim() || null,
        address: address.trim() || null,
        contact_phone: contactPhone,
        contract_start_date: startDate,
      };
      if (commitmentMonths.trim()) {
        payload.commitment_months = Number(commitmentMonths);
      }

      if (service === "mobile") {
        payload.mobile_number_mode = mobileMode;
        if (mobileMode === "use_existing") {
          payload.existing_mobile_local_number =
            normalizedExistingMobile?.nsn ?? existingMobileInput.trim();
        } else {
          payload.requested_mobile_local_number = generatedMobileNsn;
        }
      } else {
        payload.home_landline_local_number = generatedLandlineNsn;
      }

      const result = await request<SubmitResponse>(apiBaseUrl, "/api/v1/landing/submit/new", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Idempotency-Key": idempotencyKey("landing-new"),
        },
        body: JSON.stringify(payload),
      });
      setNewResult(await ensureDocumentLink(result, payload.cin as string));
      setNewStep("done");
      setBanner({ kind: "ok", text: "Subscription confirmed and contract generated." });
    });
  }

  async function lookupByCin(event: FormEvent) {
    event.preventDefault();
    if (lookupCin.trim().length < 4) {
      setBanner({ kind: "error", text: "Enter a valid CIN." });
      return;
    }

    await withGuard(async () => {
      const verification = await request<LookupVerificationResponse>(
        apiBaseUrl,
        "/api/v1/landing/clients/verify-cin",
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            cin: lookupCin.trim().toUpperCase(),
          }),
        },
      );
      setLookupToken(verification.lookup_token);
      setLookupMaskedContact(verification.masked_contact);

      setLookup(
        await request<LookupResponse>(
          apiBaseUrl,
          `/api/v1/landing/clients/${encodeURIComponent(lookupCin.trim())}/subscriptions?lookup_token=${encodeURIComponent(verification.lookup_token)}`,
        ),
      );
      setSourceContractId("");
      setTargetOfferId("");
      setPlanStep("offer");
      setBanner({
        kind: "ok",
        text: `CIN verified (${verification.masked_contact}). Select your offer change.`,
      });
    });
  }

  async function submitPlan(event: FormEvent) {
    event.preventDefault();
    if (!lookup || !selectedSource || !selectedTarget) {
      setBanner({ kind: "error", text: "Select a source contract and target offer." });
      return;
    }

    await withGuard(async () => {
      const payload: Record<string, unknown> = {
        cin: lookup.client.cin,
        source_contract_id: selectedSource.contract_id,
        target_offer_id: selectedTarget.id,
        contract_start_date: planStartDate,
      };
      if (planCommitmentMonths.trim()) {
        payload.commitment_months = Number(planCommitmentMonths);
      }
      const result = await request<SubmitResponse>(apiBaseUrl, "/api/v1/landing/submit/plan-change", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Idempotency-Key": idempotencyKey("landing-plan"),
        },
        body: JSON.stringify(payload),
      });
      setPlanResult(
        await ensureDocumentLink(result, payload.cin as string),
      );
      setPlanStep("done");
      setBanner({ kind: "ok", text: "Offer change validated and applied." });
    });
  }

  async function lookupInvoicesByCin(event: FormEvent) {
    event.preventDefault();
    if (billingCin.trim().length < 4) {
      setBanner({ kind: "error", text: "Enter a valid CIN." });
      return;
    }

    await withGuard(async () => {
      const verification = await request<LookupVerificationResponse>(
        apiBaseUrl,
        "/api/v1/landing/clients/verify-cin",
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            cin: billingCin.trim().toUpperCase(),
          }),
        },
      );
      setBillingLookupToken(verification.lookup_token);
      setBillingMaskedContact(verification.masked_contact);

      const invoicesLookup = await request<BillingLookupResponse>(
        apiBaseUrl,
        `/api/v1/landing/clients/${encodeURIComponent(billingCin.trim())}/invoices?lookup_token=${encodeURIComponent(verification.lookup_token)}`,
      );
      setBillingLookup(invoicesLookup);
      setBillingStep("invoices");
      setBanner({
        kind: "ok",
        text: `CIN verified (${verification.masked_contact}). Billing history loaded.`,
      });
    });
  }

  function toDownloadUrl(path: string | null): string | null {
    if (!path) {
      return null;
    }
    if (path.startsWith("http://") || path.startsWith("https://")) {
      return path;
    }
    return `${apiBaseUrl}${path}`;
  }

  async function ensureDocumentLink(
    result: SubmitResponse,
    cinValue: string,
  ): Promise<SubmitResponse> {
    if (result.document_download_url) {
      return result;
    }
    try {
      const bodyPayload: Record<string, string> = {
        cin: cinValue.trim().toUpperCase(),
      };
      const link = await request<DocumentLinkResponse>(
        apiBaseUrl,
        `/api/v1/landing/contracts/${encodeURIComponent(result.contract.id)}/document-link`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(bodyPayload),
        },
      );
      return { ...result, document_download_url: link.document_download_url };
    } catch (error) {
      void error;
      return result;
    }
  }

  async function generateDocumentLinkForResult(
    result: SubmitResponse,
    setResult: (next: SubmitResponse) => void,
  ) {
    if (busy) {
      return;
    }
    await withGuard(async () => {
      const next = await ensureDocumentLink(result, result.client_cin);
      setResult(next);
      if (next.document_download_url) {
        setBanner({ kind: "ok", text: "Contract PDF is ready for download." });
      } else {
        setBanner({
          kind: "error",
          text: "Could not generate PDF link. Verify CIN and try again.",
        });
      }
    });
  }

  return (
    <main className="landing-shell">
      <header className="landing-hero">
        <p className="landing-kicker">MT Facturation</p>
        <h1>Client Subscription Portal</h1>
        <p>Dedicated onboarding and plan-change journey connected directly to platform APIs.</p>
        <div className="landing-meta">
          <span>API: {apiBaseUrl}</span>
          <a href="/">Operator workspace</a>
        </div>
      </header>

      {banner ? <section className={`landing-banner landing-banner-${banner.kind}`}>{banner.text}</section> : null}

      {!flow ? (
        <section className="landing-flow-picker">
          <button
            type="button"
            className="flow-card"
            disabled={busy || !bootstrap}
            onClick={() => resetFlow("subscribe_new_service")}
          >
            <h2>Subscribe New Service</h2>
            <p>Choose service and offer, select phone criteria, fill form, validate, subscribe.</p>
          </button>
          <button
            type="button"
            className="flow-card"
            disabled={busy || !bootstrap}
            onClick={() => resetFlow("upgrade_or_downgrade_existing_service")}
          >
            <h2>Upgrade / Downgrade</h2>
            <p>Enter CIN, choose current offer, then choose an eligible target offer.</p>
          </button>
          <button
            type="button"
            className="flow-card"
            disabled={busy || !bootstrap}
            onClick={() => resetFlow("check_billing_and_download_invoices")}
          >
            <h2>Check Billing & Invoices</h2>
            <p>Verify CIN, view monthly invoices, and download invoice PDFs securely.</p>
          </button>
        </section>
      ) : null}

      {flow === "subscribe_new_service" ? (
        <section className="landing-panel">
          <div className="landing-steps">
            <span className={newStep === "offer" ? "active" : ""}>1. Service & Offer</span>
            <span className={newStep === "phone" ? "active" : ""}>2. Phone Criteria</span>
            <span className={newStep === "identity" ? "active" : ""}>3. Personal Info</span>
            <span className={newStep === "preview" ? "active" : ""}>4. Validation</span>
            <span className={newStep === "done" ? "active" : ""}>5. Done</span>
          </div>

          {newStep === "offer" ? (
            <>
              <h2>Choose Service and Offer</h2>
              <div className="service-switch">
                {(["mobile", "internet", "landline"] as ServiceCategory[]).map((item) => (
                  <button
                    key={item}
                    type="button"
                    className={service === item ? "active" : ""}
                    onClick={() => {
                      setService(item);
                      setOfferId("");
                    }}
                  >
                    {item}
                  </button>
                ))}
              </div>
              <div className="offer-cards">
                {offersForService.map((item) => (
                  <button
                    key={item.id}
                    type="button"
                    className={`offer-card ${offerId === item.id ? "selected" : ""}`}
                    onClick={() => setOfferId(item.id)}
                  >
                    <strong>{item.name}</strong>
                    <span>{item.service_type}</span>
                    <span>Monthly {item.monthly_fee}</span>
                    <span>Other fees {item.activation_fee}</span>
                  </button>
                ))}
                {offersForService.length === 0 ? (
                  <p className="empty-text">No active offers available for this service.</p>
                ) : null}
              </div>
              <div className="landing-actions">
                <button type="button" onClick={() => setFlow(null)}>
                  Back
                </button>
                <button type="button" disabled={!offerId} onClick={continueFromOffer}>
                  Continue
                </button>
              </div>
            </>
          ) : null}

          {newStep === "phone" ? (
            <>
              <h2>Phone Criteria</h2>
              <p>
                Choose whether you want to keep an existing mobile number or receive a new one.
              </p>
              <div className="inline-choice">
                <span>Mobile Number Choice</span>
                <div>
                  <button
                    type="button"
                    className={mobileMode === "assign_new" ? "active" : ""}
                    onClick={() => {
                      setMobileMode("assign_new");
                      setGeneratedMobileNsn(randomMoroccanNsn("mobile"));
                    }}
                  >
                    New Number
                  </button>
                  <button
                    type="button"
                    className={mobileMode === "use_existing" ? "active" : ""}
                    onClick={() => setMobileMode("use_existing")}
                  >
                    Existing Number
                  </button>
                </div>
              </div>
              {mobileMode === "assign_new" ? (
                <p className="choice-preview">Generated mobile number: +212{generatedMobileNsn}</p>
              ) : (
                <>
                  <p className="choice-preview">
                    You will enter the existing mobile number in the next step (Personal Info).
                  </p>
                  <p className="choice-preview">
                    Accepted formats: <code>+212 6 55 33 44 22</code>, <code>06 55 33 44 22</code>,
                    <code> 07 55 33 44 22</code>
                  </p>
                </>
              )}
              <div className="landing-actions">
                <button type="button" onClick={() => setNewStep("offer")}>
                  Back
                </button>
                <button type="button" onClick={continueFromPhoneCriteria}>
                  Continue to Form
                </button>
              </div>
            </>
          ) : null}

          {newStep === "identity" ? (
            <>
              <h2>Personal Information</h2>
              <form className="landing-form-grid" onSubmit={continueFromIdentity}>
                <label>
                  CIN
                  <input value={cin} onChange={(event) => setCin(event.target.value)} required />
                </label>
                <label>
                  Full Name
                  <input value={fullName} onChange={(event) => setFullName(event.target.value)} required />
                </label>
                <label>
                  Email
                  <input type="email" value={email} onChange={(event) => setEmail(event.target.value)} />
                </label>
                <label>
                  Address
                  <input value={address} onChange={(event) => setAddress(event.target.value)} />
                </label>
                {service === "mobile" ? (
                  <label>
                    Phone Number
                    <input
                      className={mobileMode === "assign_new" ? "read-only" : ""}
                      disabled={mobileMode === "assign_new"}
                      value={mobileMode === "assign_new" ? `+212${generatedMobileNsn}` : existingMobileInput}
                      onChange={(event) => setExistingMobileInput(event.target.value)}
                      placeholder="+212..., 06..., or 07..."
                    />
                  </label>
                ) : (
                  <label>
                    Phone Number
                    <input
                      className="read-only"
                      disabled
                      value={`+212${generatedLandlineNsn}`}
                      onChange={() => undefined}
                    />
                  </label>
                )}
                <label>
                  Contract Start Date
                  <input
                    type="date"
                    value={startDate}
                    onChange={(event) => setStartDate(event.target.value)}
                    required
                  />
                </label>
                <label>
                  Commitment (months)
                  <input
                    type="number"
                    min={1}
                    max={60}
                    value={commitmentMonths}
                    onChange={(event) => setCommitmentMonths(event.target.value)}
                  />
                </label>
                <div className="landing-actions full-row">
                  <button type="button" onClick={() => setNewStep(service === "mobile" ? "phone" : "offer")}>
                    Back
                  </button>
                  <button type="submit">Continue to Validation</button>
                </div>
              </form>
            </>
          ) : null}

          {newStep === "preview" ? (
            <>
              <h2>Validation</h2>
              <div className="preview-grid">
                <article>
                  <h3>Offer</h3>
                  <p>{selectedOffer?.name}</p>
                  <p>{selectedOffer?.service_type}</p>
                  <p>Monthly {selectedOffer?.monthly_fee}</p>
                </article>
                <article>
                  <h3>Client</h3>
                  <p>CIN: {cin.toUpperCase()}</p>
                  <p>{fullName}</p>
                  <p>{email || "-"}</p>
                </article>
                <article>
                  <h3>Identifier</h3>
                  <p>{previewIdentifier}</p>
                </article>
              </div>
              <form onSubmit={submitNew}>
                <div className="landing-actions">
                  <button type="button" onClick={() => setNewStep("identity")}>
                    Back
                  </button>
                  <button type="submit" disabled={busy}>
                    Subscribe to Offer
                  </button>
                </div>
              </form>
            </>
          ) : null}

          {newStep === "done" && newResult ? (
            <section className="success-box">
              <h2>Subscription Confirmed</h2>
              <p>Contract ID: {newResult.contract.id}</p>
              <p>Client CIN: {newResult.client_cin}</p>
              <p>Service Identifier: {newResult.service_identifier}</p>
              <p>Mode: {newResult.provisioning_mode}</p>
              {newResult.document_download_url ? (
                <a href={toDownloadUrl(newResult.document_download_url) ?? undefined}>Download Contract PDF</a>
              ) : (
                <div className="landing-actions">
                  <p>PDF link is being prepared.</p>
                  <button
                    type="button"
                    onClick={() =>
                      void generateDocumentLinkForResult(
                        newResult,
                        (next) => setNewResult(next),
                      )
                    }
                  >
                    Generate PDF Link
                  </button>
                </div>
              )}
              <div className="landing-actions">
                <button type="button" onClick={() => resetFlow("subscribe_new_service")}>
                  Start another subscription
                </button>
                <button type="button" onClick={() => setFlow(null)}>
                  Back to flow selection
                </button>
              </div>
            </section>
          ) : null}
        </section>
      ) : null}

      {flow === "upgrade_or_downgrade_existing_service" ? (
        <section className="landing-panel">
          <div className="landing-steps">
            <span className={planStep === "cin" ? "active" : ""}>1. Verify</span>
            <span className={planStep === "offer" ? "active" : ""}>2. Select Offers</span>
            <span className={planStep === "preview" ? "active" : ""}>3. Validation</span>
            <span className={planStep === "done" ? "active" : ""}>4. Done</span>
          </div>

          {planStep === "cin" ? (
            <>
              <h2>Verify CIN</h2>
              <form className="landing-form-grid" onSubmit={lookupByCin}>
                <label>
                  CIN
                  <input value={lookupCin} onChange={(event) => setLookupCin(event.target.value)} required />
                </label>
                {lookupMaskedContact ? (
                  <p className="choice-preview">
                    Verification reference: {lookupMaskedContact}
                    {lookupToken ? " (active session)" : ""}
                  </p>
                ) : null}
                <div className="landing-actions full-row">
                  <button type="button" onClick={() => setFlow(null)}>
                    Back
                  </button>
                  <button type="submit" disabled={busy}>
                    Verify CIN and Find Offers
                  </button>
                </div>
              </form>
            </>
          ) : null}

          {planStep === "offer" ? (
            <>
              <h2>Current Offer and Target Offer</h2>
              <div className="dual-columns">
                <article>
                  <h3>Current Subscriptions</h3>
                  {lookup?.subscriptions.map((item) => (
                    <button
                      type="button"
                      key={item.contract_id}
                      className={`offer-card ${sourceContractId === item.contract_id ? "selected" : ""}`}
                      onClick={() => {
                        setSourceContractId(item.contract_id);
                        setTargetOfferId("");
                      }}
                    >
                      <strong>{item.current_offer.name}</strong>
                      <span>{item.service_category}</span>
                      <span>{item.service_identifier}</span>
                    </button>
                  ))}
                </article>
                <article>
                  <h3>Eligible Target Offers</h3>
                  {selectedSource?.eligible_offers.map((item) => (
                    <button
                      type="button"
                      key={item.id}
                      className={`offer-card ${targetOfferId === item.id ? "selected" : ""}`}
                      onClick={() => setTargetOfferId(item.id)}
                    >
                      <strong>{item.name}</strong>
                      <span>{item.service_type}</span>
                      <span>Monthly {item.monthly_fee}</span>
                    </button>
                  ))}
                  {selectedSource && selectedSource.eligible_offers.length === 0 ? (
                    <p className="empty-text">No eligible offers for this service right now.</p>
                  ) : null}
                </article>
              </div>
              <div className="landing-actions">
                <button type="button" onClick={() => setPlanStep("cin")}>
                  Back
                </button>
                <button
                  type="button"
                  disabled={!sourceContractId || !targetOfferId}
                  onClick={() => setPlanStep("preview")}
                >
                  Continue
                </button>
              </div>
            </>
          ) : null}

          {planStep === "preview" ? (
            <>
              <h2>Validation</h2>
              <form className="landing-form-grid" onSubmit={submitPlan}>
                <article className="preview-block">
                  <h3>Client</h3>
                  <p>{lookup?.client.full_name}</p>
                  <p>{lookup?.client.cin}</p>
                  <p>{lookup?.client.email || "-"}</p>
                  <p>{lookup?.client.phone || "-"}</p>
                </article>
                <article className="preview-block">
                  <h3>Current</h3>
                  <p>{selectedSource?.current_offer.name}</p>
                  <p>{selectedSource?.service_identifier}</p>
                </article>
                <article className="preview-block">
                  <h3>Target</h3>
                  <p>{selectedTarget?.name}</p>
                  <p>{selectedTarget?.monthly_fee}</p>
                </article>
                <label>
                  Effective Date
                  <input
                    type="date"
                    value={planStartDate}
                    onChange={(event) => setPlanStartDate(event.target.value)}
                    required
                  />
                </label>
                <label>
                  Commitment (months)
                  <input
                    type="number"
                    min={1}
                    max={60}
                    value={planCommitmentMonths}
                    onChange={(event) => setPlanCommitmentMonths(event.target.value)}
                  />
                </label>
                <div className="landing-actions full-row">
                  <button type="button" onClick={() => setPlanStep("offer")}>
                    Back
                  </button>
                  <button type="submit" disabled={busy}>
                    Validate New Offer
                  </button>
                </div>
              </form>
            </>
          ) : null}

          {planStep === "done" && planResult ? (
            <section className="success-box">
              <h2>Plan Change Confirmed</h2>
              <p>Contract ID: {planResult.contract.id}</p>
              <p>CIN: {planResult.client_cin}</p>
              <p>Service Identifier: {planResult.service_identifier}</p>
              {planResult.document_download_url ? (
                <a href={toDownloadUrl(planResult.document_download_url) ?? undefined}>Download Contract PDF</a>
              ) : (
                <div className="landing-actions">
                  <p>PDF link is being prepared.</p>
                  <button
                    type="button"
                    onClick={() =>
                      void generateDocumentLinkForResult(
                        planResult,
                        (next) => setPlanResult(next),
                      )
                    }
                  >
                    Generate PDF Link
                  </button>
                </div>
              )}
              <div className="landing-actions">
                <button type="button" onClick={() => resetFlow("upgrade_or_downgrade_existing_service")}>
                  Start another change
                </button>
                <button type="button" onClick={() => setFlow(null)}>
                  Back to flow selection
                </button>
              </div>
            </section>
          ) : null}
        </section>
      ) : null}

      {flow === "check_billing_and_download_invoices" ? (
        <section className="landing-panel">
          <div className="landing-steps">
            <span className={billingStep === "verify" ? "active" : ""}>1. Verify</span>
            <span className={billingStep === "invoices" ? "active" : ""}>2. My Invoices</span>
          </div>

          {billingStep === "verify" ? (
            <>
              <h2>Verify Billing Access</h2>
              <p className="panel-note">
                Telecom rule: invoices are issued at the beginning of each month for active
                services.
              </p>
              <form className="landing-form-grid" onSubmit={lookupInvoicesByCin}>
                <label>
                  CIN
                  <input
                    value={billingCin}
                    onChange={(event) => setBillingCin(event.target.value)}
                    required
                  />
                </label>
                {billingMaskedContact ? (
                  <p className="choice-preview">
                    Verification reference: {billingMaskedContact}
                    {billingLookupToken ? " (active session)" : ""}
                  </p>
                ) : null}
                <div className="landing-actions full-row">
                  <button type="button" onClick={() => setFlow(null)}>
                    Back
                  </button>
                  <button type="submit" disabled={busy}>
                    Verify CIN and Load Invoices
                  </button>
                </div>
              </form>
            </>
          ) : null}

          {billingStep === "invoices" ? (
            <>
              <h2>My Invoices</h2>
              <p className="panel-note">
                Issued monthly at period start. Download each invoice PDF from this list.
              </p>
              <div className="table-wrap">
                <table>
                  <thead>
                    <tr>
                      <th>Invoice</th>
                      <th>Period</th>
                      <th>Issued</th>
                      <th>Due</th>
                      <th>Total</th>
                      <th>Status</th>
                      <th>Document</th>
                    </tr>
                  </thead>
                  <tbody>
                    {billingLookup?.invoices.map((invoice) => (
                      <tr key={invoice.invoice_id}>
                        <td>{invoice.invoice_id.slice(0, 8)}</td>
                        <td>
                          {invoice.period_start} to {invoice.period_end}
                        </td>
                        <td>{new Date(invoice.issued_at).toLocaleDateString()}</td>
                        <td>{invoice.due_date}</td>
                        <td>
                          {invoice.total_amount} {invoice.currency}
                        </td>
                        <td>{invoice.status}</td>
                        <td>
                          <a href={toDownloadUrl(invoice.document_download_url) ?? undefined}>
                            Download Invoice PDF
                          </a>
                        </td>
                      </tr>
                    ))}
                    {billingLookup?.invoices.length === 0 ? (
                      <tr>
                        <td colSpan={7}>No invoices available yet for this CIN.</td>
                      </tr>
                    ) : null}
                  </tbody>
                </table>
              </div>
              <div className="landing-actions">
                <button type="button" onClick={() => setBillingStep("verify")}>
                  Back
                </button>
                <button type="button" onClick={() => resetFlow("check_billing_and_download_invoices")}>
                  Refresh
                </button>
                <button type="button" onClick={() => setFlow(null)}>
                  Back to flow selection
                </button>
              </div>
            </>
          ) : null}
        </section>
      ) : null}
    </main>
  );
}

export default LandingPage;
