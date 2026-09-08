"use client";

import { FormEvent, useEffect, useMemo, useState } from "react";
import Link from "next/link";

import type { CartItem } from "@/types/cart";

const money = new Intl.NumberFormat("pt-BR", { style: "currency", currency: "BRL" });
const DELIVERY_FEE = 5;

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

  useEffect(() => {
    // localStorage is only available after hydration; this synchronizes browser state once.
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setItems(JSON.parse(localStorage.getItem("sushi-cart") ?? "[]") as CartItem[]);
  }, []);

  const subtotal = useMemo(() => items.reduce((total, item) => total + Number(item.unit_total ?? 0) * item.quantity, 0), [items]);
  const deliveryFee = fulfillment === "delivery" ? DELIVERY_FEE : 0;
  const total = subtotal + deliveryFee;

  function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
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
    localStorage.setItem("pending-order", JSON.stringify({ customerName, phone, fulfillment, payment, address, notes, changeFor, total: total.toFixed(2), items }));
    setError("");
    setConfirmed(true);
  }

  if (confirmed) {
    return <main className="state-page"><span className="state-symbol" aria-hidden="true">✓</span><p className="eyebrow">Tudo certo</p><h1>Pedido revisado.</h1><p>Suas informações foram preparadas para o próximo passo de confirmação.</p><Link className="primary-button" href="/cart">Voltar à sacola</Link></main>;
  }

  if (items.length === 0) {
    return <main className="state-page"><span className="state-symbol" aria-hidden="true">○</span><p className="eyebrow">Checkout</p><h1>Sua sacola está vazia.</h1><p>Adicione um item antes de continuar.</p><Link className="primary-button" href="/">Explorar o cardápio →</Link></main>;
  }

  return (
    <main className="checkout-page">
      <header className="site-header"><Link className="brand" href="/" aria-label="Sushi Poços, início"><span className="brand-mark" aria-hidden="true">SP</span><span><strong>Sushi Poços</strong><small>cozinha japonesa</small></span></Link><Link className="back-link" href="/cart">← Voltar à sacola</Link></header>
      <section className="checkout-content" aria-labelledby="checkout-title">
        <p className="eyebrow">Último passo</p><h1 id="checkout-title">Como vamos entregar?</h1>
        <form className="checkout-layout" onSubmit={submit} noValidate>
          <div className="checkout-form">
            <fieldset><legend>Seus dados</legend><label>Nome completo<input required value={customerName} onChange={(event) => setCustomerName(event.target.value)} placeholder="Como podemos chamar você?" /></label><label>Telefone<input required value={phone} onChange={(event) => setPhone(event.target.value)} placeholder="(35) 99999-9999" inputMode="tel" /></label></fieldset>
            <fieldset><legend>Recebimento</legend><div className="choice-grid"><label className={fulfillment === "delivery" ? "choice selected" : "choice"}><input type="radio" name="fulfillment" checked={fulfillment === "delivery"} onChange={() => setFulfillment("delivery")} /> Entrega <small>Receba em casa</small></label><label className={fulfillment === "pickup" ? "choice selected" : "choice"}><input type="radio" name="fulfillment" checked={fulfillment === "pickup"} onChange={() => setFulfillment("pickup")} /> Retirada <small>Na nossa casa</small></label></div></fieldset>
            {fulfillment === "delivery" && <fieldset><legend>Endereço de entrega</legend><div className="field-row"><label>Rua<input required value={address.street} onChange={(event) => setAddress({ ...address, street: event.target.value })} /></label><label>Número<input required value={address.number} onChange={(event) => setAddress({ ...address, number: event.target.value })} /></label></div><div className="field-row"><label>Bairro<input required value={address.neighborhood} onChange={(event) => setAddress({ ...address, neighborhood: event.target.value })} /></label><label>Complemento<input value={address.complement} onChange={(event) => setAddress({ ...address, complement: event.target.value })} /></label></div></fieldset>}
            <fieldset><legend>Pagamento</legend><div className="payment-list"><label><input type="radio" name="payment" checked={payment === "pix"} onChange={() => setPayment("pix")} /> PIX <span>Pagamento instantâneo</span></label><label><input type="radio" name="payment" checked={payment === "card_on_delivery"} onChange={() => setPayment("card_on_delivery")} /> Cartão na entrega <span>Leve sua maquininha</span></label><label><input type="radio" name="payment" checked={payment === "cash"} onChange={() => setPayment("cash")} /> Dinheiro <span>Pagamento na entrega</span></label></div>{payment === "cash" && <label>Troco para<input required value={changeFor} onChange={(event) => setChangeFor(event.target.value)} placeholder="Ex.: R$ 100,00" /></label>}</fieldset>
            <fieldset><legend>Observações do pedido</legend><textarea value={notes} maxLength={240} onChange={(event) => setNotes(event.target.value)} placeholder="Alguma observação para a nossa equipe?" /></fieldset>
            {error && <p className="form-error" role="alert">{error}</p>}
            <button className="primary-button confirm-button" type="submit">Revisar pedido · {money.format(total)}</button>
          </div>
          <aside className="checkout-summary"><h2>Resumo final</h2>{items.map((item, index) => <div className="summary-item" key={`${item.product_id}-${index}`}><span>{item.quantity}× {item.name}</span><strong>{money.format(Number(item.unit_total) * item.quantity)}</strong></div>)}<dl><div><dt>Subtotal</dt><dd>{money.format(subtotal)}</dd></div><div><dt>Entrega</dt><dd>{deliveryFee ? money.format(deliveryFee) : "Grátis"}</dd></div><div className="total-line"><dt>Total</dt><dd>{money.format(total)}</dd></div></dl></aside>
        </form>
      </section>
    </main>
  );
}
