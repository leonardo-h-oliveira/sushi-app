import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { MenuScreen } from "./menu-screen";

const categories = [
  { id: 1, name: "Temakis", slug: "temakis", active: true },
  { id: 2, name: "Combos", slug: "combos", active: true },
];

const products = [
  {
    id: 1,
    name: "Temaki Salmão",
    description: "Salmão fresco e cream cheese",
    price: "29.90",
    original_price: "39.90",
    discount_percent: 25,
    image_url: null,
    active: true,
    category: { id: 1, name: "Temakis", slug: "temakis" },
    addons: [{ id: 11, name: "Cream cheese extra", price_delta: "3.50", active: true }],
  },
];

describe("MenuScreen", () => {
  it("groups API products under populated categories", () => {
    render(<MenuScreen categories={categories} products={products} />);

    expect(screen.getByRole("heading", { name: "Nosso cardápio" })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Temakis" })).toBeInTheDocument();
    expect(screen.getByText("Temaki Salmão")).toBeInTheDocument();
    expect(screen.getByText("R$ 29,90")).toBeInTheDocument();
    expect(screen.getByText("R$ 39,90")).toBeInTheDocument();
    expect(screen.getByText("25% OFF")).toBeInTheDocument();
    expect(screen.queryByRole("heading", { name: "Combos" })).not.toBeInTheDocument();
  });

  it("opens product configuration and calculates quantity and add-on totals", () => {
    render(<MenuScreen categories={categories} products={products} />);

    fireEvent.click(screen.getByRole("button", { name: "Configurar Temaki Salmão" }));
    expect(screen.getByRole("dialog")).toBeInTheDocument();
    fireEvent.click(screen.getByRole("checkbox", { name: /Cream cheese extra/ }));
    fireEvent.click(screen.getByRole("button", { name: "Aumentar quantidade" }));

    expect(screen.getByRole("button", { name: /Adicionar.*66,80/ })).toBeInTheDocument();
  });

  it("shows an accessible empty state when no products are available", () => {
    render(<MenuScreen categories={categories} products={[]} />);

    expect(screen.getByText("O cardápio está sendo atualizado.")).toBeInTheDocument();
    expect(screen.queryByRole("navigation", { name: "Categorias do cardápio" })).not.toBeInTheDocument();
  });
});
