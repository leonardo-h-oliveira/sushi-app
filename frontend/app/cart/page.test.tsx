import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { describe, expect, it, beforeEach } from "vitest";

import CartPage from "./page";

beforeEach(() => localStorage.clear());

describe("CartPage", () => {
  it("shows an empty state when there are no stored items", async () => {
    render(<CartPage />);

    expect(await screen.findByText("Ainda não há itens por aqui.")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: /Explorar o cardápio/ })).toBeInTheDocument();
  });

  it("updates quantities, removes items and recalculates totals", async () => {
    localStorage.setItem("sushi-cart", JSON.stringify([{
      product_id: 1,
      name: "Temaki Salmão",
      quantity: 1,
      addon_ids: [],
      addon_names: [],
      variant_ids: [31],
      variant_names: ["Preparo: Fresco"],
      notes: "Pouco shoyu",
      unit_total: "29.90",
    }]));
    render(<CartPage />);

    expect(await screen.findByText("Temaki Salmão")).toBeInTheDocument();
    expect(screen.getByText("Preparo: Fresco")).toBeInTheDocument();
    expect(screen.getByText("R$ 34,90")).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "Aumentar Temaki Salmão" }));
    await waitFor(() => expect(screen.getByText("R$ 64,80")).toBeInTheDocument());
    fireEvent.click(screen.getByRole("button", { name: "Remover" }));
    expect(await screen.findByText("Ainda não há itens por aqui.")).toBeInTheDocument();
  });
});
