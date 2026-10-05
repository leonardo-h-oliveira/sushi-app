"use client";

import { FormEvent, useEffect, useState } from "react";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000";
const statuses = ["received", "preparing", "ready", "out_for_delivery", "completed", "cancelled"] as const;

type Order = {
  number: string;
  status: string;
  customer_name?: string;
  phone?: string;
  fulfillment_method: string;
  payment_method: string;
  total: string;
  created_at: string;
  notes?: string;
  address?: { street: string; number: string; neighborhood: string; complement?: string };
  items: {
    product_name: string;
    quantity: number;
    notes?: string;
    addons: { addon_name: string }[];
    variants: { group_name: string; variant_name: string }[];
  }[];
};

export default function AdminOrdersPage() {
  const [token, setToken] = useState<string | null>(() => typeof window === "undefined" ? null : localStorage.getItem("admin-token"));
  const [username, setUsername] = useState("admin");
  const [password, setPassword] = useState("");
  const [orders, setOrders] = useState<Order[]>([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function loadOrders(session: string) {
    setLoading(true);
    const response = await fetch(`${API_URL}/orders`, { headers: { Authorization: `Bearer ${session}` } });
    if (response.status === 401) {
      localStorage.removeItem("admin-token");
      setToken(null);
      setError("Your administrator session expired. Please sign in again.");
    } else if (!response.ok) setError("Unable to load orders.");
    else setOrders(await response.json());
    setLoading(false);
  }

  // The effect synchronizes the dashboard with an existing session restored from storage.
  // eslint-disable-next-line react-hooks/set-state-in-effect
  useEffect(() => { if (token) void loadOrders(token); }, [token]);

  async function signIn(event: FormEvent) {
    event.preventDefault(); setError("");
    const response = await fetch(`${API_URL}/auth/login`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ username, password }) });
    if (!response.ok) { setError("Invalid administrator credentials."); return; }
    const session = (await response.json()).access_token as string;
    localStorage.setItem("admin-token", session); setToken(session); setPassword(""); void loadOrders(session);
  }

  async function changeStatus(number: string, status: string) {
    if (!token) return;
    const response = await fetch(`${API_URL}/orders/${number}/status`, { method: "PATCH", headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json" }, body: JSON.stringify({ status }) });
    if (response.ok) setOrders((current) => current.map((order) => order.number === number ? { ...order, status } : order));
    else setError("Unable to update this order.");
  }

  if (!token) return <main className="mx-auto flex min-h-screen max-w-md items-center px-6"><form onSubmit={signIn} className="w-full space-y-4 rounded-3xl bg-white p-8 shadow-xl"><p className="text-sm font-semibold uppercase tracking-[0.2em] text-orange-600">Sushi Poços</p><h1 className="text-3xl font-black text-slate-950">Staff sign in</h1><input aria-label="Username" value={username} onChange={(event) => setUsername(event.target.value)} className="w-full rounded-xl border p-3" placeholder="Username" /><input aria-label="Password" type="password" value={password} onChange={(event) => setPassword(event.target.value)} className="w-full rounded-xl border p-3" placeholder="Password" /><button className="w-full rounded-xl bg-slate-950 p-3 font-bold text-white">Sign in</button>{error && <p role="alert" className="text-sm text-red-600">{error}</p>}</form></main>;

  return (
    <main className="mx-auto min-h-screen max-w-6xl px-6 py-10">
      <header className="mb-8 flex items-center justify-between">
        <div><p className="text-sm font-semibold uppercase tracking-[0.2em] text-orange-600">Sushi Poços</p><h1 className="text-4xl font-black text-slate-950">Painel de pedidos</h1></div>
        <button onClick={() => { localStorage.removeItem("admin-token"); setToken(null); }} className="rounded-xl border px-4 py-2 text-sm font-bold">Sair</button>
      </header>
      {error && <p role="alert" className="mb-4 rounded-xl bg-red-50 p-3 text-red-700">{error}</p>}
      {loading ? <p>Carregando pedidos…</p> : orders.length === 0 ? <p className="rounded-2xl bg-white p-8 text-slate-600">Nenhum pedido recebido.</p> : (
        <section className="grid gap-5 md:grid-cols-2">
          {orders.map((order) => (
            <article key={order.number} className="rounded-2xl bg-white p-5 shadow-sm">
              <div className="flex items-start justify-between gap-4">
                <div><h2 className="font-black">{order.number}</h2><p className="text-sm text-slate-600">{order.customer_name} · {order.phone}</p><p className="text-xs text-slate-500">{new Date(order.created_at).toLocaleString("pt-BR")}</p></div>
                <strong>R$ {order.total}</strong>
              </div>
              <dl className="mt-4 grid gap-1 text-sm">
                <div><dt className="inline font-bold">Recebimento: </dt><dd className="inline">{order.fulfillment_method === "delivery" ? "Entrega" : "Retirada"}</dd></div>
                <div><dt className="inline font-bold">Pagamento: </dt><dd className="inline">{order.payment_method === "pix" ? "PIX" : order.payment_method === "cash" ? "Dinheiro" : "Cartão na entrega"}</dd></div>
                {order.address && <div><dt className="inline font-bold">Endereço: </dt><dd className="inline">{order.address.street}, {order.address.number} — {order.address.neighborhood}{order.address.complement ? `, ${order.address.complement}` : ""}</dd></div>}
                {order.notes && <div><dt className="inline font-bold">Observações: </dt><dd className="inline">{order.notes}</dd></div>}
              </dl>
              <ul className="my-4 space-y-2 text-sm">{order.items.map((item, index) => <li key={`${item.product_name}-${index}`}><strong>{item.quantity}× {item.product_name}</strong>{item.variants.map((variant) => <span className="block text-slate-600" key={`${variant.group_name}-${variant.variant_name}`}>{variant.group_name}: {variant.variant_name}</span>)}{item.addons.map((addon) => <span className="block text-slate-600" key={addon.addon_name}>+ {addon.addon_name}</span>)}{item.notes && <span className="block italic text-slate-600">Item: {item.notes}</span>}</li>)}</ul>
              <select aria-label={`Status do pedido ${order.number}`} value={order.status} onChange={(event) => void changeStatus(order.number, event.target.value)} className="w-full rounded-xl border p-3">{statuses.map((status) => <option key={status} value={status}>{status.replaceAll("_", " ")}</option>)}</select>
            </article>
          ))}
        </section>
      )}
    </main>
  );
}
