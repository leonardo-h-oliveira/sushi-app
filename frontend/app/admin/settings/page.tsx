"use client";

import { FormEvent, useEffect, useState } from "react";
import Link from "next/link";

import { DEFAULT_STORE_SETTINGS, type StoreSettings } from "@/lib/store-settings";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000";

export default function AdminSettingsPage() {
  const [authenticated, setAuthenticated] = useState(true);
  const [settings, setSettings] = useState<StoreSettings>(DEFAULT_STORE_SETTINGS);
  const [message, setMessage] = useState("");
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    void fetch(`${API_URL}/admin/store-settings`, { credentials: "include" }).then(async (response) => {
      if (response.status === 401) return setAuthenticated(false);
      if (!response.ok) return setMessage("Não foi possível carregar as configurações.");
      setSettings(await response.json());
    });
  }, []);

  async function save(event: FormEvent) {
    event.preventDefault();
    setSaving(true);
    setMessage("");
    const response = await fetch(`${API_URL}/admin/store-settings`, {
      method: "PATCH",
      credentials: "include",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ ...settings, delivery_fee: Number(settings.delivery_fee), minimum_order: Number(settings.minimum_order) }),
    });
    if (response.status === 401) setAuthenticated(false);
    else if (!response.ok) setMessage("Não foi possível salvar. Confira os valores informados.");
    else {
      setSettings(await response.json());
      setMessage("Configurações salvas.");
    }
    setSaving(false);
  }

  if (!authenticated) return <main className="mx-auto max-w-md px-6 py-20"><h1 className="text-3xl font-black">Configurações</h1><p className="my-4">Entre no painel do estabelecimento primeiro.</p><Link className="font-bold text-orange-600 underline" href="/admin/orders">Abrir acesso do estabelecimento</Link></main>;

  const toggle = (field: keyof StoreSettings, label: string) => (
    <label className="flex items-center justify-between gap-4 rounded-xl border p-4"><span className="font-bold">{label}</span><input type="checkbox" checked={Boolean(settings[field])} onChange={(event) => setSettings({ ...settings, [field]: event.target.checked })} /></label>
  );

  return (
    <main className="mx-auto min-h-screen max-w-3xl px-6 py-10">
      <header className="mb-8"><p className="text-sm font-semibold uppercase tracking-[0.2em] text-orange-600">Sushi Poços</p><h1 className="text-4xl font-black">Configurações do estabelecimento</h1><nav className="mt-4 flex gap-4 text-sm font-bold"><Link href="/admin/orders">Pedidos</Link><Link href="/admin/menu">Cardápio</Link></nav></header>
      <form className="space-y-6 rounded-2xl bg-white p-6 shadow-sm" onSubmit={save}>
        <section className="space-y-3"><h2 className="text-xl font-black">Funcionamento</h2>{toggle("is_open", "Aberto para novos pedidos")}{toggle("delivery_enabled", "Aceitar entrega")}{toggle("pickup_enabled", "Aceitar retirada")}</section>
        <section className="grid gap-4 md:grid-cols-2"><label className="font-bold">Taxa de entrega<input className="mt-2 w-full rounded-xl border p-3" type="number" min="0" step="0.01" value={settings.delivery_fee} onChange={(event) => setSettings({ ...settings, delivery_fee: event.target.value })} /></label><label className="font-bold">Pedido mínimo<input className="mt-2 w-full rounded-xl border p-3" type="number" min="0" step="0.01" value={settings.minimum_order} onChange={(event) => setSettings({ ...settings, minimum_order: event.target.value })} /></label></section>
        <section className="space-y-3"><h2 className="text-xl font-black">Formas de pagamento</h2>{toggle("pix_enabled", "PIX")}{toggle("card_on_delivery_enabled", "Cartão na entrega")}{toggle("cash_enabled", "Dinheiro")}</section>
        {message && <p role="status" className="rounded-xl bg-slate-100 p-3">{message}</p>}
        <button className="rounded-xl bg-slate-950 px-5 py-3 font-bold text-white" disabled={saving}>{saving ? "Salvando…" : "Salvar configurações"}</button>
      </form>
    </main>
  );
}
