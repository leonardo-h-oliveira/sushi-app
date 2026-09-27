"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";

import type { CartItem } from "@/types/cart";

const money = new Intl.NumberFormat("pt-BR", { style: "currency", currency: "BRL" });
const DELIVERY_FEE = 5;

export default function CartPage() {
  const [items, setItems] = useState<CartItem[]>([]);
  const [fulfillment, setFulfillment] = useState<"delivery" | "pickup">("delivery");

  useEffect(() => {
    const stored = JSON.parse(localStorage.getItem("sushi-cart") ?? "[]") as CartItem[];
    // localStorage is only available after hydration; synchronize browser state once.
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setItems(stored);
  }, []);

  const subtotal = useMemo(
    () => items.reduce((total, item) => total + Number(item.unit_total ?? 0) * item.quantity, 0),
    [items],
  );
  const deliveryFee = fulfillment === "delivery" && items.length > 0 ? DELIVERY_FEE : 0;

  function persist(nextItems: CartItem[]) {
    setItems(nextItems);
    localStorage.setItem("sushi-cart", JSON.stringify(nextItems));
  }

  function changeQuantity(index: number, delta: number) {
    const nextItems = items.map((item, itemIndex) => itemIndex === index
      ? { ...item, quantity: Math.max(1, item.quantity + delta) }
      : item);
    persist(nextItems);
  }

  function removeItem(index: number) {
    persist(items.filter((_, itemIndex) => itemIndex !== index));
  }

  return (
    <main className="cart-page">
      <header className="site-header">
        <Link className="brand" href="/" aria-label="Sushi Poços, início">
          <span className="brand-mark" aria-hidden="true">SP</span>
          <span><strong>Sushi Poços</strong><small>cozinha japonesa</small></span>
        </Link>
        <Link className="back-link" href="/">← Voltar ao cardápio</Link>
      </header>
      <section className="cart-content" aria-labelledby="cart-title">
        <p className="eyebrow">Seu pedido</p>
        <h1 id="cart-title">Sua sacola</h1>
        {items.length === 0 ? (
          <div className="empty-state cart-empty">
            <span aria-hidden="true">○</span>
            <h2>Ainda não há itens por aqui.</h2>
            <p>Escolha seus favoritos no cardápio e eles aparecem nesta sacola.</p>
            <Link className="primary-button" href="/">Explorar o cardápio →</Link>
          </div>
        ) : (
          <div className="cart-layout">
            <div className="cart-items" aria-label="Itens do pedido">
              {items.map((item, index) => (
                <article className="cart-item" key={`${item.product_id}-${index}`}>
                  <div><h2>{item.name}</h2>
                    {item.variant_names?.length > 0 && <p>{item.variant_names.join(" · ")}</p>}
                    {item.addon_names?.length > 0 && <p>+ {item.addon_names.join(", ")}</p>}
                    {item.notes && <p>“{item.notes}”</p>}
                  </div>
                  <strong>{money.format(Number(item.unit_total) * item.quantity)}</strong>
                  <div className="cart-item-actions">
                    <div className="quantity-control" aria-label={`Quantidade de ${item.name}`}>
                      <button type="button" onClick={() => changeQuantity(index, -1)} aria-label={`Diminuir ${item.name}`}>−</button>
                      <output>{item.quantity}</output>
                      <button type="button" onClick={() => changeQuantity(index, 1)} aria-label={`Aumentar ${item.name}`}>+</button>
                    </div>
                    <button className="remove-button" type="button" onClick={() => removeItem(index)}>Remover</button>
                  </div>
                </article>
              ))}
            </div>
            <aside className="cart-summary" aria-label="Resumo do pedido">
              <h2>Resumo</h2>
              <label className="fulfillment-option"><input type="radio" name="fulfillment" checked={fulfillment === "delivery"} onChange={() => setFulfillment("delivery")} /> Entrega <span>{money.format(DELIVERY_FEE)}</span></label>
              <label className="fulfillment-option"><input type="radio" name="fulfillment" checked={fulfillment === "pickup"} onChange={() => setFulfillment("pickup")} /> Retirada <span>Grátis</span></label>
              <dl><div><dt>Subtotal</dt><dd>{money.format(subtotal)}</dd></div><div><dt>Entrega</dt><dd>{deliveryFee ? money.format(deliveryFee) : "Grátis"}</dd></div><div className="total-line"><dt>Total</dt><dd>{money.format(subtotal + deliveryFee)}</dd></div></dl>
              <Link className="primary-button checkout-button" href="/checkout">Continuar para checkout →</Link>
              <p className="checkout-hint">Você poderá revisar endereço e pagamento na próxima etapa.</p>
            </aside>
          </div>
        )}
      </section>
    </main>
  );
}
