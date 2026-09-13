import { render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import OrderTrackingPage from "./page";

beforeEach(() => {
  vi.stubGlobal("fetch", vi.fn().mockResolvedValue({
    ok: true,
    json: async () => ({
      number: "SP260908-ABC123",
      status: "preparing",
      fulfillment_method: "delivery",
      payment_method: "pix",
      subtotal: "29.90",
      delivery_fee: "5.00",
      total: "34.90",
      items: [{
        product_name: "Temaki Salmão",
        quantity: 1,
        unit_price: "29.90",
        total: "29.90",
      }],
    }),
  }));
});

describe("OrderTrackingPage", () => {
  it("shows the current status and complete customer summary", async () => {
    render(<OrderTrackingPage params={Promise.resolve({ number: "SP260908-ABC123" })} />);

    expect(await screen.findByRole("heading", { name: "Em preparo" })).toBeInTheDocument();
    const details = screen.getByRole("region", { name: "Detalhes do pedido" });
    expect(details).toHaveTextContent("Temaki Salmão");
    expect(details).toHaveTextContent("Entrega");
    expect(details).toHaveTextContent("PIX");
    expect(details).toHaveTextContent("R$ 34,90");
  });
});
