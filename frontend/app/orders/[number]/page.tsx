"use client";

import { useEffect, useState } from "react";
import Link from "next/link";

const labels: Record<string, string> = { received: "Recebido", preparing: "Em preparo", ready: "Pronto", out_for_delivery: "Saiu para entrega", completed: "Concluído", cancelled: "Cancelado" };

export default function OrderTrackingPage({ params }: { params: Promise<{ number: string }> }) {
  const [number, setNumber] = useState("");
  const [status, setStatus] = useState("received");
  const [error, setError] = useState("");

  useEffect(() => {
    params.then(({ number: orderNumber }) => {
      setNumber(orderNumber);
      fetch(`${process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000"}/orders/${orderNumber}`)
        .then((response) => response.ok ? response.json() : Promise.reject(new Error("Pedido não encontrado.")))
        .then((order: { status: string }) => setStatus(order.status))
        .catch((requestError: Error) => setError(requestError.message));
    });
  }, [params]);

  return <main className="state-page order-tracking"><span className="state-symbol" aria-hidden="true">{status === "completed" ? "✓" : "◌"}</span><p className="eyebrow">Pedido {number}</p><h1>{error || labels[status] || "Atualizando..."}</h1><p>{error ? "Confira o número do pedido e tente novamente." : "Estamos cuidando de cada detalhe. Você pode voltar aqui para consultar o andamento."}</p><Link className="primary-button" href="/">Voltar ao cardápio</Link></main>;
}
