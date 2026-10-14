"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";

import type { CartItem } from "@/types/cart";
import { DEFAULT_STORE_SETTINGS, fetchStoreSettings, type StoreSettings } from "@/lib/store-settings";

const money = new Intl.NumberFormat("pt-BR", { style: "currency", currency: "BRL" });

export default function CartPage() {
  const [items, setItems] = useState<CartItem[]>([]);
  const [fulfillment, setFulfillment] = useState<"delivery" | "pickup">("delivery");
  const [store, setStore] = useState<StoreSettings>(DEFAULT_STORE_SETTINGS);

  useEffect(() => {
    const stored = JSON.parse(localStorage.getItem("sushi-cart") ?? "[]") as CartItem[];
    const storedFulfillment = localStorage.getItem("sushi-fulfillment");
    // localStorage is only available after hydration; synchronize browser state once.
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setItems(stored);
    if (storedFulfillment === "pickup" || storedFulfillment === "delivery") {
      setFulfillment(storedFulfillment);
    }
    void fetchStoreSettings().then((settings) => {
      setStore(settings);
      if ((!settings.delivery_enabled || !settings.is_open) && settings.pickup_enabled) setFulfillment("pickup");
      else if (!settings.pickup_enabled && settings.delivery_enabled) setFulfillment("delivery");
    }).catch(() => undefined);
  }, []);

  const subtotal = useMemo(
    () => items.reduce((total, item) => total + Number(item.unit_total ?? 0) * item.quantity, 0),
    [items],
  );
  const deliveryFee = fulfillment === "delivery" && items.length > 0 ? Number(store.delivery_fee) : 0;

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

  function changeFulfillment(nextFulfillment: "delivery" | "pickup") {
    setFulfillment(nextFulfillment);
    localStorage.setItem("sushi-fulfillment", nextFulfillment);
  }

  return (
    <main className="cart-page">
      <header className="site-header">
        <Link className="brand" href="/" aria-label="Sushi Poços, início">
          <span className="brand-logo" aria-hidden="true" />
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
              {!store.is_open && <p className="form-error" role="alert">O estabelecimento está fechado para novos pedidos.</p>}
              {store.delivery_enabled && <label className="fulfillment-option"><input type="radio" name="fulfillment" checked={fulfillment === "delivery"} onChange={() => changeFulfillment("delivery")} /> Entrega <span>{money.format(Number(store.delivery_fee))}</span></label>}
              {store.pickup_enabled && <label className="fulfillment-option"><input type="radio" name="fulfillment" checked={fulfillment === "pickup"} onChange={() => changeFulfillment("pickup")} /> Retirada <span>Grátis</span></label>}
              <dl><div><dt>Subtotal</dt><dd>{money.format(subtotal)}</dd></div><div><dt>Entrega</dt><dd>{deliveryFee ? money.format(deliveryFee) : "Grátis"}</dd></div><div className="total-line"><dt>Total</dt><dd>{money.format(subtotal + deliveryFee)}</dd></div></dl>
              {Number(store.minimum_order) > 0 && <p className="checkout-hint">Pedido mínimo: {money.format(Number(store.minimum_order))}</p>}
              {store.is_open && (store.delivery_enabled || store.pickup_enabled) && <Link className="primary-button checkout-button" href="/checkout">Continuar para checkout →</Link>}
              <p className="checkout-hint">Você poderá revisar endereço e pagamento na próxima etapa.</p>
            </aside>
          </div>
        )}
      </section>
    </main>
  );
}
