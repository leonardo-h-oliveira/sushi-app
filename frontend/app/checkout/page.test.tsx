import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it } from "vitest";

import CheckoutPage from "./page";

const item = { product_id: 1, name: "Temaki Salmão", quantity: 1, addon_ids: [], addon_names: [], notes: "", unit_total: "29.90" };

beforeEach(() => {
  localStorage.clear();
  localStorage.setItem("sushi-cart", JSON.stringify([item]));
});

describe("CheckoutPage", () => {
  it("requires customer and delivery information", async () => {
    render(<CheckoutPage />);
    await screen.findByRole("heading", { name: "Como vamos entregar?" });

    fireEvent.click(screen.getByRole("button", { name: /Revisar pedido/ }));
    expect(screen.getByRole("alert")).toHaveTextContent("nome e telefone");
    fireEvent.change(screen.getByLabelText("Nome completo"), { target: { value: "Ana Sushi" } });
    fireEvent.change(screen.getByLabelText("Telefone"), { target: { value: "35999999999" } });
    fireEvent.click(screen.getByRole("button", { name: /Revisar pedido/ }));
    expect(screen.getByRole("alert")).toHaveTextContent("rua, número e bairro");
  });

  it("supports pickup and confirms a valid order review", async () => {
    render(<CheckoutPage />);
    await screen.findByRole("heading", { name: "Como vamos entregar?" });
    fireEvent.change(screen.getByLabelText("Nome completo"), { target: { value: "Ana Sushi" } });
    fireEvent.change(screen.getByLabelText("Telefone"), { target: { value: "35999999999" } });
    fireEvent.click(screen.getByLabelText(/Retirada/));
    fireEvent.click(screen.getByRole("button", { name: /Revisar pedido/ }));

    await waitFor(() => expect(screen.getByRole("heading", { name: "Pedido revisado." })).toBeInTheDocument());
    expect(JSON.parse(localStorage.getItem("pending-order") ?? "{}").fulfillment).toBe("pickup");
  });
});
