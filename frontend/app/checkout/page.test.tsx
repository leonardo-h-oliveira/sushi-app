import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import CheckoutPage from "./page";
import { DEFAULT_STORE_SETTINGS } from "@/lib/store-settings";

const item = { product_id: 1, name: "Temaki Salmão", quantity: 1, addon_ids: [], addon_names: [], variant_ids: [], variant_names: [], notes: "", unit_total: "29.90" };

beforeEach(() => {
  localStorage.clear();
  localStorage.setItem("sushi-cart", JSON.stringify([item]));
  vi.stubGlobal("fetch", vi.fn().mockResolvedValueOnce({ ok: true, json: async () => DEFAULT_STORE_SETTINGS }).mockResolvedValue({ ok: true, json: async () => ({ number: "SP260908-ABC123", tracking_token: "secure-tracking-token", status: "received", fulfillment_method: "pickup", payment_method: "pix", subtotal: "29.90", delivery_fee: "0.00", total: "29.90", items: [{ product_name: "Temaki Salmão", quantity: 1, unit_price: "29.90", total: "29.90" }] }) }));
});

describe("CheckoutPage", () => {
  it("blocks checkout on a settings failure and supports retry", async () => {
    vi.stubGlobal("fetch", vi.fn().mockRejectedValueOnce(new Error("offline")).mockResolvedValue({ ok: true, json: async () => DEFAULT_STORE_SETTINGS }));
    render(<CheckoutPage />);
    await screen.findByRole("alert");
    expect(screen.queryByRole("button", { name: /Confirmar pedido/ })).not.toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "Tentar novamente" }));
    expect(await screen.findByRole("button", { name: /Confirmar pedido/ })).toBeEnabled();
  });

  it("refreshes a changed fee and waits for a second explicit confirmation", async () => {
    const fetchMock = vi.fn()
      .mockResolvedValueOnce({ ok: true, json: async () => DEFAULT_STORE_SETTINGS })
      .mockResolvedValueOnce({ ok: false, status: 409, json: async () => ({ detail: { code: "price_changed", message: "O valor do pedido mudou.", subtotal: "29.90", delivery_fee: "10.00", total: "39.90" } }) })
      .mockResolvedValueOnce({ ok: true, json: async () => ({ ...DEFAULT_STORE_SETTINGS, delivery_fee: "10.00" }) });
    vi.stubGlobal("fetch", fetchMock);
    render(<CheckoutPage />);
    await screen.findByRole("button", { name: /Confirmar pedido/ });
    fireEvent.change(screen.getByLabelText("Nome completo"), { target: { value: "Ana Sushi" } });
    fireEvent.change(screen.getByLabelText("Telefone"), { target: { value: "35999999999" } });
    for (const [label, value] of [["Rua", "Rua Central"], ["Número", "10"], ["Bairro", "Centro"]]) {
      fireEvent.change(screen.getByLabelText(label), { target: { value } });
    }
    fireEvent.click(screen.getByRole("button", { name: /Confirmar pedido/ }));
    await screen.findByRole("alert");
    expect(await screen.findByRole("button", { name: /Confirmar pedido · R\$\s*39,90/ })).toBeEnabled();
    expect(fetchMock.mock.calls.filter((call) => call[1]?.method === "POST")).toHaveLength(1);
    expect(JSON.parse(fetchMock.mock.calls[1][1].body).expected_total).toBe("34.90");
    expect(localStorage.getItem("sushi-cart")).not.toBeNull();
  });

  it("requires customer and delivery information", async () => {
    render(<CheckoutPage />);
    await screen.findByRole("heading", { name: "Como vamos entregar?" });

    fireEvent.click(screen.getByRole("button", { name: /Confirmar pedido/ }));
    expect(screen.getByRole("alert")).toHaveTextContent("nome e telefone");
    fireEvent.change(screen.getByLabelText("Nome completo"), { target: { value: "Ana Sushi" } });
    fireEvent.change(screen.getByLabelText("Telefone"), { target: { value: "35999999999" } });
    fireEvent.click(screen.getByRole("button", { name: /Confirmar pedido/ }));
    expect(screen.getByRole("alert")).toHaveTextContent("rua, número e bairro");
  });

  it("supports pickup and confirms a valid order review", async () => {
    localStorage.setItem("sushi-fulfillment", "pickup");
    render(<CheckoutPage />);
    await screen.findByRole("heading", { name: "Como vamos entregar?" });
    expect(screen.getByLabelText(/Retirada/)).toBeChecked();
    expect(screen.queryByRole("group", { name: "Endereço de entrega" })).not.toBeInTheDocument();
    fireEvent.change(screen.getByLabelText("Nome completo"), { target: { value: "Ana Sushi" } });
    fireEvent.change(screen.getByLabelText("Telefone"), { target: { value: "35999999999" } });
    fireEvent.click(screen.getByRole("button", { name: /Confirmar pedido/ }));

    await waitFor(() => expect(screen.getByRole("heading", { name: "Obrigado por pedir com a gente." })).toBeInTheDocument());
    expect(localStorage.getItem("last-order-tracking-token")).toBe("secure-tracking-token");
    expect(screen.getByRole("link", { name: /Acompanhar pedido/ })).toHaveAttribute("href", "/orders/secure-tracking-token");
    expect(screen.getByRole("region", { name: "Resumo do pedido" })).toHaveTextContent("Temaki Salmão");
    expect(screen.getByRole("region", { name: "Resumo do pedido" })).toHaveTextContent("R$ 29,90");
  });
});
