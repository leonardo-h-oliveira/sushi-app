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
  const [original, setOriginal] = useState<StoreSettings | null>(null);
  const [loading, setLoading] = useState(true);

  async function loadSettings() {
    setLoading(true);
    setOriginal(null);
    setMessage("");
    try {
      const response = await fetch(`${API_URL}/admin/store-settings`, { credentials: "include" });
      if (response.status === 401) { setAuthenticated(false); return; }
      if (!response.ok) throw new Error("load failed");
      const data: StoreSettings = await response.json();
      setSettings(data);
      setOriginal(data);
    } catch {
      setMessage("Não foi possível carregar as configurações. Tente novamente.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void Promise.resolve().then(loadSettings);
  }, []);

  async function save(event: FormEvent) {
    event.preventDefault();
    if (!original || loading || saving) return;
    const edited = { ...settings, delivery_neighborhoods: settings.delivery_neighborhoods.map((name) => name.trim()).filter(Boolean), closed_dates: settings.closed_dates.map((date) => date.trim()).filter(Boolean) };
    const changes = Object.fromEntries(Object.entries(edited).filter(([key, value]) => JSON.stringify(value) !== JSON.stringify(original[key as keyof StoreSettings])));
    if (Object.keys(changes).length === 0) { setMessage("Nenhuma alteração para salvar."); return; }
    setSaving(true);
    setMessage("");
    try {
      const response = await fetch(`${API_URL}/admin/store-settings`, {
      method: "PATCH",
      credentials: "include",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(changes),
    });
    if (response.status === 401) setAuthenticated(false);
    else if (!response.ok) setMessage("Não foi possível salvar. Confira os valores informados.");
    else {
      const data: StoreSettings = await response.json();
      setSettings(data);
      setOriginal(data);
      setMessage("Configurações salvas.");
    }
    } catch {
      setMessage("Não foi possível salvar. Confira sua conexão e tente novamente.");
    } finally {
      setSaving(false);
    }
  }

  if (!authenticated) return <main className="mx-auto max-w-md px-6 py-20"><h1 className="text-3xl font-black">Configurações</h1><p className="my-4">Entre no painel do estabelecimento primeiro.</p><Link className="font-bold text-orange-600 underline" href="/admin/orders">Abrir acesso do estabelecimento</Link></main>;

  const toggle = (field: keyof StoreSettings, label: string) => (
    <label className="flex items-center justify-between gap-4 rounded-xl border p-4"><span className="font-bold">{label}</span><input type="checkbox" checked={Boolean(settings[field])} onChange={(event) => setSettings({ ...settings, [field]: event.target.checked })} /></label>
  );

  return (
    <main className="mx-auto min-h-screen max-w-3xl px-6 py-10">
      <header className="mb-8"><p className="text-sm font-semibold uppercase tracking-[0.2em] text-orange-600">Sushi Poços</p><h1 className="text-4xl font-black">Configurações do estabelecimento</h1><nav className="mt-4 flex gap-4 text-sm font-bold"><Link href="/admin/orders">Pedidos</Link><Link href="/admin/menu">Cardápio</Link></nav></header>
      <form className="space-y-6 rounded-2xl bg-white p-6 shadow-sm" onSubmit={save}>
        {loading && <p role="status">Carregando configurações…</p>}
        {!loading && !original && <button type="button" onClick={() => void loadSettings()}>Tentar novamente</button>}
        {message && <p role="status" className="rounded-xl bg-slate-100 p-3">{message}</p>}
        <fieldset disabled={loading || !original || saving} className="space-y-6">
        <section className="space-y-3"><h2 className="text-xl font-black">Funcionamento</h2>{toggle("is_open", "Aberto para novos pedidos")}{toggle("delivery_enabled", "Aceitar entrega")}{toggle("pickup_enabled", "Aceitar retirada")}</section>
        <section className="grid gap-4 md:grid-cols-2"><label className="font-bold">Taxa de entrega<input className="mt-2 w-full rounded-xl border p-3" type="number" min="0" step="0.01" value={settings.delivery_fee} onChange={(event) => setSettings({ ...settings, delivery_fee: event.target.value })} /></label><label className="font-bold">Pedido mínimo<input className="mt-2 w-full rounded-xl border p-3" type="number" min="0" step="0.01" value={settings.minimum_order} onChange={(event) => setSettings({ ...settings, minimum_order: event.target.value })} /></label></section>
        <section className="space-y-3"><h2 className="text-xl font-black">Formas de pagamento</h2>{toggle("pix_enabled", "PIX")}{toggle("card_on_delivery_enabled", "Cartão na entrega")}{toggle("cash_enabled", "Dinheiro")}</section>
        <section className="space-y-3"><h2 className="text-xl font-black">Área de entrega</h2><p>Taxa única para os bairros cadastrados em Poços de Caldas, MG. Cadastre um bairro por linha.</p><label className="block font-bold">Bairros atendidos<textarea className="mt-2 w-full rounded-xl border p-3" rows={5} value={settings.delivery_neighborhoods.join("\n")} onChange={(event) => setSettings({ ...settings, delivery_neighborhoods: event.target.value.split("\n") })} /></label></section>
        <section className="space-y-3"><h2 className="text-xl font-black">Horários de atendimento</h2><p>Horário de São Paulo. Um fechamento anterior à abertura termina no dia seguinte. Fechar a loja manualmente sempre bloqueia novos pedidos.</p>{toggle("schedule_enabled", "Usar horários automáticos")}
          {["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"].map((day, weekday) => {
            const window = settings.opening_hours.find((entry) => entry.weekday === weekday);
            const updateWindow = (field: "opens" | "closes", value: string) => setSettings({ ...settings, opening_hours: settings.opening_hours.map((entry) => entry.weekday === weekday ? { ...entry, [field]: value } : entry) });
            return <div key={day} className="flex flex-wrap items-center gap-3 rounded-xl border p-3"><label><input type="checkbox" checked={Boolean(window)} onChange={(event) => setSettings({ ...settings, opening_hours: event.target.checked ? [...settings.opening_hours, { weekday, opens: "18:00", closes: "23:00" }] : settings.opening_hours.filter((entry) => entry.weekday !== weekday) })} /> {day}</label>{window && <><label>Abre <input aria-label={`Abertura ${day}`} type="time" required value={window.opens} onChange={(event) => updateWindow("opens", event.target.value)} /></label><label>Fecha <input aria-label={`Fechamento ${day}`} type="time" required value={window.closes} onChange={(event) => updateWindow("closes", event.target.value)} /></label></>}</div>;
          })}
          <label className="block font-bold">Datas sem atendimento<textarea className="mt-2 w-full rounded-xl border p-3" placeholder="AAAA-MM-DD, uma data por linha" value={settings.closed_dates.join("\n")} onChange={(event) => setSettings({ ...settings, closed_dates: event.target.value.split("\n") })} /></label>
        </section>
        <section className="space-y-3"><h2 className="text-xl font-black">Instruções do PIX</h2><label className="block font-bold">Como pagar por PIX<textarea className="mt-2 w-full rounded-xl border p-3" maxLength={1000} value={settings.pix_instructions} onChange={(event) => setSettings({ ...settings, pix_instructions: event.target.value })} /></label><p>Este texto aparece para o cliente. Use apenas dados de recebimento autorizados pelo restaurante. A confirmação do pagamento é feita pela equipe.</p></section>
        <section className="space-y-3"><h2 className="text-xl font-black">Liberação operacional</h2><p>Revise bairros, valores, horários, pagamentos e cardápio antes de liberar pedidos reais. A loja permanece fechada em ambientes publicados enquanto esta confirmação estiver desmarcada.</p>{toggle("operations_ready", "Regras revisadas para receber pedidos reais")}</section>
        <button className="rounded-xl bg-slate-950 px-5 py-3 font-bold text-white" disabled={saving}>{saving ? "Salvando…" : "Salvar configurações"}</button>
        </fieldset>
      </form>
    </main>
  );
}
