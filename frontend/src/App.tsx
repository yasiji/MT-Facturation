import { FormEvent, useEffect, useMemo, useState } from "react";

import "./App.css";

type ClientType = "individual" | "business";
type ClientStatus = "active" | "suspended" | "terminated";
type SubscriberType = "mobile" | "fiber" | "adsl" | "tv" | "addon" | "landline";
type SubscriberStatus = "active" | "suspended" | "terminated";
type OfferStatus = "active" | "retired";
type OfferServiceCategory = "mobile" | "internet" | "landline";
type InternetAccessType = "fiber" | "adsl";
type ContractStatus = "draft" | "active" | "suspended" | "terminated";
type InvoiceStatus = "issued" | "paid" | "overdue" | "void";
type PaymentMethod = "cash" | "card" | "bank_transfer" | "wallet" | "other";
type CollectionCaseStatus = "open" | "in_progress" | "resolved" | "closed";
type CollectionCaseStatusFilter = CollectionCaseStatus | "all";
type AgingBucket = "current" | "1_30" | "31_60" | "61_90" | "90_plus";
type AgingBucketFilter = AgingBucket | "all";
type CollectionActionType =
  | "case_opened"
  | "case_reopened"
  | "payment_recorded"
  | "status_updated"
  | "reminder_sent"
  | "warning_sent"
  | "note"
  | "case_resolved"
  | "case_closed";
type ViewTab = "contracts" | "clients" | "offers" | "invoices" | "collections";
type ContractClientMode = "existing" | "new";

interface Client {
  id: string;
  client_type: ClientType;
  full_name: string;
  address: string | null;
  email: string | null;
  phone: string | null;
  is_delinquent: boolean;
  delinquent_since: string | null;
  status: ClientStatus;
  created_at: string;
  updated_at: string;
}

interface Subscriber {
  id: string;
  client_id: string;
  service_type: SubscriberType;
  service_identifier: string;
  status: SubscriberStatus;
  created_at: string;
  updated_at: string;
}

interface Offer {
  id: string;
  name: string;
  service_category: OfferServiceCategory;
  service_type: SubscriberType;
  mobile_data_gb: number | null;
  mobile_calls_hours: number | null;
  internet_access_type: InternetAccessType | null;
  internet_fiber_speed_mbps: number | null;
  internet_adsl_speed_mbps: number | null;
  internet_landline_included: boolean;
  internet_tv_included: boolean;
  landline_national_included: boolean;
  landline_international_hours: number | null;
  landline_phone_hours: number | null;
  version: number;
  monthly_fee: string;
  activation_fee: string;
  status: OfferStatus;
  valid_from: string;
  valid_to: string | null;
  created_at: string;
  updated_at: string;
}

interface Contract {
  id: string;
  client_id: string;
  subscriber_id: string;
  offer_id: string;
  status: ContractStatus;
  start_date: string;
  end_date: string | null;
  commitment_months: number | null;
  activated_at: string | null;
  terminated_at: string | null;
  created_at: string;
  updated_at: string;
}

interface InvoiceLine {
  id: string;
  invoice_id: string;
  contract_id: string;
  line_type: "recurring" | "activation";
  description: string;
  quantity: number;
  unit_amount: string;
  line_total: string;
  created_at: string;
}

interface Invoice {
  id: string;
  billing_run_id: string;
  client_id: string;
  period_start: string;
  period_end: string;
  due_date: string;
  status: InvoiceStatus;
  currency: string;
  subtotal_amount: string;
  tax_amount: string;
  total_amount: string;
  issued_at: string;
  pdf_file_name: string | null;
  created_at: string;
  updated_at: string;
}

interface InvoiceDetail extends Invoice {
  lines: InvoiceLine[];
}

interface Payment {
  id: string;
  invoice_id: string;
  client_id: string;
  amount: string;
  currency: string;
  payment_date: string;
  method: PaymentMethod;
  reference: string | null;
  note: string | null;
  status: "posted" | "reversed";
  created_at: string;
}

interface PaymentAllocationResult {
  payment: Payment;
  invoice_status: InvoiceStatus;
  outstanding_amount: string;
  allocation_state: "partial" | "full";
  collection_case_status: CollectionCaseStatus | null;
  idempotency_replayed: boolean;
}

interface CollectionCase {
  id: string;
  invoice_id: string;
  client_id: string;
  status: CollectionCaseStatus;
  reason: string;
  days_past_due: number;
  aging_bucket: AgingBucket;
  outstanding_amount: string;
  opened_at: string;
  last_action_at: string | null;
  closed_at: string | null;
  created_at: string;
  updated_at: string;
}

interface CollectionCaseAction {
  id: string;
  case_id: string;
  action_type: CollectionActionType;
  actor_id: string | null;
  note: string | null;
  payload: string;
  created_at: string;
}

interface CollectionOverview {
  open_cases: number;
  in_progress_cases: number;
  overdue_invoices: number;
  total_outstanding_amount: string;
  bucket_totals: Record<AgingBucket, string>;
}

interface BillingRunResult {
  billing_run_id: string;
  period_start: string;
  period_end: string;
  invoice_count: number;
  subtotal_amount: string;
  tax_amount: string;
  total_amount: string;
  invoice_ids: string[];
  idempotency_replayed: boolean;
}

interface ContractProvisionResult {
  contract: Contract;
  created_client: boolean;
  created_subscriber: boolean;
  provisioning_mode: "upgrade_existing_contract" | "new_contract";
}

interface ListEnvelope<T> {
  data: T[];
  meta: {
    page: number;
    size: number;
    total: number;
    sort: string | null;
    filters: string | null;
  };
}

interface ApiErrorEnvelope {
  error?: {
    code?: string;
    message?: string;
    details?: {
      errors?: Array<{
        loc?: Array<string | number>;
        msg?: string;
      }>;
    };
  };
}

interface BinaryToggleProps {
  label: string;
  value: boolean;
  disabled?: boolean;
  onChange: (value: boolean) => void;
}

function BinaryToggle({ label, value, disabled = false, onChange }: BinaryToggleProps) {
  return (
    <div className="binary-toggle" role="group" aria-label={label}>
      <button
        type="button"
        className={`toggle-chip ${value ? "active" : ""}`}
        onClick={() => onChange(true)}
        disabled={disabled}
        aria-pressed={value}
      >
        On
      </button>
      <button
        type="button"
        className={`toggle-chip ${!value ? "active" : ""}`}
        onClick={() => onChange(false)}
        disabled={disabled}
        aria-pressed={!value}
      >
        Off
      </button>
    </div>
  );
}

const CONFIGURED_API_BASE_URL = (import.meta.env.VITE_API_BASE_URL ?? "").trim();
const ACTOR_ID = import.meta.env.VITE_ACTOR_ID ?? "frontend-operator";
const ACTOR_ROLES = import.meta.env.VITE_ACTOR_ROLES ?? "admin,billing,user";
const DEFAULT_API_BASE_URL = "http://localhost:8010";
const FALLBACK_API_BASE_URLS = [
  "http://localhost:8010",
  "http://localhost:8000",
  "http://127.0.0.1:8010",
  "http://127.0.0.1:8000",
];

function buildApiErrorMessage(payload: ApiErrorEnvelope | undefined, fallbackMessage: string): string {
  const baseMessage = payload?.error?.message?.trim();
  const firstValidationIssue = payload?.error?.details?.errors?.[0];
  const issueMessage = firstValidationIssue?.msg?.trim();
  const issuePath = firstValidationIssue?.loc
    ?.filter((part) => part !== "body")
    .map((part) => String(part))
    .join(".");

  if (issueMessage) {
    if (issuePath) {
      return `${baseMessage ?? "Request validation failed"}: ${issuePath} - ${issueMessage}`;
    }
    return `${baseMessage ?? "Request validation failed"}: ${issueMessage}`;
  }

  return baseMessage || fallbackMessage;
}

function buildApiBaseCandidates(): string[] {
  const candidates = [CONFIGURED_API_BASE_URL, ...FALLBACK_API_BASE_URLS];
  const unique: string[] = [];
  for (const candidate of candidates) {
    const normalized = candidate.trim();
    if (!normalized || unique.includes(normalized)) {
      continue;
    }
    unique.push(normalized);
  }
  return unique;
}

async function resolveApiBaseUrl(candidates: string[]): Promise<string> {
  for (const baseUrl of candidates) {
    try {
      const response = await fetch(`${baseUrl}/api/v1/health`, {
        method: "GET",
        headers: buildRequestHeaders({ method: "GET" }),
      });
      if (!response.ok) {
        continue;
      }

      const openApiResponse = await fetch(`${baseUrl}/openapi.json`, {
        method: "GET",
      });
      if (!openApiResponse.ok) {
        continue;
      }

      const openApiPayload = (await openApiResponse.json()) as { paths?: Record<string, unknown> };
      if (!openApiPayload.paths) {
        continue;
      }
      if (
        !Object.prototype.hasOwnProperty.call(openApiPayload.paths, "/api/v1/customers") ||
        !Object.prototype.hasOwnProperty.call(openApiPayload.paths, "/api/v1/offers") ||
        !Object.prototype.hasOwnProperty.call(openApiPayload.paths, "/api/v1/contracts")
      ) {
        continue;
      }

      return baseUrl;
    } catch (error) {
      void error;
    }
  }

  throw new Error(`Could not connect to backend. Tried: ${candidates.join(", ")}`);
}

function buildRequestHeaders(init?: RequestInit): Headers {
  const headers = new Headers(init?.headers ?? undefined);
  headers.set("X-Actor-Id", ACTOR_ID);
  headers.set("X-Actor-Roles", ACTOR_ROLES);

  const method = (init?.method ?? "GET").toUpperCase();
  const hasBody = init?.body !== undefined && init?.body !== null;
  if (hasBody && ["POST", "PUT", "PATCH"].includes(method) && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }
  return headers;
}

