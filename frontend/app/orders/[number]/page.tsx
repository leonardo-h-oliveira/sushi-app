"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import type { OrderResult } from "@/lib/order-api";

const labels: Record<string, string> = { received: "Recebido", preparing: "Em preparo", ready: "Pronto", out_for_delivery: "Saiu para entrega", completed: "Concluído", cancelled: "Cancelado" };
const money = new Intl.NumberFormat("pt-BR", { style: "currency", currency: "BRL" });

export default function OrderTrackingPage({ params }: { params: Promise<{ number: string }> }) {
  const [number, setNumber] = useState("");
  const [order, setOrder] = useState<OrderResult | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    params.then(({ number: orderNumber }) => {
      setNumber(orderNumber);
      fetch(`${process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000"}/orders/${orderNumber}`)
        .then((response) => response.ok ? response.json() : Promise.reject(new Error("Pedido não encontrado.")))
        .then((result: OrderResult) => setOrder(result))
        .catch((requestError: Error) => setError(requestError.message));
    });
  }, [params]);

  return <main className="state-page order-tracking"><span className="state-symbol" aria-hidden="true">{order?.status === "completed" ? "✓" : "◌"}</span><p className="eyebrow">Pedido {number}</p><h1>{error || (order ? labels[order.status] : "Atualizando...")}</h1>{error ? <p>Confira o número do pedido e tente novamente.</p> : order ? <section className="order-confirmation" aria-label="Detalhes do pedido"><ul>{order.items.map((item, index) => <li key={`${item.product_name}-${index}`}>{item.quantity}× {item.product_name} — {money.format(Number(item.total))}</li>)}</ul><p>Recebimento: <strong>{order.fulfillment_method === "delivery" ? "Entrega" : "Retirada"}</strong></p><p>Pagamento: <strong>{order.payment_method === "pix" ? "PIX" : order.payment_method === "cash" ? "Dinheiro" : "Cartão na entrega"}</strong></p><p>Total: <strong>{money.format(Number(order.total))}</strong></p></section> : <p>Consultando o andamento do seu pedido.</p>}<Link className="primary-button" href="/">Voltar ao cardápio</Link></main>;
}
