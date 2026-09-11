import { fireEvent, render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it } from "vitest";

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
    variant_groups: [{
      id: 21,
      name: "Preparo",
      required: true,
      active: true,
      variants: [
        { id: 31, name: "Fresco", price_delta: "0.00", active: true },
        { id: 32, name: "Grelhado", price_delta: "2.00", active: true },
      ],
    }],
  },
];

beforeEach(() => localStorage.clear());

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
    fireEvent.click(screen.getByRole("radio", { name: /Fresco/ }));
    fireEvent.click(screen.getByRole("checkbox", { name: /Cream cheese extra/ }));
    fireEvent.click(screen.getByRole("button", { name: "Aumentar quantidade" }));

    expect(screen.getByRole("button", { name: /Adicionar.*66,80/ })).toBeInTheDocument();
  });

  it("requires variants and saves selected option snapshots in the cart", () => {
    render(<MenuScreen categories={categories} products={products} />);

    fireEvent.click(screen.getByRole("button", { name: "Configurar Temaki Salmão" }));
    fireEvent.click(screen.getByRole("button", { name: /Adicionar/ }));
    expect(screen.getByText(/Escolha uma opção de Preparo/)).toBeInTheDocument();

    fireEvent.click(screen.getByRole("radio", { name: /Grelhado/ }));
    fireEvent.click(screen.getByRole("button", { name: /Adicionar.*31,90/ }));

    const [saved] = JSON.parse(localStorage.getItem("sushi-cart") ?? "[]");
    expect(saved.variant_ids).toEqual([32]);
    expect(saved.variant_names).toEqual(["Preparo: Grelhado"]);
    expect(saved.unit_total).toBe("31.90");
  });

  it("shows an accessible empty state when no products are available", () => {
    render(<MenuScreen categories={categories} products={[]} />);

    expect(screen.getByText("O cardápio está sendo atualizado.")).toBeInTheDocument();
    expect(screen.queryByRole("navigation", { name: "Categorias do cardápio" })).not.toBeInTheDocument();
  });

  it("keeps products without configurable options orderable", () => {
    const plainProduct = { ...products[0], addons: [], variant_groups: [] };
    render(<MenuScreen categories={categories} products={[plainProduct]} />);

    fireEvent.click(screen.getByRole("button", { name: "Configurar Temaki Salmão" }));
    fireEvent.click(screen.getByRole("button", { name: /Adicionar/ }));

    const [saved] = JSON.parse(localStorage.getItem("sushi-cart") ?? "[]");
    expect(saved.variant_ids).toEqual([]);
    expect(saved.addon_ids).toEqual([]);
  });
});
