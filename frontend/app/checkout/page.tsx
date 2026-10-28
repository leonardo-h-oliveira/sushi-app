"use client";

import { FormEvent, useEffect, useMemo, useState } from "react";
import Link from "next/link";

import type { CartItem } from "@/types/cart";
import { cartItemsToOrderItems, createOrder, OrderRequestError } from "@/lib/order-api";
import type { OrderResult } from "@/lib/order-api";
import { DEFAULT_STORE_SETTINGS, fetchStoreSettings, type StoreSettings } from "@/lib/store-settings";

const money = new Intl.NumberFormat("pt-BR", { style: "currency", currency: "BRL" });

export default function CheckoutPage() {
  const [items, setItems] = useState<CartItem[]>([]);
  const [fulfillment, setFulfillment] = useState<"delivery" | "pickup">("delivery");
  const [payment, setPayment] = useState<"pix" | "card_on_delivery" | "cash">("pix");
  const [customerName, setCustomerName] = useState("");
  const [phone, setPhone] = useState("");
  const [address, setAddress] = useState({ street: "", number: "", neighborhood: "", city: "Poços de Caldas", state: "MG", complement: "" });
  const [notes, setNotes] = useState("");
  const [changeFor, setChangeFor] = useState("");
  const [error, setError] = useState("");
  const [confirmed, setConfirmed] = useState(false);
  const [confirmedOrder, setConfirmedOrder] = useState<OrderResult | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [store, setStore] = useState<StoreSettings>(DEFAULT_STORE_SETTINGS);
  const [settingsReady, setSettingsReady] = useState(false);
  const [settingsError, setSettingsError] = useState("");

  async function loadSettings() {
    setSettingsReady(false);
    setSettingsError("");
    try {
      const settings = await fetchStoreSettings();
      setStore(settings);
      if (!settings.delivery_enabled && settings.pickup_enabled) setFulfillment("pickup");
      else if (!settings.pickup_enabled && settings.delivery_enabled) setFulfillment("delivery");
      if (!settings.pix_enabled) {
        if (settings.card_on_delivery_enabled) setPayment("card_on_delivery");
        else if (settings.cash_enabled) setPayment("cash");
      }
      setSettingsReady(true);
    } catch {
      setSettingsError("Não foi possível carregar as regras da loja. Tente novamente.");
    }
  }

  useEffect(() => {
    // localStorage is only available after hydration; this synchronizes browser state once.
    try {
      const stored = JSON.parse(localStorage.getItem("sushi-cart") ?? "[]");
      // eslint-disable-next-line react-hooks/set-state-in-effect -- hydrate browser-only cart state.
      setItems(Array.isArray(stored) ? stored : []);
    } catch {
      setItems([]);
    }
    const storedFulfillment = localStorage.getItem("sushi-fulfillment");
    if (storedFulfillment === "pickup" || storedFulfillment === "delivery") {
      setFulfillment(storedFulfillment);
    }
    void loadSettings();
  }, []);

  const subtotal = useMemo(() => items.reduce((total, item) => total + Number(item.unit_total ?? 0) * item.quantity, 0), [items]);
  const deliveryFee = fulfillment === "delivery" ? Number(store.delivery_fee) : 0;
  const total = subtotal + deliveryFee;

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!settingsReady || submitting) return;
    if (!store.is_open) return setError("O estabelecimento está fechado para novos pedidos.");
    if (subtotal < Number(store.minimum_order)) return setError(`O pedido mínimo é ${money.format(Number(store.minimum_order))}.`);
    if (!customerName.trim() || !phone.trim()) {
      setError("Informe seu nome e telefone para continuar.");
      return;
    }
    if (fulfillment === "delivery" && (!address.street.trim() || !address.number.trim() || !address.neighborhood.trim())) {
      setError("Para entrega, informe rua, número e bairro.");
      return;
    }
    if (payment === "cash" && !changeFor.trim()) {
      setError("Informe para qual valor precisamos preparar o troco.");
      return;
    }
    setSubmitting(true);
    try {
      const order = await createOrder({
        customer_name: customerName.trim(), phone: phone.trim(), fulfillment_method: fulfillment,
        payment_method: payment, address: fulfillment === "delivery" ? address : null,
        notes: `${notes}${payment === "cash" ? ` Troco para ${changeFor}.` : ""}`.trim() || null,
        items: cartItemsToOrderItems(items),
        expected_total: total.toFixed(2),
      });
      localStorage.setItem("last-order-tracking-token", order.tracking_token);
      localStorage.removeItem("sushi-cart");
      setConfirmedOrder(order);
      setError("");
      setConfirmed(true);
    } catch (requestError) {
      if (requestError instanceof OrderRequestError && (requestError.status === 409 || requestError.status === 422)) {
        await loadSettings();
      }
      setError(requestError instanceof Error ? requestError.message : "Não foi possível enviar o pedido.");
    } finally {
      setSubmitting(false);
    }
  }

  if (confirmed) {
    if (!confirmedOrder) return null;
    return <main className="state-page"><span className="state-symbol" aria-hidden="true">✓</span><p className="eyebrow">Pedido confirmado</p><h1>Obrigado por pedir com a gente.</h1><p>Seu número é <strong>{confirmedOrder.number}</strong>.</p><section className="order-confirmation" aria-label="Resumo do pedido"><ul>{confirmedOrder.items.map((item, index) => <li key={`${item.product_name}-${index}`}>{item.quantity}× {item.product_name} — {money.format(Number(item.total))}</li>)}</ul><p>Recebimento: <strong>{confirmedOrder.fulfillment_method === "delivery" ? "Entrega" : "Retirada"}</strong></p><p>Pagamento: <strong>{confirmedOrder.payment_method === "pix" ? "PIX" : confirmedOrder.payment_method === "cash" ? "Dinheiro" : "Cartão na entrega"}</strong></p><p>Status: <strong>Recebido</strong></p><p>Total: <strong>{money.format(Number(confirmedOrder.total))}</strong></p></section><Link className="primary-button" href={`/orders/${confirmedOrder.tracking_token}`}>Acompanhar pedido →</Link></main>;
  }

  if (items.length === 0) {
    return <main className="state-page"><span className="state-symbol" aria-hidden="true">○</span><p className="eyebrow">Checkout</p><h1>Sua sacola está vazia.</h1><p>Adicione um item antes de continuar.</p><Link className="primary-button" href="/">Explorar o cardápio →</Link></main>;
  }

  if (!settingsReady) return <main className="state-page"><h1>Checkout</h1>{settingsError ? <><p role="alert">{settingsError}</p><button className="primary-button" onClick={() => void loadSettings()}>Tentar novamente</button></> : <p role="status">Carregando as regras da loja…</p>}<Link href="/cart">Voltar à sacola</Link></main>;

  return (
    <main className="checkout-page">
      <header className="site-header"><Link className="brand" href="/" aria-label="Sushi Poços, início"><span className="brand-logo" aria-hidden="true" /><span><strong>Sushi Poços</strong><small>cozinha japonesa</small></span></Link><Link className="back-link" href="/cart">← Voltar à sacola</Link></header>
      <section className="checkout-content" aria-labelledby="checkout-title">
        <p className="eyebrow">Último passo</p><h1 id="checkout-title">Como vamos entregar?</h1>
        <form className="checkout-layout" onSubmit={submit} noValidate>
          <div className="checkout-form">
            <fieldset><legend>Seus dados</legend><label>Nome completo<input required value={customerName} onChange={(event) => setCustomerName(event.target.value)} placeholder="Como podemos chamar você?" /></label><label>Telefone<input required value={phone} onChange={(event) => setPhone(event.target.value)} placeholder="(35) 99999-9999" inputMode="tel" /></label></fieldset>
            <fieldset><legend>Recebimento</legend><div className="choice-grid">{store.delivery_enabled && <label className={fulfillment === "delivery" ? "choice selected" : "choice"}><input type="radio" name="fulfillment" checked={fulfillment === "delivery"} onChange={() => { setFulfillment("delivery"); localStorage.setItem("sushi-fulfillment", "delivery"); }} /> Entrega <small>Receba em casa</small></label>}{store.pickup_enabled && <label className={fulfillment === "pickup" ? "choice selected" : "choice"}><input type="radio" name="fulfillment" checked={fulfillment === "pickup"} onChange={() => { setFulfillment("pickup"); localStorage.setItem("sushi-fulfillment", "pickup"); }} /> Retirada <small>Na nossa casa</small></label>}</div></fieldset>
            {fulfillment === "delivery" && <fieldset><legend>Endereço de entrega</legend><div className="field-row"><label>Rua<input required value={address.street} onChange={(event) => setAddress({ ...address, street: event.target.value })} /></label><label>Número<input required value={address.number} onChange={(event) => setAddress({ ...address, number: event.target.value })} /></label></div><div className="field-row"><label>Bairro<input required value={address.neighborhood} onChange={(event) => setAddress({ ...address, neighborhood: event.target.value })} /></label><label>Complemento<input value={address.complement} onChange={(event) => setAddress({ ...address, complement: event.target.value })} /></label></div></fieldset>}
            <fieldset><legend>Pagamento</legend><div className="payment-list">{store.pix_enabled && <label><input type="radio" name="payment" checked={payment === "pix"} onChange={() => setPayment("pix")} /> PIX <span>Pagamento instantâneo</span></label>}{store.card_on_delivery_enabled && <label><input type="radio" name="payment" checked={payment === "card_on_delivery"} onChange={() => setPayment("card_on_delivery")} /> Cartão na entrega <span>Leve sua maquininha</span></label>}{store.cash_enabled && <label><input type="radio" name="payment" checked={payment === "cash"} onChange={() => setPayment("cash")} /> Dinheiro <span>Pagamento na entrega</span></label>}</div>{payment === "cash" && store.cash_enabled && <label>Troco para<input required value={changeFor} onChange={(event) => setChangeFor(event.target.value)} placeholder="Ex.: R$ 100,00" /></label>}</fieldset>
            <fieldset><legend>Observações do pedido</legend><textarea value={notes} maxLength={240} onChange={(event) => setNotes(event.target.value)} placeholder="Alguma observação para a nossa equipe?" /></fieldset>
            {error && <p className="form-error" role="alert">{error}</p>}
            <button className="primary-button confirm-button" type="submit" disabled={submitting || !store.is_open}>{submitting ? "Enviando pedido..." : store.is_open ? `Confirmar pedido · ${money.format(total)}` : "Estabelecimento fechado"}</button>
          </div>
          <aside className="checkout-summary"><h2>Resumo final</h2>{items.map((item, index) => <div className="summary-item" key={`${item.product_id}-${index}`}><span>{item.quantity}× {item.name}</span><strong>{money.format(Number(item.unit_total) * item.quantity)}</strong></div>)}<dl><div><dt>Subtotal</dt><dd>{money.format(subtotal)}</dd></div><div><dt>Entrega</dt><dd>{deliveryFee ? money.format(deliveryFee) : "Grátis"}</dd></div><div className="total-line"><dt>Total</dt><dd>{money.format(total)}</dd></div></dl></aside>
        </form>
      </section>
    </main>
  );
}