async function apiRequest<T>(baseUrl: string, path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${baseUrl}${path}`, {
    ...init,
    headers: buildRequestHeaders(init),
  });

  if (!response.ok) {
    const fallbackMessage = `Request failed with status ${response.status}`;
    let payload: ApiErrorEnvelope | undefined;
    try {
      payload = (await response.json()) as ApiErrorEnvelope;
    } catch (error) {
      void error;
    }
    throw new Error(buildApiErrorMessage(payload, fallbackMessage));
  }

  if (response.status === 204) {
    return undefined as T;
  }

  const responseText = await response.text();
  if (!responseText) {
    return undefined as T;
  }

  return JSON.parse(responseText) as T;
}

function idempotencyKey(prefix: string): string {
  if (typeof crypto !== "undefined" && typeof crypto.randomUUID === "function") {
    return `${prefix}-${crypto.randomUUID()}`;
  }
  return `${prefix}-${Date.now()}-${Math.random().toString(16).slice(2)}`;
}

function currentMonthStartIso(): string {
  const now = new Date();
  return new Date(now.getFullYear(), now.getMonth(), 1).toISOString().slice(0, 10);
}

function currentMonthEndIso(): string {
  const now = new Date();
  return new Date(now.getFullYear(), now.getMonth() + 1, 0).toISOString().slice(0, 10);
}

function parseOfferIntegerInput(value: string): number | null {
  const trimmed = value.trim();
  if (!trimmed) {
    return null;
  }
  const parsed = Number(trimmed);
  if (!Number.isInteger(parsed) || parsed <= 0) {
    return null;
  }
  return parsed;
}

function App() {
  const formatServiceCategory = (category: OfferServiceCategory): string => {
    if (category === "mobile") {
      return "Mobile";
    }
    if (category === "internet") {
      return "Internet";
    }
    return "Landline";
  };

  const getOfferComponentsSummary = (offer: Offer): string => {
    if (offer.service_category === "mobile") {
      const parts: string[] = [];
      if (offer.mobile_data_gb !== null) {
        parts.push(`${offer.mobile_data_gb}Go data`);
      }
      if (offer.mobile_calls_hours !== null) {
        parts.push(`${offer.mobile_calls_hours}h calls`);
      }
      return parts.join(" + ") || "-";
    }
    if (offer.service_category === "internet") {
      const parts: string[] = [];
      if (offer.internet_access_type === "fiber" && offer.internet_fiber_speed_mbps !== null) {
        parts.push(`Fiber ${offer.internet_fiber_speed_mbps}Mbps`);
      }
      if (offer.internet_access_type === "adsl" && offer.internet_adsl_speed_mbps !== null) {
        parts.push(`ADSL ${offer.internet_adsl_speed_mbps}Mbps`);
      }
      parts.push("Landline");
      if (offer.internet_tv_included) {
        parts.push("TV");
      }
      return parts.join(" + ") || "-";
    }
    const parts: string[] = [];
    if (offer.landline_national_included) {
      parts.push("National unlimited");
    }
    if (offer.landline_international_hours !== null) {
      parts.push(`International ${offer.landline_international_hours}h`);
    }
    if (offer.landline_phone_hours !== null) {
      parts.push(`Phone ${offer.landline_phone_hours}h`);
    }
    return parts.join(" + ") || "-";
  };

  const buildOfferLabel = (offer: Offer): string =>
    `${offer.name} (${formatServiceCategory(offer.service_category)} / ${offer.service_type})`;

  const [apiBaseUrl, setApiBaseUrl] = useState<string>(
    CONFIGURED_API_BASE_URL || DEFAULT_API_BASE_URL
  );
  const [apiResolved, setApiResolved] = useState(false);

  const [activeTab, setActiveTab] = useState<ViewTab>("contracts");
  const [clients, setClients] = useState<Client[]>([]);
  const [offers, setOffers] = useState<Offer[]>([]);
  const [subscribers, setSubscribers] = useState<Subscriber[]>([]);
  const [contracts, setContracts] = useState<Contract[]>([]);
  const [invoices, setInvoices] = useState<Invoice[]>([]);
  const [selectedInvoiceId, setSelectedInvoiceId] = useState<string>("");
  const [selectedInvoiceDetail, setSelectedInvoiceDetail] = useState<InvoiceDetail | null>(null);
  const [collectionsOverview, setCollectionsOverview] = useState<CollectionOverview | null>(null);
  const [collectionCases, setCollectionCases] = useState<CollectionCase[]>([]);
  const [selectedCollectionCaseId, setSelectedCollectionCaseId] = useState<string>("");
  const [collectionCaseActions, setCollectionCaseActions] = useState<CollectionCaseAction[]>([]);
  const [selectedClientId, setSelectedClientId] = useState<string>("");
  const [contractClientMode, setContractClientMode] = useState<ContractClientMode>("existing");
  const [isBusy, setIsBusy] = useState(false);
  const [banner, setBanner] = useState<{ kind: "ok" | "error"; text: string } | null>(null);
  const [editingOfferId, setEditingOfferId] = useState<string | null>(null);

  const [newClientForm, setNewClientForm] = useState({
    client_type: "individual" as ClientType,
    first_name: "",
    last_name: "",
    address: "",
    email: "",
    phone: "",
  });
  const [offerForm, setOfferForm] = useState({
    service_category: "mobile" as OfferServiceCategory,
    name: "",
    mobile_data_gb: "",
    mobile_calls_hours: "",
    internet_access_type: "fiber" as InternetAccessType,
    internet_fiber_speed_mbps: "",
    internet_adsl_speed_mbps: "",
    internet_landline_included: false,
    internet_tv_included: false,
    landline_national_included: true,
    landline_international_enabled: false,
    landline_international_hours: "",
    landline_phone_enabled: false,
    landline_phone_hours: "",
    monthly_fee: "49.90",
    activation_fee: "0.00",
    status: "active" as OfferStatus,
    valid_from: new Date().toISOString().slice(0, 10),
    use_validation_date: false,
    valid_to: "",
  });
  const [contractForm, setContractForm] = useState({
    offer_id: "",
    target_contract_id: "",
    new_service_identifier: "",
    contract_start_date: new Date().toISOString().slice(0, 10),
    commitment_months: "12",
    auto_activate: true,
  });
  const [billingRunForm, setBillingRunForm] = useState({
    period_start: currentMonthStartIso(),
    period_end: currentMonthEndIso(),
    due_days: "15",
    tax_rate: "0.00",
  });
  const [invoiceFilters, setInvoiceFilters] = useState({
    client_id: "",
    service: "all" as OfferServiceCategory | "all",
    offer_id: "",
  });
  const [collectionFilters, setCollectionFilters] = useState({
    status: "all" as CollectionCaseStatusFilter,
    aging_bucket: "all" as AgingBucketFilter,
    client_id: "",
  });
  const [paymentForm, setPaymentForm] = useState({
    invoice_id: "",
    amount: "",
    payment_date: new Date().toISOString().slice(0, 10),
    method: "cash" as PaymentMethod,
    reference: "",
    note: "",
  });
  const [actionForm, setActionForm] = useState({
    action_type: "reminder_sent" as CollectionActionType,
    note: "",
  });

  const selectedProvisionOffer = useMemo(
    () => offers.find((offer) => offer.id === contractForm.offer_id) ?? null,
    [offers, contractForm.offer_id]
  );

  const sortedClients = useMemo(
    () => [...clients].sort((a, b) => a.full_name.localeCompare(b.full_name)),
    [clients]
  );
  const sortedOffers = useMemo(
    () =>
      [...offers].sort(
        (a, b) =>
          a.service_category.localeCompare(b.service_category) ||
          a.name.localeCompare(b.name)
      ),
    [offers]
  );
  const sortedSubscribers = useMemo(
    () => [...subscribers].sort((a, b) => a.service_identifier.localeCompare(b.service_identifier)),
    [subscribers]
  );
  const sortedContracts = useMemo(
    () => [...contracts].sort((a, b) => a.created_at.localeCompare(b.created_at)).reverse(),
    [contracts]
  );
  const sortedInvoices = useMemo(
    () => [...invoices].sort((a, b) => a.issued_at.localeCompare(b.issued_at)).reverse(),
    [invoices]
  );
  const selectableInvoiceFilterOffers = useMemo(() => {
    if (invoiceFilters.service === "all") {
      return sortedOffers;
    }
    return sortedOffers.filter((offer) => offer.service_category === invoiceFilters.service);
  }, [sortedOffers, invoiceFilters.service]);
  const sortedCollectionCases = useMemo(
    () =>
      [...collectionCases].sort(
        (a, b) => b.days_past_due - a.days_past_due || b.updated_at.localeCompare(a.updated_at)
      ),
    [collectionCases]
  );
  const selectedCollectionCase = useMemo(
    () => sortedCollectionCases.find((entry) => entry.id === selectedCollectionCaseId) ?? null,
    [sortedCollectionCases, selectedCollectionCaseId]
  );
  const payableInvoices = useMemo(
    () => sortedInvoices.filter((invoice) => invoice.status !== "void"),
    [sortedInvoices]
  );
  const selectableSubscribersForContract = useMemo(() => {
    if (!selectedProvisionOffer) {
      return sortedSubscribers;
    }
    return sortedSubscribers.filter(
      (subscriber) => subscriber.service_type === selectedProvisionOffer.service_type
    );
  }, [selectedProvisionOffer, sortedSubscribers]);
  const upgradeCandidateContracts = useMemo(() => {
    if (!selectedClientId || !selectedProvisionOffer) {
      return [];
    }
    return sortedContracts.filter((contract) => {
      if (contract.client_id !== selectedClientId || contract.status !== "active") {
        return false;
      }
      const subscriber = selectableSubscribersForContract.find(
        (item) => item.id === contract.subscriber_id
      );
      return Boolean(subscriber);
    });
  }, [selectedClientId, selectedProvisionOffer, sortedContracts, selectableSubscribersForContract]);
  const normalizedNewServiceIdentifier = contractForm.new_service_identifier.trim();
  const hasNewServiceIdentifier = normalizedNewServiceIdentifier.length > 0;
  const normalizedFirstName = newClientForm.first_name.trim();
  const normalizedLastName = newClientForm.last_name.trim();
  const normalizedFullName = `${normalizedFirstName} ${normalizedLastName}`.trim();
  const isProvisioningForExistingClient = contractClientMode === "existing";
  const autoDetectedProvisioningMode = useMemo(() => {
    if (!isProvisioningForExistingClient) {
      return "new_line";
    }
    if (hasNewServiceIdentifier) {
      return "new_line";
    }
    if (contractForm.target_contract_id) {
      return "upgrade";
    }
    if (upgradeCandidateContracts.length === 1) {
      return "upgrade";
    }
    if (upgradeCandidateContracts.length === 0) {
      return "new_line";
    }
    return "ambiguous";
  }, [
    hasNewServiceIdentifier,
    contractForm.target_contract_id,
    isProvisioningForExistingClient,
    upgradeCandidateContracts.length,
  ]);
  const requiresUpgradeTarget = autoDetectedProvisioningMode === "ambiguous";
  const canProvisionContract =
    (isProvisioningForExistingClient
      ? selectedClientId.length > 0
      : normalizedFullName.length >= 3) &&
    contractForm.offer_id.length > 0 &&
    !requiresUpgradeTarget;

  const offerPreviewComponents = useMemo(() => {
    if (offerForm.service_category === "mobile") {
      const parts: string[] = [];
      const data = parseOfferIntegerInput(offerForm.mobile_data_gb);
      const calls = parseOfferIntegerInput(offerForm.mobile_calls_hours);
      if (data !== null) {
        parts.push(`Data ${data}Go`);
      }
      if (calls !== null) {
        parts.push(`Calls ${calls}h`);
      }
      return parts.length > 0 ? parts : ["No component selected yet"];
    }

    if (offerForm.service_category === "internet") {
      const parts: string[] = [];
      const fiber = parseOfferIntegerInput(offerForm.internet_fiber_speed_mbps);
      const adsl = parseOfferIntegerInput(offerForm.internet_adsl_speed_mbps);
      if (offerForm.internet_access_type === "fiber") {
        parts.push(`Fiber ${fiber ?? "-"} Mbps`);
      } else {
        parts.push(`ADSL ${adsl ?? "-"} Mbps`);
      }
      parts.push("Landline On (mandatory)");
      parts.push(`TV ${offerForm.internet_tv_included ? "On" : "Off"}`);
      return parts;
    }

    const parts: string[] = [];
    parts.push(`National ${offerForm.landline_national_included ? "On" : "Off"}`);
    const international = parseOfferIntegerInput(offerForm.landline_international_hours);
    const phone = parseOfferIntegerInput(offerForm.landline_phone_hours);
    parts.push(
      `International ${
        offerForm.landline_international_enabled ? `${international ?? "-"}h` : "Off"
      }`
    );
    parts.push(`Phone ${offerForm.landline_phone_enabled ? `${phone ?? "-"}h` : "Off"}`);
    return parts;
  }, [offerForm]);

  const offerPreviewValidationDate = offerForm.use_validation_date
    ? offerForm.valid_to || "Select date"
    : "Undefined";

  const offerPreviewMonthlyFee = Number(offerForm.monthly_fee);
  const offerPreviewActivationFee = Number(offerForm.activation_fee);

  useEffect(() => {
    if (offerForm.service_category === "internet" && !offerForm.internet_landline_included) {
      setOfferForm((previous) => ({ ...previous, internet_landline_included: true }));
    }
  }, [offerForm.service_category, offerForm.internet_landline_included]);

  useEffect(() => {
    if (!invoiceFilters.offer_id) {
      return;
    }
    const exists = selectableInvoiceFilterOffers.some((offer) => offer.id === invoiceFilters.offer_id);
    if (!exists) {
      setInvoiceFilters((previous) => ({ ...previous, offer_id: "" }));
    }
  }, [invoiceFilters.offer_id, selectableInvoiceFilterOffers]);

  async function withGuard(fn: () => Promise<void>) {
    setIsBusy(true);
    setBanner(null);
    try {
      await fn();
    } catch (error) {
      const message = error instanceof Error ? error.message : "Unexpected error";
      setBanner({ kind: "error", text: message });
    } finally {
      setIsBusy(false);
    }
  }

  async function loadClients(baseUrl: string = apiBaseUrl) {
    const payload = await apiRequest<ListEnvelope<Client>>(
      baseUrl,
      "/api/v1/customers?page=1&size=100"
    );
    setClients(payload.data);
    if (!selectedClientId && payload.data.length > 0) {
      setSelectedClientId(payload.data[0].id);
    }
  }

  async function loadOffers(baseUrl: string = apiBaseUrl) {
    const payload = await apiRequest<ListEnvelope<Offer>>(baseUrl, "/api/v1/offers?page=1&size=100");
    setOffers(payload.data);
    setContractForm((previous) => {
      const stillExists = payload.data.some((offer) => offer.id === previous.offer_id);
      if (stillExists) {
        return previous;
      }
      return { ...previous, offer_id: payload.data[0]?.id ?? "" };
    });
  }

  async function loadSubscribers(clientId: string, baseUrl: string = apiBaseUrl) {
    if (!clientId) {
      setSubscribers([]);
      return;
    }
    const payload = await apiRequest<ListEnvelope<Subscriber>>(
      baseUrl,
      `/api/v1/customers/${clientId}/subscribers?page=1&size=100`
    );
    setSubscribers(payload.data);
  }

  async function loadContracts(baseUrl: string = apiBaseUrl) {
    const payload = await apiRequest<ListEnvelope<Contract>>(
      baseUrl,
      "/api/v1/contracts?page=1&size=100"
    );
    setContracts(payload.data);
  }

  async function loadInvoices(
    baseUrl: string = apiBaseUrl,
    filters = invoiceFilters
  ) {
    const params = new URLSearchParams({ page: "1", size: "100" });
    if (filters.client_id.trim()) {
      params.set("client_id", filters.client_id.trim());
    }
    if (filters.service !== "all") {
      params.set("service", filters.service);
    }
    if (filters.offer_id.trim()) {
      params.set("offer_id", filters.offer_id.trim());
    }

    const payload = await apiRequest<ListEnvelope<Invoice>>(
      baseUrl,
      `/api/v1/invoices?${params.toString()}`
    );
    setInvoices(payload.data);
    setSelectedInvoiceId((previous) => {
      if (!payload.data.length) {
        setSelectedInvoiceDetail(null);
        return "";
      }
      const stillExists = payload.data.some((invoice) => invoice.id === previous);
      return stillExists ? previous : payload.data[0].id;
    });
  }

  async function loadInvoiceDetail(invoiceId: string, baseUrl: string = apiBaseUrl) {
    if (!invoiceId) {
      setSelectedInvoiceDetail(null);
      return;
    }
    const detail = await apiRequest<InvoiceDetail>(baseUrl, `/api/v1/invoices/${invoiceId}`);
    setSelectedInvoiceDetail(detail);
  }

  async function loadCollectionsOverview(baseUrl: string = apiBaseUrl) {
    const payload = await apiRequest<CollectionOverview>(baseUrl, "/api/v1/collections/overview");
    setCollectionsOverview(payload);
  }

  async function loadCollectionCases(
    baseUrl: string = apiBaseUrl,
    filters: {
      status: CollectionCaseStatusFilter;
      aging_bucket: AgingBucketFilter;
      client_id: string;
    } = collectionFilters
  ): Promise<CollectionCase[]> {
    const params = new URLSearchParams({ page: "1", size: "100" });
    if (filters.status !== "all") {
      params.set("status", filters.status);
    }
    if (filters.aging_bucket !== "all") {
      params.set("aging_bucket", filters.aging_bucket);
    }
    if (filters.client_id.trim()) {
      params.set("client_id", filters.client_id.trim());
    }

    const payload = await apiRequest<ListEnvelope<CollectionCase>>(
      baseUrl,
      `/api/v1/collections/cases?${params.toString()}`
    );
    setCollectionCases(payload.data);
    setSelectedCollectionCaseId((previous) => {
      if (!payload.data.length) {
        setCollectionCaseActions([]);
        return "";
      }
      const stillExists = payload.data.some((entry) => entry.id === previous);
      return stillExists ? previous : payload.data[0].id;
    });
    return payload.data;
  }

  async function loadCollectionCaseActions(caseId: string, baseUrl: string = apiBaseUrl) {
    if (!caseId) {
      setCollectionCaseActions([]);
      return;
    }
    const payload = await apiRequest<CollectionCaseAction[]>(
      baseUrl,
      `/api/v1/collections/cases/${caseId}/actions`
    );
    setCollectionCaseActions(payload);
  }

  useEffect(() => {
    void withGuard(async () => {
      const resolvedBaseUrl = await resolveApiBaseUrl(buildApiBaseCandidates());
      setApiBaseUrl(resolvedBaseUrl);
      setApiResolved(true);
      await Promise.all([
        loadClients(resolvedBaseUrl),
        loadOffers(resolvedBaseUrl),
        loadContracts(resolvedBaseUrl),
        loadInvoices(resolvedBaseUrl),
        loadCollectionsOverview(resolvedBaseUrl),
        loadCollectionCases(resolvedBaseUrl),
      ]);
      setBanner({ kind: "ok", text: `Connected to backend services (${resolvedBaseUrl}).` });
    });
  }, []);

  useEffect(() => {
    if (!apiResolved) {
      return;
    }
    if (!isProvisioningForExistingClient) {
      setSubscribers([]);
      return;
    }
    void withGuard(async () => {
      await loadSubscribers(selectedClientId, apiBaseUrl);
    });
  }, [selectedClientId, isProvisioningForExistingClient, apiBaseUrl, apiResolved]);

  useEffect(() => {
    if (!apiResolved) {
      return;
    }
    if (!selectedInvoiceId) {
      setSelectedInvoiceDetail(null);
      return;
    }
    void withGuard(async () => {
      await loadInvoiceDetail(selectedInvoiceId, apiBaseUrl);
    });
  }, [selectedInvoiceId, apiBaseUrl, apiResolved]);

  useEffect(() => {
    if (!apiResolved) {
      return;
    }
    if (!selectedCollectionCaseId) {
      setCollectionCaseActions([]);
      return;
    }
    void withGuard(async () => {
      await loadCollectionCaseActions(selectedCollectionCaseId, apiBaseUrl);
    });
  }, [selectedCollectionCaseId, apiBaseUrl, apiResolved]);

  useEffect(() => {
    if (!selectedCollectionCase) {
      return;
    }
    setPaymentForm((previous) => ({
      ...previous,
      invoice_id: selectedCollectionCase.invoice_id,
    }));
  }, [selectedCollectionCase]);

  useEffect(() => {
    if (!isProvisioningForExistingClient) {
      if (contractForm.target_contract_id) {
        setContractForm((previous) => ({ ...previous, target_contract_id: "" }));
      }
      return;
    }
    if (hasNewServiceIdentifier) {
      if (contractForm.target_contract_id) {
        setContractForm((previous) => ({ ...previous, target_contract_id: "" }));
      }
      return;
    }

    const hasCurrentTarget = upgradeCandidateContracts.some(
      (contract) => contract.id === contractForm.target_contract_id
    );
    if (hasCurrentTarget) {
      return;
    }

    if (upgradeCandidateContracts.length === 1) {
      setContractForm((previous) => ({
        ...previous,
        target_contract_id: upgradeCandidateContracts[0].id,
      }));
      return;
    }

    if (contractForm.target_contract_id) {
      setContractForm((previous) => ({ ...previous, target_contract_id: "" }));
    }
  }, [
    hasNewServiceIdentifier,
    contractForm.target_contract_id,
    isProvisioningForExistingClient,
    upgradeCandidateContracts,
  ]);

  async function handleUpdateClientStatus(clientId: string, status: ClientStatus) {
    await withGuard(async () => {
      await apiRequest<Client>(apiBaseUrl, `/api/v1/customers/${clientId}`, {
        method: "PUT",
        body: JSON.stringify({ status }),
      });
      await loadClients();
      setBanner({ kind: "ok", text: "Client status updated." });
    });
  }

  async function handleDeleteClient(clientId: string) {
    await withGuard(async () => {
      await apiRequest<void>(apiBaseUrl, `/api/v1/customers/${clientId}`, {
        method: "DELETE",
      });
      if (selectedClientId === clientId) {
        setSelectedClientId("");
      }
      await Promise.all([loadClients(), loadContracts()]);
      setBanner({ kind: "ok", text: "Client deleted." });
    });
  }

  function parsePositiveInteger(value: string): number | null {
    const trimmed = value.trim();
    if (!trimmed) {
      return null;
    }
    const parsed = Number(trimmed);
    if (!Number.isInteger(parsed) || parsed <= 0) {
      return null;
    }
    return parsed;
  }

  function parsePositiveIntegerWithState(
    value: string
  ): { parsed: number | null; hasInvalidInput: boolean } {
    const trimmed = value.trim();
    if (!trimmed) {
      return { parsed: null, hasInvalidInput: false };
    }
    const parsed = Number(trimmed);
    if (!Number.isInteger(parsed) || parsed <= 0) {
      return { parsed: null, hasInvalidInput: true };
    }
    return { parsed, hasInvalidInput: false };
  }

  function validateOfferForm(): string | null {
    if (!offerForm.name.trim()) {
      return "Offer name is required.";
    }
    const monthlyFee = Number(offerForm.monthly_fee);
    if (!Number.isFinite(monthlyFee) || monthlyFee <= 0) {
      return "Monthly fee must be greater than zero.";
    }
    const activationFee = Number(offerForm.activation_fee);
    if (!Number.isFinite(activationFee) || activationFee < 0) {
      return "Other fees (activation fee) must be zero or greater.";
    }
    if (offerForm.use_validation_date && !offerForm.valid_to) {
      return "Validation date is required when enabled.";
    }
    if (offerForm.use_validation_date && offerForm.valid_to < offerForm.valid_from) {
      return "Validation date cannot be earlier than valid from date.";
    }

    if (offerForm.service_category === "mobile") {
      const data = parsePositiveIntegerWithState(offerForm.mobile_data_gb);
      const calls = parsePositiveIntegerWithState(offerForm.mobile_calls_hours);
      if (data.hasInvalidInput) {
        return "Mobile data must be a positive integer (Go).";
      }
      if (calls.hasInvalidInput) {
        return "Mobile calls must be a positive integer (hours).";
      }
      if (data.parsed === null && calls.parsed === null) {
        return "Mobile offers require at least one component: Data or Calls.";
      }
      return null;
    }

    if (offerForm.service_category === "internet") {
      if (offerForm.internet_access_type === "fiber") {
        const fiber = parsePositiveIntegerWithState(offerForm.internet_fiber_speed_mbps);
        if (fiber.hasInvalidInput || fiber.parsed === null) {
          return "Fiber speed must be a positive integer (Mbps).";
        }
      } else {
        const adsl = parsePositiveIntegerWithState(offerForm.internet_adsl_speed_mbps);
        if (adsl.hasInvalidInput || adsl.parsed === null) {
          return "ADSL speed must be a positive integer (Mbps).";
        }
      }
      return null;
    }

    const international = parsePositiveIntegerWithState(
      offerForm.landline_international_enabled ? offerForm.landline_international_hours : ""
    );
    const phone = parsePositiveIntegerWithState(
      offerForm.landline_phone_enabled ? offerForm.landline_phone_hours : ""
    );
    if (international.hasInvalidInput) {
      return "Landline international hours must be a positive integer.";
    }
    if (phone.hasInvalidInput) {
      return "Landline phone hours must be a positive integer.";
    }
    if (!offerForm.landline_national_included && international.parsed === null && phone.parsed === null) {
      return "Landline offers require at least one component: National, International, or Phone.";
    }
    return null;
  }

  function resetOfferForm() {
    setOfferForm((previous) => ({
      ...previous,
      name: "",
      service_category: "mobile",
      mobile_data_gb: "",
      mobile_calls_hours: "",
      internet_access_type: "fiber",
      internet_fiber_speed_mbps: "",
      internet_adsl_speed_mbps: "",
      internet_landline_included: false,
      internet_tv_included: false,
      landline_national_included: true,
      landline_international_enabled: false,
      landline_international_hours: "",
      landline_phone_enabled: false,
      landline_phone_hours: "",
      monthly_fee: "49.90",
      activation_fee: "0.00",
      valid_from: new Date().toISOString().slice(0, 10),
      use_validation_date: false,
      valid_to: "",
      status: "active",
    }));
    setEditingOfferId(null);
  }

  function buildOfferPayload(): Record<string, unknown> {
    const editingOffer = editingOfferId
      ? offers.find((offer) => offer.id === editingOfferId) ?? null
      : null;
    const payload: Record<string, unknown> = {
      name: offerForm.name.trim(),
      service_category: offerForm.service_category,
      version: editingOffer?.version ?? 1,
      monthly_fee: offerForm.monthly_fee,
      activation_fee: offerForm.activation_fee,
      status: offerForm.status,
      valid_from: offerForm.valid_from,
      valid_to: offerForm.use_validation_date ? offerForm.valid_to || null : null,
    };

    if (offerForm.service_category === "mobile") {
      payload.mobile_data_gb = parsePositiveInteger(offerForm.mobile_data_gb);
      payload.mobile_calls_hours = parsePositiveInteger(offerForm.mobile_calls_hours);
    } else if (offerForm.service_category === "internet") {
      payload.internet_access_type = offerForm.internet_access_type;
      payload.internet_fiber_speed_mbps =
        offerForm.internet_access_type === "fiber"
          ? parsePositiveInteger(offerForm.internet_fiber_speed_mbps)
          : null;
      payload.internet_adsl_speed_mbps =
        offerForm.internet_access_type === "adsl"
          ? parsePositiveInteger(offerForm.internet_adsl_speed_mbps)
          : null;
      payload.internet_landline_included = true;
      payload.internet_tv_included = offerForm.internet_tv_included;
    } else {
      payload.landline_national_included = offerForm.landline_national_included;
      payload.landline_international_hours = offerForm.landline_international_enabled
        ? parsePositiveInteger(offerForm.landline_international_hours)
        : null;
      payload.landline_phone_hours = offerForm.landline_phone_enabled
        ? parsePositiveInteger(offerForm.landline_phone_hours)
        : null;
    }

    return payload;
  }

  function startOfferEdit(offer: Offer) {
    setEditingOfferId(offer.id);
    setOfferForm({
      name: offer.name,
      service_category: offer.service_category,
      mobile_data_gb: offer.mobile_data_gb === null ? "" : String(offer.mobile_data_gb),
      mobile_calls_hours: offer.mobile_calls_hours === null ? "" : String(offer.mobile_calls_hours),
      internet_access_type: offer.internet_access_type ?? "fiber",
      internet_fiber_speed_mbps:
        offer.internet_fiber_speed_mbps === null ? "" : String(offer.internet_fiber_speed_mbps),
      internet_adsl_speed_mbps:
        offer.internet_adsl_speed_mbps === null ? "" : String(offer.internet_adsl_speed_mbps),
      internet_landline_included:
        offer.service_category === "internet" ? true : offer.internet_landline_included,
      internet_tv_included: offer.internet_tv_included,
      landline_national_included: offer.landline_national_included,
      landline_international_enabled: offer.landline_international_hours !== null,
      landline_international_hours:
        offer.landline_international_hours === null ? "" : String(offer.landline_international_hours),
      landline_phone_enabled: offer.landline_phone_hours !== null,
      landline_phone_hours:
        offer.landline_phone_hours === null ? "" : String(offer.landline_phone_hours),
      monthly_fee: offer.monthly_fee,
      activation_fee: offer.activation_fee,
      status: offer.status,
      valid_from: offer.valid_from,
      use_validation_date: offer.valid_to !== null,
      valid_to: offer.valid_to ?? "",
    });
  }

  async function handleCreateOffer(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    await withGuard(async () => {
      const validationMessage = validateOfferForm();
      if (validationMessage) {
        setBanner({ kind: "error", text: validationMessage });
        return;
      }
      const payload = buildOfferPayload();
      if (editingOfferId) {
        await apiRequest<Offer>(apiBaseUrl, `/api/v1/offers/${editingOfferId}`, {
          method: "PUT",
          body: JSON.stringify(payload),
        });
      } else {
        await apiRequest<Offer>(apiBaseUrl, "/api/v1/offers", {
          method: "POST",
          body: JSON.stringify(payload),
        });
      }
      await loadOffers();
      resetOfferForm();
      setBanner({ kind: "ok", text: editingOfferId ? "Offer updated." : "Offer created." });
    });
  }

  async function handleUpdateOfferStatus(offerId: string, status: OfferStatus) {
    await withGuard(async () => {
      await apiRequest<Offer>(apiBaseUrl, `/api/v1/offers/${offerId}`, {
        method: "PUT",
        body: JSON.stringify({ status }),
      });
      await loadOffers();
      setBanner({ kind: "ok", text: "Offer status updated." });
    });
  }

  async function handleDeleteOffer(offerId: string) {
    await withGuard(async () => {
      await apiRequest<void>(apiBaseUrl, `/api/v1/offers/${offerId}`, {
        method: "DELETE",
      });
      if (editingOfferId === offerId) {
        resetOfferForm();
      }
      await Promise.all([loadOffers(), loadContracts()]);
      setBanner({ kind: "ok", text: "Offer deleted." });
    });
  }

  async function handleProvisionContract(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!contractForm.offer_id) {
      setBanner({ kind: "error", text: "Select an offer before provisioning a contract." });
      return;
    }
    if (isProvisioningForExistingClient && !selectedClientId) {
      setBanner({ kind: "error", text: "Select a client before provisioning a contract." });
      return;
    }
    if (!isProvisioningForExistingClient && normalizedFullName.length < 3) {
      setBanner({
        kind: "error",
        text: "Provide first name and last name for new-client provisioning.",
      });
      return;
    }

    await withGuard(async () => {
      const commitmentValue = contractForm.commitment_months.trim();
      const payload: Record<string, unknown> = {
        offer_id: contractForm.offer_id,
        provisioning_intent: "auto",
        contract_start_date: contractForm.contract_start_date,
        auto_activate: contractForm.auto_activate,
      };
      if (isProvisioningForExistingClient) {
        payload.client_id = selectedClientId;
      } else {
        payload.client = {
          client_type: newClientForm.client_type,
          full_name: normalizedFullName,
          address: newClientForm.address.trim() || null,
          email: newClientForm.email.trim() || null,
          phone: newClientForm.phone.trim() || null,
        };
      }
      if (commitmentValue.length > 0) {
        payload.commitment_months = Number(commitmentValue);
      }
      if (isProvisioningForExistingClient && contractForm.target_contract_id) {
        payload.target_contract_id = contractForm.target_contract_id;
      }
      if (normalizedNewServiceIdentifier.length > 0) {
        payload.subscriber = { service_identifier: normalizedNewServiceIdentifier };
      }

      const response = await apiRequest<ContractProvisionResult>(
        apiBaseUrl,
        "/api/v1/contracts/provision",
        {
        method: "POST",
        body: JSON.stringify(payload),
      });
      if (isProvisioningForExistingClient) {
        await Promise.all([loadContracts(), loadSubscribers(selectedClientId), loadClients()]);
      } else {
        await Promise.all([loadContracts(), loadClients(), loadOffers()]);
      }
      setContractForm((previous) => ({
        ...previous,
        target_contract_id: "",
        new_service_identifier: "",
      }));
      if (!isProvisioningForExistingClient) {
        setNewClientForm((previous) => ({
          ...previous,
          first_name: "",
          last_name: "",
          address: "",
          email: "",
          phone: "",
        }));
      }
      const subscriberMsg = response.created_subscriber
        ? "new subscriber auto-created"
        : "existing subscriber reused";
      const modeMsg =
        response.provisioning_mode === "upgrade_existing_contract"
          ? "Existing contract upgraded."
          : "New contract created.";
      setBanner({
        kind: "ok",
        text: `${modeMsg} ${subscriberMsg}.`,
      });
    });
  }

  async function handleUpdateContractStatus(contractId: string, status: ContractStatus) {
    await withGuard(async () => {
      await apiRequest<Contract>(apiBaseUrl, `/api/v1/contracts/${contractId}/status`, {
        method: "PUT",
        body: JSON.stringify({ status }),
      });
      await loadContracts();
      setBanner({ kind: "ok", text: "Contract status updated." });
    });
  }

  async function handleRunBillingCycle(event: FormEvent) {
    event.preventDefault();
    const dueDays = Number(billingRunForm.due_days);
    const taxRate = Number(billingRunForm.tax_rate);
    if (!billingRunForm.period_start || !billingRunForm.period_end) {
      setBanner({ kind: "error", text: "Billing period start and end dates are required." });
      return;
    }
    if (billingRunForm.period_end < billingRunForm.period_start) {
      setBanner({ kind: "error", text: "Billing period end cannot be earlier than start." });
      return;
    }
    if (!Number.isInteger(dueDays) || dueDays < 1 || dueDays > 90) {
      setBanner({ kind: "error", text: "Due days must be an integer between 1 and 90." });
      return;
    }
    if (!Number.isFinite(taxRate) || taxRate < 0 || taxRate > 1) {
      setBanner({ kind: "error", text: "Tax rate must be between 0.00 and 1.00." });
      return;
    }

    await withGuard(async () => {
      const result = await apiRequest<BillingRunResult>(apiBaseUrl, "/api/v1/billing/runs", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Idempotency-Key": idempotencyKey("billing-run"),
        },
        body: JSON.stringify({
          period_start: billingRunForm.period_start,
          period_end: billingRunForm.period_end,
          due_days: dueDays,
          tax_rate: taxRate.toFixed(2),
        }),
      });
      await Promise.all([loadInvoices(), loadCollectionsOverview(), loadCollectionCases()]);
      if (result.invoice_ids.length > 0) {
        setSelectedInvoiceId(result.invoice_ids[0]);
      }
      setBanner({
        kind: "ok",
        text: result.idempotency_replayed
          ? `Billing run replayed: ${result.invoice_count} invoices.`
          : `Billing run completed: ${result.invoice_count} invoices issued.`,
      });
    });
  }

  async function handleApplyInvoiceFilters(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    await withGuard(async () => {
      await loadInvoices();
      setBanner({ kind: "ok", text: "Invoice filters applied." });
    });
  }

  async function handleResetInvoiceFilters() {
    const resetFilters = {
      client_id: "",
      service: "all" as OfferServiceCategory | "all",
      offer_id: "",
    };
    setInvoiceFilters(resetFilters);
    await withGuard(async () => {
      await loadInvoices(apiBaseUrl, resetFilters);
      setBanner({ kind: "ok", text: "Invoice filters reset." });
    });
  }

  async function handleDownloadInvoicePdf(invoiceId: string) {
    await withGuard(async () => {
      const response = await fetch(`${apiBaseUrl}/api/v1/invoices/${invoiceId}/pdf`, {
        method: "GET",
        headers: buildRequestHeaders({ method: "GET" }),
      });
      if (!response.ok) {
        let payload: ApiErrorEnvelope | undefined;
        try {
          payload = (await response.json()) as ApiErrorEnvelope;
        } catch (error) {
          void error;
        }
        throw new Error(buildApiErrorMessage(payload, `Request failed with status ${response.status}`));
      }
      const blob = await response.blob();
      const objectUrl = URL.createObjectURL(blob);
      const anchor = document.createElement("a");
      anchor.href = objectUrl;
      anchor.download = `invoice-${invoiceId}.pdf`;
      document.body.appendChild(anchor);
      anchor.click();
      anchor.remove();
      URL.revokeObjectURL(objectUrl);
      setBanner({ kind: "ok", text: "Invoice PDF downloaded." });
    });
  }

  async function handleApproveInvoicePaid(invoiceId: string) {
    await withGuard(async () => {
      const result = await apiRequest<PaymentAllocationResult>(
        apiBaseUrl,
        `/api/v1/collections/invoices/${invoiceId}/approve-paid`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "Idempotency-Key": idempotencyKey(`approve-paid-${invoiceId}`),
          },
          body: JSON.stringify({
            payment_date: new Date().toISOString().slice(0, 10),
            method: "other",
            note: "Invoice approved as paid from invoice center",
          }),
        }
      );
      await Promise.all([loadInvoices(), loadCollectionsOverview(), loadCollectionCases()]);
      if (selectedInvoiceId === invoiceId) {
        await loadInvoiceDetail(invoiceId);
      }
      setBanner({
        kind: "ok",
        text: result.idempotency_replayed
          ? "Payment approval replayed; invoice already settled."
          : "Invoice approved as paid and payment recorded.",
      });
    });
  }

  async function handleRefreshCollections(filters?: {
    status: CollectionCaseStatusFilter;
    aging_bucket: AgingBucketFilter;
    client_id: string;
  }) {
    await withGuard(async () => {
      await Promise.all([loadCollectionsOverview(), loadCollectionCases(apiBaseUrl, filters)]);
      setBanner({ kind: "ok", text: "Collections data refreshed." });
    });
  }

  async function handleRecordPayment(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!paymentForm.invoice_id.trim()) {
      setBanner({ kind: "error", text: "Select an invoice before recording payment." });
      return;
    }

    const amountValue = Number(paymentForm.amount);
    if (!Number.isFinite(amountValue) || amountValue <= 0) {
      setBanner({ kind: "error", text: "Payment amount must be greater than zero." });
      return;
    }

    await withGuard(async () => {
      const payload: Record<string, unknown> = {
        invoice_id: paymentForm.invoice_id,
        amount: amountValue.toFixed(2),
        payment_date: paymentForm.payment_date,
        method: paymentForm.method,
      };
      if (paymentForm.reference.trim()) {
        payload.reference = paymentForm.reference.trim();
      }
      if (paymentForm.note.trim()) {
        payload.note = paymentForm.note.trim();
      }

      const result = await apiRequest<PaymentAllocationResult>(apiBaseUrl, "/api/v1/collections/payments", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Idempotency-Key": idempotencyKey("payment"),
        },
        body: JSON.stringify(payload),
      });

      await Promise.all([loadInvoices(), loadCollectionsOverview()]);
      const cases = await loadCollectionCases();
      const matchingCase = cases.find((entry) => entry.invoice_id === result.payment.invoice_id);
      if (matchingCase) {
        setSelectedCollectionCaseId(matchingCase.id);
        await loadCollectionCaseActions(matchingCase.id);
      }

      setPaymentForm((previous) => ({
        ...previous,
        amount: "",
        reference: "",
        note: "",
      }));
      setBanner({
        kind: "ok",
        text: result.idempotency_replayed
          ? "Payment replay detected: existing transaction returned."
          : `Payment recorded. Invoice is now ${result.invoice_status}.`,
      });
    });
  }

  async function handleUpdateCollectionCaseStatus(caseId: string, status: CollectionCaseStatus) {
    await withGuard(async () => {
      await apiRequest<CollectionCase>(apiBaseUrl, `/api/v1/collections/cases/${caseId}/status`, {
        method: "PUT",
        body: JSON.stringify({ status }),
      });
      await Promise.all([loadCollectionsOverview(), loadCollectionCases()]);
      if (caseId === selectedCollectionCaseId) {
        await loadCollectionCaseActions(caseId);
      }
      setBanner({ kind: "ok", text: "Collection case status updated." });
    });
  }

  async function handleCollectionAction(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!selectedCollectionCaseId) {
      setBanner({ kind: "error", text: "Select a collection case first." });
      return;
    }
    if (actionForm.action_type === "note" && !actionForm.note.trim()) {
      setBanner({ kind: "error", text: "Note text is required for note action." });
      return;
    }

    await withGuard(async () => {
      await apiRequest<CollectionCaseAction>(
        apiBaseUrl,
        `/api/v1/collections/cases/${selectedCollectionCaseId}/actions`,
        {
          method: "POST",
          body: JSON.stringify({
            action_type: actionForm.action_type,
            note: actionForm.note.trim() || null,
          }),
        }
      );
      await Promise.all([
        loadCollectionCaseActions(selectedCollectionCaseId),
        loadCollectionsOverview(),
        loadCollectionCases(),
      ]);
      setActionForm((previous) => ({
        ...previous,
        note: "",
      }));
      setBanner({ kind: "ok", text: "Collection action added." });
    });
  }

  function getClientLabel(clientId: string): string {
    const client = clients.find((item) => item.id === clientId);
    return client ? client.full_name : clientId;
  }

  function getOfferLabel(offerId: string): string {
    const offer = offers.find((item) => item.id === offerId);
    return offer ? buildOfferLabel(offer) : offerId;
  }

  function getSubscriberLabel(subscriberId: string): string {
    const subscriber = subscribers.find((item) => item.id === subscriberId);
    return subscriber ? subscriber.service_identifier : subscriberId;
  }

  function formatMoney(value: string): string {
    const parsed = Number(value);
    if (!Number.isFinite(parsed)) {
      return value;
    }
    return parsed.toFixed(2);
  }

  function formatDateTime(value: string): string {
    const parsed = new Date(value);
    if (Number.isNaN(parsed.getTime())) {
      return value;
    }
    return parsed.toLocaleString();
  }

  function formatAgingBucket(bucket: AgingBucket): string {
    if (bucket === "current") {
      return "Current";
    }
    if (bucket === "1_30") {
      return "1-30 days";
    }
    if (bucket === "31_60") {
      return "31-60 days";
    }
    if (bucket === "61_90") {
      return "61-90 days";
    }
    return "90+ days";
  }

  function statusBadgeClass(status: string): string {
    if (status === "active" || status === "paid" || status === "resolved") {
      return "status-pill status-active";
    }
    if (status === "suspended" || status === "issued" || status === "in_progress") {
      return "status-pill status-suspended";
    }
    if (status === "terminated" || status === "retired" || status === "overdue" || status === "open") {
      return "status-pill status-terminated";
    }
    if (status === "draft" || status === "closed" || status === "void") {
      return "status-pill status-draft";
    }
    return "status-pill status-neutral";
  }

  return (
    <main className="app-shell">
      <header className="app-header">
        <p className="kicker">Telecom Operator Workspace</p>
        <h1>MT-Facturation Control Center</h1>
        <p className="subtitle">
          Client, Subscriber, Offer, and Contract operations are connected to the backend APIs.
        </p>
        <div className="meta-line">
          <span>API: {apiBaseUrl}</span>
          <span>Actor: {ACTOR_ID}</span>
        </div>
      </header>

      {banner ? (
        <section className={`banner banner-${banner.kind}`} role="status">
          {banner.text}
        </section>
      ) : null}

      <nav className="tab-row" aria-label="Main sections">
        <button
          type="button"
          className={`tab-button ${activeTab === "contracts" ? "active" : ""}`}
          onClick={() => setActiveTab("contracts")}
        >
          Contracts
        </button>
        <button
          type="button"
          className={`tab-button ${activeTab === "clients" ? "active" : ""}`}
          onClick={() => setActiveTab("clients")}
        >
          Clients
        </button>
        <button
          type="button"
          className={`tab-button ${activeTab === "offers" ? "active" : ""}`}
          onClick={() => setActiveTab("offers")}
        >
          Offers
        </button>
        <button
          type="button"
          className={`tab-button ${activeTab === "invoices" ? "active" : ""}`}
          onClick={() => setActiveTab("invoices")}
        >
          Invoices
        </button>
        <button
          type="button"
          className={`tab-button ${activeTab === "collections" ? "active" : ""}`}
          onClick={() => setActiveTab("collections")}
        >
          Collections
        </button>
      </nav>

      {activeTab === "clients" ? (
      <section className="panel">
        <h2>Client Management</h2>
        <p className="panel-note">
          Client creation is handled from Contract Provisioning. This tab is for status management
          and controlled deletion only.
        </p>
        <button type="button" disabled={isBusy} onClick={() => void withGuard(loadClients)}>
          Refresh Clients
        </button>

        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Name</th>
                <th>Type</th>
                <th>Address</th>
                <th>Email</th>
                <th>Status</th>
                <th>Status Action</th>
                <th>Delete</th>
              </tr>
            </thead>
            <tbody>
              {sortedClients.map((client) => (
                <tr key={client.id}>
                  <td>
                    <button
                      className={`link-like ${selectedClientId === client.id ? "active" : ""}`}
                      type="button"
                      onClick={() => setSelectedClientId(client.id)}
                    >
                      {client.full_name}
                    </button>
                  </td>
                  <td>{client.client_type}</td>
                  <td>{client.address ?? "-"}</td>
                  <td>{client.email ?? "-"}</td>
                  <td>
                    <span className={statusBadgeClass(client.status)}>{client.status}</span>
                  </td>
                  <td>
                    <select
                      value={client.status}
                      onChange={(event) =>
                        void handleUpdateClientStatus(client.id, event.target.value as ClientStatus)
                      }
                    >
                      <option value="active">active</option>
                      <option value="suspended">suspended</option>
                      <option value="terminated">terminated</option>
                    </select>
                  </td>
                  <td>
                    <button
                      type="button"
                      disabled={isBusy}
                      onClick={() => void handleDeleteClient(client.id)}
                    >
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
              {sortedClients.length === 0 ? (
                <tr>
                  <td colSpan={7}>No clients yet.</td>
                </tr>
              ) : null}
            </tbody>
          </table>
        </div>
      </section>
      ) : null}

      {activeTab === "offers" ? (
      <section className="panel">
        <h2>Offer Management</h2>
        <p className="panel-note">
          Configure offers from a stable operations panel: no jumping controls, live preview, and
          service-specific rules.
        </p>
        <div className="offers-workspace">
          <form className="offer-ops-panel" onSubmit={handleCreateOffer}>
            <div className="offer-grid">
              <label>
                Service
                <select
                  value={offerForm.service_category}
                  onChange={(event) => {
                    const selectedCategory = event.target.value as OfferServiceCategory;
                    setOfferForm((previous) => ({
                      ...previous,
                      service_category: selectedCategory,
                      internet_landline_included:
                        selectedCategory === "internet" ? true : previous.internet_landline_included,
                    }));
                  }}
                >
                  <option value="mobile">Mobile</option>
                  <option value="internet">Internet</option>
                  <option value="landline">Landline</option>
                </select>
              </label>
              <label>
                Offer Name
                <input
                  value={offerForm.name}
                  onChange={(event) =>
                    setOfferForm((previous) => ({ ...previous, name: event.target.value }))
                  }
                  required
                />
              </label>
            </div>

            <div className="offer-card">
              <h3>Service Components</h3>
              {offerForm.service_category === "mobile" ? (
                <div className="component-rows">
                  <div className="component-row">
                    <div className="component-meta">
                      <strong>Data</strong>
                      <span>Optional quota</span>
                    </div>
                    <input
                      type="number"
                      min={1}
                      step={1}
                      value={offerForm.mobile_data_gb}
                      onChange={(event) =>
                        setOfferForm((previous) => ({
                          ...previous,
                          mobile_data_gb: event.target.value,
                        }))
                      }
                      placeholder="Go"
                    />
                  </div>
                  <div className="component-row">
                    <div className="component-meta">
                      <strong>Calls</strong>
                      <span>Optional quota</span>
                    </div>
                    <input
                      type="number"
                      min={1}
                      step={1}
                      value={offerForm.mobile_calls_hours}
                      onChange={(event) =>
                        setOfferForm((previous) => ({
                          ...previous,
                          mobile_calls_hours: event.target.value,
                        }))
                      }
                      placeholder="Hours"
                    />
                  </div>
                </div>
              ) : null}

              {offerForm.service_category === "internet" ? (
                <div className="component-rows">
                  <div className="component-row">
                    <div className="component-meta">
                      <strong>Access Type</strong>
                      <span>Pick one required option</span>
                    </div>
                    <div className="segment-toggle" role="group" aria-label="Internet access type">
                      <button
                        type="button"
                        className={`toggle-chip ${
                          offerForm.internet_access_type === "fiber" ? "active" : ""
                        }`}
                        onClick={() =>
                          setOfferForm((previous) => ({
                            ...previous,
                            internet_access_type: "fiber",
                          }))
                        }
                        aria-pressed={offerForm.internet_access_type === "fiber"}
                      >
                        Fiber
                      </button>
                      <button
                        type="button"
                        className={`toggle-chip ${
                          offerForm.internet_access_type === "adsl" ? "active" : ""
                        }`}
                        onClick={() =>
                          setOfferForm((previous) => ({
                            ...previous,
                            internet_access_type: "adsl",
                          }))
                        }
                        aria-pressed={offerForm.internet_access_type === "adsl"}
                      >
                        ADSL
                      </button>
                    </div>
                  </div>
                  <div className="component-row">
                    <div className="component-meta">
                      <strong>Fiber Speed</strong>
                      <span>Required when Fiber is on</span>
                    </div>
                    <input
                      type="number"
                      min={1}
                      step={1}
                      value={offerForm.internet_fiber_speed_mbps}
                      onChange={(event) =>
                        setOfferForm((previous) => ({
                          ...previous,
                          internet_fiber_speed_mbps: event.target.value,
                        }))
                      }
                      placeholder="Mbps"
                      disabled={offerForm.internet_access_type !== "fiber"}
                    />
                  </div>
                  <div className="component-row">
                    <div className="component-meta">
                      <strong>ADSL Speed</strong>
                      <span>Required when ADSL is on</span>
                    </div>
                    <input
                      type="number"
                      min={1}
                      step={1}
                      value={offerForm.internet_adsl_speed_mbps}
                      onChange={(event) =>
                        setOfferForm((previous) => ({
                          ...previous,
                          internet_adsl_speed_mbps: event.target.value,
                        }))
                      }
                      placeholder="Mbps"
                      disabled={offerForm.internet_access_type !== "adsl"}
                    />
                  </div>
                  <div className="component-row">
                    <div className="component-meta">
                      <strong>Include Landline</strong>
                      <span>Mandatory component for internet offers</span>
                    </div>
                    <span className="mandatory-chip">Always On</span>
                  </div>
                  <div className="component-row">
                    <div className="component-meta">
                      <strong>Include TV</strong>
                      <span>Optional bundle component</span>
                    </div>
                    <BinaryToggle
                      label="Include TV"
                      value={offerForm.internet_tv_included}
                      onChange={(value) =>
                        setOfferForm((previous) => ({
                          ...previous,
                          internet_tv_included: value,
                        }))
                      }
                    />
                  </div>
                </div>
              ) : null}

              {offerForm.service_category === "landline" ? (
                <div className="component-rows">
                  <div className="component-row">
                    <div className="component-meta">
                      <strong>National</strong>
                      <span>Unlimited component</span>
                    </div>
                    <BinaryToggle
                      label="National"
                      value={offerForm.landline_national_included}
                      onChange={(value) =>
                        setOfferForm((previous) => ({
                          ...previous,
                          landline_national_included: value,
                        }))
                      }
                    />
                  </div>
                  <div className="component-row with-input">
                    <div className="component-meta">
                      <strong>International</strong>
                      <span>Enable and set hour quota</span>
                    </div>
                    <BinaryToggle
                      label="International Hours"
                      value={offerForm.landline_international_enabled}
                      onChange={(value) =>
                        setOfferForm((previous) => ({
                          ...previous,
                          landline_international_enabled: value,
                          landline_international_hours: value
                            ? previous.landline_international_hours
                            : "",
                        }))
                      }
                    />
                    <input
                      type="number"
                      min={1}
                      step={1}
                      value={offerForm.landline_international_hours}
                      onChange={(event) =>
                        setOfferForm((previous) => ({
                          ...previous,
                          landline_international_hours: event.target.value,
                        }))
                      }
                      placeholder="Hours"
                      disabled={!offerForm.landline_international_enabled}
                    />
                  </div>
                  <div className="component-row with-input">
                    <div className="component-meta">
                      <strong>Phone</strong>
                      <span>Enable and set hour quota</span>
                    </div>
                    <BinaryToggle
                      label="Phone Hours"
                      value={offerForm.landline_phone_enabled}
                      onChange={(value) =>
                        setOfferForm((previous) => ({
                          ...previous,
                          landline_phone_enabled: value,
                          landline_phone_hours: value ? previous.landline_phone_hours : "",
                        }))
                      }
                    />
                    <input
                      type="number"
                      min={1}
                      step={1}
                      value={offerForm.landline_phone_hours}
                      onChange={(event) =>
                        setOfferForm((previous) => ({
                          ...previous,
                          landline_phone_hours: event.target.value,
                        }))
                      }
                      placeholder="Hours"
                      disabled={!offerForm.landline_phone_enabled}
                    />
                  </div>
                </div>
              ) : null}
            </div>

            <div className="offer-card">
              <h3>Commercials and Validity</h3>
              <div className="offer-grid">
                <label>
                  Monthly Fee
                  <input
                    type="number"
                    step="0.01"
                    value={offerForm.monthly_fee}
                    onChange={(event) =>
                      setOfferForm((previous) => ({ ...previous, monthly_fee: event.target.value }))
                    }
                    required
                  />
                </label>
                <label>
                  Other Fees (Activation Fee)
                  <input
                    type="number"
                    step="0.01"
                    min={0}
                    value={offerForm.activation_fee}
                    onChange={(event) =>
                      setOfferForm((previous) => ({
                        ...previous,
                        activation_fee: event.target.value,
                      }))
                    }
                    required
                  />
                </label>
                <label>
                  Valid From
                  <input
                    type="date"
                    value={offerForm.valid_from}
                    onChange={(event) =>
                      setOfferForm((previous) => ({ ...previous, valid_from: event.target.value }))
                    }
                    required
                  />
                </label>
                <label>
                  Status
                  <select
                    value={offerForm.status}
                    onChange={(event) =>
                      setOfferForm((previous) => ({
                        ...previous,
                        status: event.target.value as OfferStatus,
                      }))
                    }
                  >
                    <option value="active">active</option>
                    <option value="retired">retired</option>
                  </select>
                </label>
              </div>
              <div className="component-row with-input">
                <div className="component-meta">
                  <strong>Validation Date</strong>
                  <span>Enable only when this offer needs an end date</span>
                </div>
                <BinaryToggle
                  label="Apply Validation Date"
                  value={offerForm.use_validation_date}
                  onChange={(value) =>
                    setOfferForm((previous) => ({
                      ...previous,
                      use_validation_date: value,
                      valid_to: value ? previous.valid_to : "",
                    }))
                  }
                />
                <input
                  type="date"
                  value={offerForm.valid_to}
                  onChange={(event) =>
                    setOfferForm((previous) => ({
                      ...previous,
                      valid_to: event.target.value,
                    }))
                  }
                  disabled={!offerForm.use_validation_date}
                />
              </div>
            </div>

            <div className="offer-actions">
              <button type="submit" disabled={isBusy}>
                {editingOfferId ? "Update Offer" : "Create Offer"}
              </button>
              <button type="button" disabled={isBusy} onClick={resetOfferForm}>
                Reset Form
              </button>
              <button type="button" disabled={isBusy} onClick={() => void withGuard(loadOffers)}>
                Refresh Offers
              </button>
            </div>
          </form>

          <aside className="offer-preview-panel">
            <p className="preview-kicker">Live Preview</p>
            <h3>{offerForm.name.trim() || "Unnamed Offer"}</h3>
            <p className="preview-service">{formatServiceCategory(offerForm.service_category)}</p>
            <div className="preview-grid">
              <div>
                <span>Monthly Fee</span>
                <strong>
                  {Number.isFinite(offerPreviewMonthlyFee) ? offerPreviewMonthlyFee.toFixed(2) : "-"}
                </strong>
              </div>
              <div>
                <span>Other Fees</span>
                <strong>
                  {Number.isFinite(offerPreviewActivationFee)
                    ? offerPreviewActivationFee.toFixed(2)
                    : "-"}
                </strong>
              </div>
              <div>
                <span>Validation</span>
                <strong>{offerPreviewValidationDate}</strong>
              </div>
              <div>
                <span>Status</span>
                <strong>{offerForm.status}</strong>
              </div>
            </div>
            <div className="preview-components">
              <span>Components</span>
              <ul>
                {offerPreviewComponents.map((item) => (
                  <li key={item}>{item}</li>
                ))}
              </ul>
            </div>
          </aside>
        </div>

        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Service</th>
                <th>Name</th>
                <th>Components</th>
                <th>Monthly Fee</th>
                <th>Other Fees</th>
                <th>Validation Date</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {sortedOffers.map((offer) => (
                <tr key={offer.id}>
                  <td>{formatServiceCategory(offer.service_category)}</td>
                  <td>{offer.name}</td>
                  <td>{getOfferComponentsSummary(offer)}</td>
                  <td>{offer.monthly_fee}</td>
                  <td>{offer.activation_fee}</td>
                  <td>{offer.valid_to ?? "Undefined"}</td>
                  <td>
                    <span className={statusBadgeClass(offer.status)}>{offer.status}</span>
                  </td>
                  <td>
                    <div className="row-actions">
                      <select
                        value={offer.status}
                        onChange={(event) =>
                          void handleUpdateOfferStatus(offer.id, event.target.value as OfferStatus)
                        }
                      >
                        <option value="active">active</option>
                        <option value="retired">retired</option>
                      </select>
                      <button type="button" onClick={() => startOfferEdit(offer)} disabled={isBusy}>
                        Edit
                      </button>
                      <button
                        type="button"
                        onClick={() => void handleDeleteOffer(offer.id)}
                        disabled={isBusy}
                      >
                        Delete
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
              {sortedOffers.length === 0 ? (
                <tr>
                  <td colSpan={8}>No offers yet.</td>
                </tr>
              ) : null}
            </tbody>
          </table>
        </div>
      </section>
      ) : null}

      {activeTab === "contracts" ? (
      <section className="panel">
        <h2>Contract Provisioning</h2>
        <p className="panel-note">
          Provision flow is automated: the system auto-detects upgrade vs new line based on active
          contracts, target selection, and service identifier input.
        </p>
        <form className="form-grid" onSubmit={handleProvisionContract}>
          <label>
            Client Flow
            <select
              value={contractClientMode}
              onChange={(event) => setContractClientMode(event.target.value as ContractClientMode)}
            >
              <option value="existing">existing client</option>
              <option value="new">new client</option>
            </select>
          </label>
          {isProvisioningForExistingClient ? (
            <label>
              Client
              <select
                value={selectedClientId}
                onChange={(event) => setSelectedClientId(event.target.value)}
                required
              >
                <option value="" disabled>
                  Select client
                </option>
                {sortedClients.map((client) => (
                  <option key={client.id} value={client.id}>
                    {client.full_name}
                  </option>
                ))}
              </select>
            </label>
          ) : (
            <>
              <label>
                First Name
                <input
                  value={newClientForm.first_name}
                  onChange={(event) =>
                    setNewClientForm((previous) => ({
                      ...previous,
                      first_name: event.target.value,
                    }))
                  }
                  required
                />
              </label>
              <label>
                Last Name
                <input
                  value={newClientForm.last_name}
                  onChange={(event) =>
                    setNewClientForm((previous) => ({
                      ...previous,
                      last_name: event.target.value,
                    }))
                  }
                  required
                />
              </label>
              <label>
                Client Type
                <select
                  value={newClientForm.client_type}
                  onChange={(event) =>
                    setNewClientForm((previous) => ({
                      ...previous,
                      client_type: event.target.value as ClientType,
                    }))
                  }
                >
                  <option value="individual">individual</option>
                  <option value="business">business</option>
                </select>
              </label>
              <label>
                Address
                <input
                  value={newClientForm.address}
                  onChange={(event) =>
                    setNewClientForm((previous) => ({
                      ...previous,
                      address: event.target.value,
                    }))
                  }
                  placeholder="Street, city"
                />
              </label>
              <label>
                Email
                <input
                  type="email"
                  value={newClientForm.email}
                  onChange={(event) =>
                    setNewClientForm((previous) => ({
                      ...previous,
                      email: event.target.value,
                    }))
                  }
                />
              </label>
              <label>
                Phone
                <input
                  value={newClientForm.phone}
                  onChange={(event) =>
                    setNewClientForm((previous) => ({
                      ...previous,
                      phone: event.target.value,
                    }))
                  }
                />
              </label>
            </>
          )}
          <label>
            Offer
            <select
              value={contractForm.offer_id}
              onChange={(event) =>
                setContractForm((previous) => ({ ...previous, offer_id: event.target.value }))
              }
              required
            >
              <option value="" disabled>
                Select offer
              </option>
              {sortedOffers.map((offer) => (
                <option key={offer.id} value={offer.id}>
                  {buildOfferLabel(offer)}
                </option>
              ))}
            </select>
          </label>
          <label>
            Detected Mode
            <input
              value={
                autoDetectedProvisioningMode === "upgrade"
                  ? "upgrade existing active contract"
                  : autoDetectedProvisioningMode === "new_line"
                    ? "new line (create new subscriber)"
                    : "multiple active candidates, target selection required"
              }
              readOnly
            />
          </label>
          <label>
            Target Contract (Optional)
            <select
              value={contractForm.target_contract_id}
              onChange={(event) =>
                setContractForm((previous) => ({
                  ...previous,
                  target_contract_id: event.target.value,
                }))
              }
              disabled={
                !isProvisioningForExistingClient ||
                hasNewServiceIdentifier ||
                upgradeCandidateContracts.length === 0
              }
            >
              <option value="">
                {upgradeCandidateContracts.length === 0
                  ? "No active upgrade candidates"
                  : "Auto-select if exactly one candidate"}
              </option>
              {upgradeCandidateContracts.map((contract) => (
                <option key={contract.id} value={contract.id}>
                  {contract.id.slice(0, 8)} - {getOfferLabel(contract.offer_id)} -{" "}
                  {getSubscriberLabel(contract.subscriber_id)}
                </option>
              ))}
            </select>
          </label>
          <label>
            New Service Identifier (Optional)
            <input
              value={contractForm.new_service_identifier}
              onChange={(event) =>
                setContractForm((previous) => ({
                  ...previous,
                  new_service_identifier: event.target.value,
                }))
              }
              placeholder="Leave empty for auto-generated"
            />
          </label>
          <label>
            Contract Start
            <input
              type="date"
              value={contractForm.contract_start_date}
              onChange={(event) =>
                setContractForm((previous) => ({
                  ...previous,
                  contract_start_date: event.target.value,
                }))
              }
              required
            />
          </label>
          <label>
            Commitment (Months)
            <input
              type="number"
              min={1}
              max={60}
              value={contractForm.commitment_months}
              onChange={(event) =>
                setContractForm((previous) => ({
                  ...previous,
                  commitment_months: event.target.value,
                }))
              }
            />
          </label>
          <label>
            Auto Activate
            <select
              value={contractForm.auto_activate ? "yes" : "no"}
              onChange={(event) =>
                setContractForm((previous) => ({
                  ...previous,
                  auto_activate: event.target.value === "yes",
                }))
              }
            >
              <option value="yes">yes</option>
              <option value="no">no (draft)</option>
            </select>
          </label>
          <button type="submit" disabled={isBusy || !canProvisionContract}>
            Provision Contract
          </button>
          <button type="button" disabled={isBusy} onClick={() => void withGuard(loadContracts)}>
            Refresh Contracts
          </button>
        </form>
        {isProvisioningForExistingClient && requiresUpgradeTarget ? (
          <p className="panel-note">
            Multiple active contracts match this offer service. Either select a target contract or
            provide a new service identifier to force new-line provisioning.
          </p>
        ) : null}

        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Contract</th>
                <th>Client</th>
                <th>Offer</th>
                <th>Status</th>
                <th>Start</th>
                <th>End</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {sortedContracts.map((contract) => (
                <tr key={contract.id}>
                  <td>{contract.id.slice(0, 8)}</td>
                  <td>{getClientLabel(contract.client_id)}</td>
                  <td>{getOfferLabel(contract.offer_id)}</td>
                  <td>
                    <span className={statusBadgeClass(contract.status)}>{contract.status}</span>
                  </td>
                  <td>{contract.start_date}</td>
                  <td>{contract.end_date ?? "-"}</td>
                  <td>
                    <select
                      value={contract.status}
                      onChange={(event) =>
                        void handleUpdateContractStatus(
                          contract.id,
                          event.target.value as ContractStatus
                        )
                      }
                    >
                      <option value="draft">draft</option>
                      <option value="active">active</option>
                      <option value="suspended">suspended</option>
                      <option value="terminated">terminated</option>
                    </select>
                  </td>
                </tr>
              ))}
              {sortedContracts.length === 0 ? (
                <tr>
                  <td colSpan={7}>No contracts yet.</td>
                </tr>
              ) : null}
            </tbody>
          </table>
        </div>

      </section>
      ) : null}

      {activeTab === "invoices" ? (
      <section className="panel">
        <div className="billing-header">
          <h2>Invoice Center</h2>
          <p>Generate grouped monthly invoices and download issued invoice PDFs.</p>
        </div>

        <form className="billing-run-form" onSubmit={handleRunBillingCycle}>
          <label>
            Period Start
            <input
              type="date"
              value={billingRunForm.period_start}
              onChange={(event) =>
                setBillingRunForm((previous) => ({
                  ...previous,
                  period_start: event.target.value,
                }))
              }
              required
            />
          </label>
          <label>
            Period End
            <input
              type="date"
              value={billingRunForm.period_end}
              onChange={(event) =>
                setBillingRunForm((previous) => ({
                  ...previous,
                  period_end: event.target.value,
                }))
              }
              required
            />
          </label>
          <label>
            Due Days
            <input
              type="number"
              min={1}
              max={90}
              value={billingRunForm.due_days}
              onChange={(event) =>
                setBillingRunForm((previous) => ({
                  ...previous,
                  due_days: event.target.value,
                }))
              }
              required
            />
          </label>
          <label>
            Tax Rate
            <input
              type="number"
              min={0}
              max={1}
              step="0.01"
              value={billingRunForm.tax_rate}
              onChange={(event) =>
                setBillingRunForm((previous) => ({
                  ...previous,
                  tax_rate: event.target.value,
                }))
              }
              required
            />
          </label>
          <button type="submit" disabled={isBusy}>
            Run Billing Cycle
          </button>
          <button type="button" disabled={isBusy} onClick={() => void withGuard(loadInvoices)}>
            Refresh Invoices
          </button>
        </form>

        <form className="billing-run-form" onSubmit={handleApplyInvoiceFilters}>
          <label>
            Client
            <select
              value={invoiceFilters.client_id}
              onChange={(event) =>
                setInvoiceFilters((previous) => ({
                  ...previous,
                  client_id: event.target.value,
                }))
              }
            >
              <option value="">all clients</option>
              {sortedClients.map((client) => (
                <option key={client.id} value={client.id}>
                  {client.full_name}
                </option>
              ))}
            </select>
          </label>
          <label>
            Service
            <select
              value={invoiceFilters.service}
              onChange={(event) =>
                setInvoiceFilters((previous) => ({
                  ...previous,
                  service: event.target.value as OfferServiceCategory | "all",
                }))
              }
            >
              <option value="all">all services</option>
              <option value="mobile">mobile</option>
              <option value="internet">internet</option>
              <option value="landline">landline</option>
            </select>
          </label>
          <label>
            Offer
            <select
              value={invoiceFilters.offer_id}
              onChange={(event) =>
                setInvoiceFilters((previous) => ({
                  ...previous,
                  offer_id: event.target.value,
                }))
              }
            >
              <option value="">all offers</option>
              {selectableInvoiceFilterOffers.map((offer) => (
                <option key={offer.id} value={offer.id}>
                  {buildOfferLabel(offer)}
                </option>
              ))}
            </select>
          </label>
          <button type="submit" disabled={isBusy}>
            Apply Filters
          </button>
          <button type="button" disabled={isBusy} onClick={() => void handleResetInvoiceFilters()}>
            Reset Filters
          </button>
        </form>

        <div className="billing-layout">
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Invoice</th>
                  <th>Client</th>
                  <th>Period</th>
                  <th>Due Date</th>
                  <th>Total (MAD)</th>
                  <th>Status</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {sortedInvoices.map((invoice) => (
                  <tr key={invoice.id}>
                    <td>{invoice.id.slice(0, 8)}</td>
                    <td>{getClientLabel(invoice.client_id)}</td>
                    <td>
                      {invoice.period_start} to {invoice.period_end}
                    </td>
                    <td>{invoice.due_date}</td>
                    <td>{formatMoney(invoice.total_amount)}</td>
                    <td>
                      <span className={statusBadgeClass(invoice.status)}>{invoice.status}</span>
                    </td>
                    <td>
                      <div className="row-actions">
                        <button
                          type="button"
                          className={`link-like ${selectedInvoiceId === invoice.id ? "active" : ""}`}
                          onClick={() => setSelectedInvoiceId(invoice.id)}
                          disabled={isBusy}
                        >
                          View
                        </button>
                        <button
                          type="button"
                          className="link-like"
                          onClick={() => void handleDownloadInvoicePdf(invoice.id)}
                          disabled={isBusy}
                        >
                          Download PDF
                        </button>
                        {invoice.status !== "paid" && invoice.status !== "void" ? (
                          <button
                            type="button"
                            className="link-like"
                            onClick={() => void handleApproveInvoicePaid(invoice.id)}
                            disabled={isBusy}
                          >
                            Approve Paid
                          </button>
                        ) : null}
                      </div>
                    </td>
                  </tr>
                ))}
                {sortedInvoices.length === 0 ? (
                  <tr>
                    <td colSpan={7}>No invoices generated yet.</td>
                  </tr>
                ) : null}
              </tbody>
            </table>
          </div>

          <aside className="billing-detail-panel">
            <h4>Invoice Detail</h4>
            {selectedInvoiceDetail ? (
              <>
                <div className="billing-summary-grid">
                  <div>
                    <span>Invoice</span>
                    <strong>{selectedInvoiceDetail.id}</strong>
                  </div>
                  <div>
                    <span>Issued</span>
                    <strong>{formatDateTime(selectedInvoiceDetail.issued_at)}</strong>
                  </div>
                  <div>
                    <span>Subtotal</span>
                    <strong>{formatMoney(selectedInvoiceDetail.subtotal_amount)} MAD</strong>
                  </div>
                  <div>
                    <span>Tax</span>
                    <strong>{formatMoney(selectedInvoiceDetail.tax_amount)} MAD</strong>
                  </div>
                  <div>
                    <span>Total</span>
                    <strong>{formatMoney(selectedInvoiceDetail.total_amount)} MAD</strong>
                  </div>
                  <div>
                    <span>Due Date</span>
                    <strong>{selectedInvoiceDetail.due_date}</strong>
                  </div>
                </div>
                <div className="table-wrap">
                  <table>
                    <thead>
                      <tr>
                        <th>Type</th>
                        <th>Description</th>
                        <th>Qty</th>
                        <th>Unit</th>
                        <th>Total</th>
                      </tr>
                    </thead>
                    <tbody>
                      {selectedInvoiceDetail.lines.map((line) => (
                        <tr key={line.id}>
                          <td>{line.line_type}</td>
                          <td>{line.description}</td>
                          <td>{line.quantity}</td>
                          <td>{formatMoney(line.unit_amount)}</td>
                          <td>{formatMoney(line.line_total)}</td>
                        </tr>
                      ))}
                      {selectedInvoiceDetail.lines.length === 0 ? (
                        <tr>
                          <td colSpan={5}>No invoice lines found.</td>
                        </tr>
                      ) : null}
                    </tbody>
                  </table>
                </div>
              </>
            ) : (
              <p className="panel-note">Select an invoice to view line-level details.</p>
            )}
          </aside>
        </div>
      </section>
      ) : null}

      {activeTab === "collections" ? (
      <section className="panel">
        <div className="billing-header">
          <h2>Collections Center</h2>
          <p>Track overdue balances, post settlements, and log reminder/warning actions.</p>
        </div>

        <div className="collections-overview-grid">
          <article className="metric-card">
            <span>Open Cases</span>
            <strong>{collectionsOverview?.open_cases ?? 0}</strong>
          </article>
          <article className="metric-card">
            <span>In Progress</span>
            <strong>{collectionsOverview?.in_progress_cases ?? 0}</strong>
          </article>
          <article className="metric-card">
            <span>Overdue Invoices</span>
            <strong>{collectionsOverview?.overdue_invoices ?? 0}</strong>
          </article>
          <article className="metric-card">
            <span>Total Outstanding</span>
            <strong>{formatMoney(collectionsOverview?.total_outstanding_amount ?? "0")} MAD</strong>
          </article>
        </div>

        <div className="collections-buckets">
          {(["current", "1_30", "31_60", "61_90", "90_plus"] as AgingBucket[]).map((bucket) => (
            <div key={bucket}>
              <span>{formatAgingBucket(bucket)}</span>
              <strong>{formatMoney(collectionsOverview?.bucket_totals?.[bucket] ?? "0")} MAD</strong>
            </div>
          ))}
        </div>

        <form
          className="billing-run-form"
          onSubmit={(event) => {
            event.preventDefault();
            void handleRefreshCollections();
          }}
        >
          <label>
            Status
            <select
              value={collectionFilters.status}
              onChange={(event) =>
                setCollectionFilters((previous) => ({
                  ...previous,
                  status: event.target.value as CollectionCaseStatusFilter,
                }))
              }
            >
              <option value="all">all</option>
              <option value="open">open</option>
              <option value="in_progress">in_progress</option>
              <option value="resolved">resolved</option>
              <option value="closed">closed</option>
            </select>
          </label>
          <label>
            Aging Bucket
            <select
              value={collectionFilters.aging_bucket}
              onChange={(event) =>
                setCollectionFilters((previous) => ({
                  ...previous,
                  aging_bucket: event.target.value as AgingBucketFilter,
                }))
              }
            >
              <option value="all">all</option>
              <option value="current">current</option>
              <option value="1_30">1_30</option>
              <option value="31_60">31_60</option>
              <option value="61_90">61_90</option>
              <option value="90_plus">90_plus</option>
            </select>
          </label>
          <label>
            Client
            <select
              value={collectionFilters.client_id}
              onChange={(event) =>
                setCollectionFilters((previous) => ({
                  ...previous,
                  client_id: event.target.value,
                }))
              }
            >
              <option value="">all clients</option>
              {sortedClients.map((client) => (
                <option key={client.id} value={client.id}>
                  {client.full_name}
                </option>
              ))}
            </select>
          </label>
          <button type="submit" disabled={isBusy}>
            Apply Filters
          </button>
          <button
            type="button"
            disabled={isBusy}
            onClick={() => {
              const resetFilters = {
                status: "all",
                aging_bucket: "all",
                client_id: "",
              } as const;
              setCollectionFilters(resetFilters);
              void handleRefreshCollections(resetFilters);
            }}
          >
            Reset Filters
          </button>
        </form>

        <div className="collections-layout">
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Case</th>
                  <th>Client</th>
                  <th>Invoice</th>
                  <th>Days Past Due</th>
                  <th>Bucket</th>
                  <th>Outstanding (MAD)</th>
                  <th>Status</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {sortedCollectionCases.map((entry) => (
                  <tr key={entry.id}>
                    <td>{entry.id.slice(0, 8)}</td>
                    <td>{getClientLabel(entry.client_id)}</td>
                    <td>{entry.invoice_id.slice(0, 8)}</td>
                    <td>{entry.days_past_due}</td>
                    <td>{formatAgingBucket(entry.aging_bucket)}</td>
                    <td>{formatMoney(entry.outstanding_amount)}</td>
                    <td>
                      <span className={statusBadgeClass(entry.status)}>{entry.status}</span>
                    </td>
                    <td>
                      <div className="row-actions">
                        <button
                          type="button"
                          className={`link-like ${selectedCollectionCaseId === entry.id ? "active" : ""}`}
                          onClick={() => setSelectedCollectionCaseId(entry.id)}
                          disabled={isBusy}
                        >
                          View
                        </button>
                        <select
                          value={entry.status}
                          onChange={(event) =>
                            void handleUpdateCollectionCaseStatus(
                              entry.id,
                              event.target.value as CollectionCaseStatus
                            )
                          }
                          disabled={isBusy}
                        >
                          <option value="open">open</option>
                          <option value="in_progress">in_progress</option>
                          <option value="resolved">resolved</option>
                          <option value="closed">closed</option>
                        </select>
                      </div>
                    </td>
                  </tr>
                ))}
                {sortedCollectionCases.length === 0 ? (
                  <tr>
                    <td colSpan={8}>No collection cases found for the selected filters.</td>
                  </tr>
                ) : null}
              </tbody>
            </table>
          </div>

          <aside className="collections-detail-panel">
            <h4>Case Action Panel</h4>
            {selectedCollectionCase ? (
              <>
                <div className="billing-summary-grid">
                  <div>
                    <span>Case</span>
                    <strong>{selectedCollectionCase.id}</strong>
                  </div>
                  <div>
                    <span>Client</span>
                    <strong>{getClientLabel(selectedCollectionCase.client_id)}</strong>
                  </div>
                  <div>
                    <span>Invoice</span>
                    <strong>{selectedCollectionCase.invoice_id}</strong>
                  </div>
                  <div>
                    <span>Outstanding</span>
                    <strong>{formatMoney(selectedCollectionCase.outstanding_amount)} MAD</strong>
                  </div>
                </div>

                <form className="collections-payment-form" onSubmit={handleRecordPayment}>
                  <label>
                    Invoice
                    <select
                      value={paymentForm.invoice_id}
                      onChange={(event) =>
                        setPaymentForm((previous) => ({
                          ...previous,
                          invoice_id: event.target.value,
                        }))
                      }
                      required
                    >
                      <option value="" disabled>
                        Select invoice
                      </option>
                      {payableInvoices.map((invoice) => (
                        <option key={invoice.id} value={invoice.id}>
                          {invoice.id.slice(0, 8)} - {getClientLabel(invoice.client_id)} -{" "}
                          {formatMoney(invoice.total_amount)} MAD ({invoice.status})
                        </option>
                      ))}
                    </select>
                  </label>
                  <label>
                    Amount (MAD)
                    <input
                      type="number"
                      step="0.01"
                      min={0.01}
                      value={paymentForm.amount}
                      onChange={(event) =>
                        setPaymentForm((previous) => ({
                          ...previous,
                          amount: event.target.value,
                        }))
                      }
                      required
                    />
                  </label>
                  <label>
                    Payment Date
                    <input
                      type="date"
                      value={paymentForm.payment_date}
                      onChange={(event) =>
                        setPaymentForm((previous) => ({
                          ...previous,
                          payment_date: event.target.value,
                        }))
                      }
                      required
                    />
                  </label>
                  <label>
                    Method
                    <select
                      value={paymentForm.method}
                      onChange={(event) =>
                        setPaymentForm((previous) => ({
                          ...previous,
                          method: event.target.value as PaymentMethod,
                        }))
                      }
                    >
                      <option value="cash">cash</option>
                      <option value="card">card</option>
                      <option value="bank_transfer">bank_transfer</option>
                      <option value="wallet">wallet</option>
                      <option value="other">other</option>
                    </select>
                  </label>
                  <label>
                    Reference (Optional)
                    <input
                      value={paymentForm.reference}
                      onChange={(event) =>
                        setPaymentForm((previous) => ({
                          ...previous,
                          reference: event.target.value,
                        }))
                      }
                    />
                  </label>
                  <label>
                    Note (Optional)
                    <input
                      value={paymentForm.note}
                      onChange={(event) =>
                        setPaymentForm((previous) => ({
                          ...previous,
                          note: event.target.value,
                        }))
                      }
                    />
                  </label>
                  <button type="submit" disabled={isBusy}>
                    Record Payment
                  </button>
                </form>

                <form className="collections-action-form" onSubmit={handleCollectionAction}>
                  <label>
                    Action Type
                    <select
                      value={actionForm.action_type}
                      onChange={(event) =>
                        setActionForm((previous) => ({
                          ...previous,
                          action_type: event.target.value as CollectionActionType,
                        }))
                      }
                    >
                      <option value="reminder_sent">reminder_sent</option>
                      <option value="warning_sent">warning_sent</option>
                      <option value="note">note</option>
                    </select>
                  </label>
                  <label>
                    Note
                    <input
                      value={actionForm.note}
                      onChange={(event) =>
                        setActionForm((previous) => ({
                          ...previous,
                          note: event.target.value,
                        }))
                      }
                      placeholder="Required for note action"
                    />
                  </label>
                  <button type="submit" disabled={isBusy}>
                    Add Action
                  </button>
                </form>

                <div className="collections-action-list">
                  <h5>Action History</h5>
                  {collectionCaseActions.map((entry) => (
                    <article key={entry.id} className="collections-action-item">
                      <div>
                        <strong>{entry.action_type}</strong>
                        <span>{formatDateTime(entry.created_at)}</span>
                      </div>
                      <p>{entry.note || "No note"}</p>
                    </article>
                  ))}
                  {collectionCaseActions.length === 0 ? (
                    <p className="panel-note">No actions recorded yet for this case.</p>
                  ) : null}
                </div>
              </>
            ) : (
              <p className="panel-note">Select a collection case to manage payments and actions.</p>
            )}
          </aside>
        </div>
      </section>
      ) : null}

    </main>
  );
}

export default App;

