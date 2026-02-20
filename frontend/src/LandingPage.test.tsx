import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { vi } from "vitest";

import LandingPage from "./LandingPage";

describe("LandingPage", () => {
  function installFetchMock() {
    const fetchMock = vi.spyOn(globalThis, "fetch").mockImplementation(async (input, init) => {
      const url = String(input);
      const method = (init?.method ?? "GET").toUpperCase();

      if (url.endsWith("/api/v1/health")) {
        return new Response("{}", { status: 200, headers: { "Content-Type": "application/json" } });
      }
      if (url.endsWith("/openapi.json")) {
        return new Response(JSON.stringify({ paths: { "/api/v1/landing/bootstrap": {} } }), {
          status: 200,
          headers: { "Content-Type": "application/json" },
        });
      }
      if (url.endsWith("/api/v1/landing/bootstrap")) {
        return new Response(
          JSON.stringify({
            offer_categories: [
              {
                service_category: "mobile",
                offers: [
                  {
                    id: "offer-mob-1",
                    name: "Mobile Flex",
                    service_category: "mobile",
                    service_type: "mobile",
                    monthly_fee: "59.00",
                    activation_fee: "9.00",
                  },
                ],
              },
              {
                service_category: "internet",
                offers: [
                  {
                    id: "offer-int-1",
                    name: "Fiber 200",
                    service_category: "internet",
                    service_type: "fiber",
                    monthly_fee: "199.00",
                    activation_fee: "49.00",
                  },
                ],
              },
              { service_category: "landline", offers: [] },
            ],
          }),
          { status: 200, headers: { "Content-Type": "application/json" } },
        );
      }
      if (url.endsWith("/api/v1/landing/clients/verify-cin") && method === "POST") {
        return new Response(
          JSON.stringify({
            cin: "AA12345",
            masked_contact: "AA***45",
            lookup_token: "lookup-token-1",
            expires_at: "2026-02-18T12:00:00Z",
          }),
          { status: 200, headers: { "Content-Type": "application/json" } },
        );
      }
      if (url.includes("/api/v1/landing/clients/AA12345/subscriptions") && method === "GET") {
        return new Response(
          JSON.stringify({
            client: { cin: "AA12345", full_name: "Lookup User", email: "l***@example.com", phone: "+******0000", address: "Rabat" },
            subscriptions: [
              {
                contract_id: "contract-1",
                service_identifier: "+212612345678",
                service_category: "mobile",
                current_offer: {
                  id: "offer-mob-1",
                  name: "Mobile Flex",
                  service_category: "mobile",
                  service_type: "mobile",
                  monthly_fee: "59.00",
                  activation_fee: "9.00",
                },
                eligible_offers: [
                  {
                    id: "offer-mob-2",
                    name: "Mobile Max",
                    service_category: "mobile",
                    service_type: "mobile",
                    monthly_fee: "89.00",
                    activation_fee: "9.00",
                  },
                ],
              },
            ],
          }),
          { status: 200, headers: { "Content-Type": "application/json" } },
        );
      }
      if (url.includes("/api/v1/landing/clients/AA12345/invoices") && method === "GET") {
        return new Response(
          JSON.stringify({
            client: {
              cin: "AA12345",
              full_name: "Lookup User",
              email: "l***@example.com",
              phone: "+******0000",
              address: "Rabat",
            },
            invoices: [
              {
                invoice_id: "invoice-1",
                period_start: "2026-02-01",
                period_end: "2026-02-28",
                due_date: "2026-03-15",
                issued_at: "2026-03-01T00:00:00Z",
                status: "issued",
                currency: "MAD",
                subtotal_amount: "99.00",
                tax_amount: "9.90",
                total_amount: "108.90",
                document_download_url: "/api/v1/landing/invoices/invoice-1/document?token=abc",
              },
            ],
          }),
          { status: 200, headers: { "Content-Type": "application/json" } },
        );
      }
      if (url.endsWith("/api/v1/landing/submit/new") && method === "POST") {
        return new Response(
          JSON.stringify({
            contract: { id: "contract-1" },
            client_cin: "AA12345",
            service_identifier: "+2126123456789",
            provisioning_mode: "new_contract",
            document_download_url: "/api/v1/landing/contracts/contract-1/document?token=abc",
          }),
          { status: 200, headers: { "Content-Type": "application/json" } },
        );
      }

      return new Response("{}", { status: 200, headers: { "Content-Type": "application/json" } });
    });

    return fetchMock;
  }

  it("loads bootstrap and lets user start new-subscription flow", async () => {
    installFetchMock();
    render(<LandingPage />);

    await waitFor(() => {
      expect(screen.getByRole("heading", { level: 1 })).toHaveTextContent(
        "Client Subscription Portal",
      );
    });

    fireEvent.click(screen.getByRole("button", { name: /Subscribe New Service/i }));
    expect(
      screen.getByRole("heading", { level: 2, name: "Choose Service and Offer" }),
    ).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: /Mobile Flex/i }));
    fireEvent.click(screen.getByRole("button", { name: "Continue" }));
    expect(screen.getByRole("heading", { level: 2, name: "Phone Criteria" })).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "Continue to Form" }));
    expect(screen.getByRole("heading", { level: 2, name: "Personal Information" })).toBeInTheDocument();

    vi.restoreAllMocks();
  });

  it("toggles mobile phone field disabled state between new and existing modes", async () => {
    installFetchMock();
    render(<LandingPage />);

    await waitFor(() => {
      expect(screen.getByRole("button", { name: /Subscribe New Service/i })).toBeInTheDocument();
    });

    fireEvent.click(screen.getByRole("button", { name: /Subscribe New Service/i }));
    fireEvent.click(screen.getByRole("button", { name: /Mobile Flex/i }));
    fireEvent.click(screen.getByRole("button", { name: "Continue" }));
    fireEvent.click(screen.getByRole("button", { name: "Continue to Form" }));

    const newNumberInput = screen.getByLabelText("Phone Number") as HTMLInputElement;
    expect(newNumberInput.disabled).toBe(true);

    fireEvent.click(screen.getByRole("button", { name: "Back" }));
    fireEvent.click(screen.getByRole("button", { name: "Existing Number" }));
    fireEvent.click(screen.getByRole("button", { name: "Continue to Form" }));

    const existingNumberInput = screen.getByLabelText("Phone Number") as HTMLInputElement;
    expect(existingNumberInput.disabled).toBe(false);

    vi.restoreAllMocks();
  });

  it("allows CIN-only verification in upgrade flow before loading subscriptions", async () => {
    const fetchMock = installFetchMock();
    render(<LandingPage />);

    await waitFor(() => {
      expect(screen.getByRole("button", { name: /Upgrade \/ Downgrade/i })).toBeInTheDocument();
    });

    fireEvent.click(screen.getByRole("button", { name: /Upgrade \/ Downgrade/i }));
    fireEvent.change(screen.getByLabelText("CIN"), { target: { value: "AA12345" } });
    fireEvent.click(screen.getByRole("button", { name: "Verify CIN and Find Offers" }));

    await waitFor(() => {
      expect(screen.getByRole("heading", { level: 2, name: "Current Offer and Target Offer" })).toBeInTheDocument();
    });

    const calls = fetchMock.mock.calls.map((entry) => String(entry[0]));
    expect(calls.some((url) => url.endsWith("/api/v1/landing/clients/verify-cin"))).toBe(true);
    expect(calls.some((url) => url.endsWith("/api/v1/landing/clients/verify"))).toBe(false);

    vi.restoreAllMocks();
  });

  it("loads billing invoices after CIN verification and shows download links", async () => {
    const fetchMock = installFetchMock();
    render(<LandingPage />);

    await waitFor(() => {
      expect(screen.getByRole("button", { name: /Check Billing & Invoices/i })).toBeInTheDocument();
    });

    fireEvent.click(screen.getByRole("button", { name: /Check Billing & Invoices/i }));
    fireEvent.change(screen.getByLabelText("CIN"), { target: { value: "AA12345" } });
    fireEvent.click(screen.getByRole("button", { name: "Verify CIN and Load Invoices" }));

    await waitFor(() => {
      expect(screen.getByRole("heading", { level: 2, name: "My Invoices" })).toBeInTheDocument();
    });
    expect(screen.getByText("invoice-")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Download Invoice PDF" })).toBeInTheDocument();

    const calls = fetchMock.mock.calls.map((entry) => String(entry[0]));
    expect(calls.some((url) => url.endsWith("/api/v1/landing/clients/verify-cin"))).toBe(true);
    expect(calls.some((url) => url.endsWith("/api/v1/landing/clients/verify"))).toBe(false);
    expect(calls.some((url) => url.includes("/api/v1/landing/clients/AA12345/invoices"))).toBe(true);

    vi.restoreAllMocks();
  });
});
