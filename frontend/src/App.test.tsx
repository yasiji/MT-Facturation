import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { vi } from "vitest";

import App from "./App";

describe("App", () => {
  it("renders tabbed workspace", async () => {
    vi.spyOn(globalThis, "fetch").mockImplementation(async (input) => {
      const url =
        typeof input === "string" ? input : input instanceof URL ? input.toString() : input.url;
      const listPayload = {
        data: [],
        meta: { page: 1, size: 100, total: 0, sort: null, filters: null },
      };
      if (url.includes("/api/v1/health")) {
        return new Response(JSON.stringify({ status: "ok" }), {
          status: 200,
          headers: { "Content-Type": "application/json" },
        });
      }
      if (url.includes("/openapi.json")) {
        return new Response(
          JSON.stringify({
            paths: {
              "/api/v1/customers": {},
              "/api/v1/offers": {},
              "/api/v1/contracts": {},
            },
          }),
          {
            status: 200,
            headers: { "Content-Type": "application/json" },
          }
        );
      }
      if (
        url.includes("/api/v1/customers") ||
        url.includes("/api/v1/offers") ||
        url.includes("/api/v1/contracts") ||
        url.includes("/api/v1/invoices")
      ) {
        return new Response(JSON.stringify(listPayload), {
          status: 200,
          headers: { "Content-Type": "application/json" },
        });
      }
      if (url.includes("/api/v1/collections/overview")) {
        return new Response(
          JSON.stringify({
            open_cases: 0,
            in_progress_cases: 0,
            overdue_invoices: 0,
            total_outstanding_amount: "0.00",
            bucket_totals: {
              current: "0.00",
              "1_30": "0.00",
              "31_60": "0.00",
              "61_90": "0.00",
              "90_plus": "0.00",
            },
          }),
          {
            status: 200,
            headers: { "Content-Type": "application/json" },
          }
        );
      }
      if (url.includes("/api/v1/collections/cases/") && url.includes("/actions")) {
        return new Response(JSON.stringify([]), {
          status: 200,
          headers: { "Content-Type": "application/json" },
        });
      }
      if (url.includes("/api/v1/collections/cases")) {
        return new Response(JSON.stringify(listPayload), {
          status: 200,
          headers: { "Content-Type": "application/json" },
        });
      }

      return new Response(JSON.stringify({}), {
        status: 200,
        headers: { "Content-Type": "application/json" },
      });
    });

    render(<App />);
    await waitFor(() => {
      expect(screen.getByRole("heading", { level: 1 })).toHaveTextContent(
        "MT-Facturation Control Center"
      );
    });
    expect(screen.getByRole("button", { name: "Contracts" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Clients" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Offers" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Invoices" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Collections" })).toBeInTheDocument();
    expect(screen.getByRole("heading", { level: 2, name: "Contract Provisioning" })).toBeInTheDocument();
    expect(screen.getByRole("combobox", { name: "Client Flow" })).toBeInTheDocument();

    fireEvent.click(screen.getByRole("button", { name: "Invoices" }));
    expect(screen.getByRole("heading", { level: 2, name: "Invoice Center" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Run Billing Cycle" })).toBeInTheDocument();
    expect(screen.getByRole("combobox", { name: "Service" })).toBeInTheDocument();

    fireEvent.click(screen.getByRole("button", { name: "Collections" }));
    expect(screen.getByRole("heading", { level: 2, name: "Collections Center" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Apply Filters" })).toBeInTheDocument();

    fireEvent.click(screen.getByRole("button", { name: "Clients" }));
    expect(screen.getByRole("heading", { level: 2, name: "Client Management" })).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Create Client" })).not.toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "Offers" }));
    expect(screen.getByRole("heading", { level: 2, name: "Offer Management" })).toBeInTheDocument();
    expect(screen.getByRole("textbox", { name: "Offer Name" })).toBeInTheDocument();
    expect(screen.getByRole("combobox", { name: "Service" })).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "Contracts" }));
    expect(screen.getByRole("textbox", { name: "Detected Mode" })).toBeInTheDocument();
    expect(screen.getByRole("combobox", { name: "Target Contract (Optional)" })).toBeInTheDocument();
    vi.restoreAllMocks();
  });
});
