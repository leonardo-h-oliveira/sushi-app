"use client";

import { FormEvent, useEffect, useState } from "react";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000";

type Category = { id: number; name: string; slug: string };
type ProductOption = { id: number; name: string; price_delta: string; active: boolean };
type VariantGroup = {
  id: number;
  name: string;
  required: boolean;
  active: boolean;
  variants: ProductOption[];
};
type Product = {
  id: number;
  name: string;
  price: string;
  original_price: string | null;
  discount_percent: number | null;
  description: string;
  active: boolean;
  category: Category;
  addons: ProductOption[];
  variant_groups: VariantGroup[];
};

const EMPTY_PRODUCT = {
  name: "",
  description: "",
  price: "",
  original_price: "",
  category_id: "",
};

export default function AdminMenuPage() {
  const [token, setToken] = useState<string | null>(() =>
    typeof window === "undefined" ? null : localStorage.getItem("admin-token"),
  );
  const [categories, setCategories] = useState<Category[]>([]);
  const [products, setProducts] = useState<Product[]>([]);
  const [category, setCategory] = useState("");
  const [product, setProduct] = useState(EMPTY_PRODUCT);
  const [error, setError] = useState("");
  const [groupForm, setGroupForm] = useState({ product_id: "", name: "", required: true });
  const [variantForm, setVariantForm] = useState({ group_id: "", name: "", price_delta: "" });
  const [addonForm, setAddonForm] = useState({ product_id: "", name: "", price_delta: "" });

  async function load(session: string) {
    const headers = { Authorization: `Bearer ${session}` };
    const [cats, items] = await Promise.all([
      fetch(`${API_URL}/categories`, { headers }),
      fetch(`${API_URL}/products`, { headers }),
    ]);
    if (cats.status === 401 || items.status === 401) {
      localStorage.removeItem("admin-token");
      setToken(null);
      setError("Your administrator session expired.");
      return;
    }
    setCategories(await cats.json());
    setProducts(await items.json());
  }

  useEffect(() => {
    if (token) {
      // Loading remote data is the synchronization this effect performs.
      // eslint-disable-next-line react-hooks/set-state-in-effect
      void load(token);
    }
  }, [token]);

  async function createCategory(event: FormEvent) {
    event.preventDefault();
    if (!token) return;
    const response = await fetch(`${API_URL}/admin/categories`, {
      method: "POST",
      headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json" },
      body: JSON.stringify({ name: category }),
    });
    if (!response.ok) {
      setError("Category could not be saved.");
      return;
    }
    setCategory("");
    void load(token);
  }

  async function createProduct(event: FormEvent) {
    event.preventDefault();
    if (!token) return;
    const response = await fetch(`${API_URL}/admin/products`, {
      method: "POST",
      headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json" },
      body: JSON.stringify({
        ...product,
        price: Number(product.price),
        original_price: product.original_price ? Number(product.original_price) : null,
        category_id: Number(product.category_id),
      }),
    });
    if (!response.ok) {
      setError("Product could not be saved. Check the fields.");
      return;
    }
    setProduct(EMPTY_PRODUCT);
    void load(token);
  }

  async function saveOption(path: string, method: "POST" | "PATCH", body: object) {
    if (!token) return false;
    const response = await fetch(`${API_URL}${path}`, {
      method,
      headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    if (!response.ok) {
      setError("Option could not be saved. Check its name and price.");
      return false;
    }
    setError("");
    await load(token);
    return true;
  }

  async function createGroup(event: FormEvent) {
    event.preventDefault();
    const saved = await saveOption(
      `/admin/products/${groupForm.product_id}/variant-groups`,
      "POST",
      { name: groupForm.name, required: groupForm.required },
    );
    if (saved) setGroupForm({ product_id: "", name: "", required: true });
  }

  async function createVariant(event: FormEvent) {
    event.preventDefault();
    const saved = await saveOption(
      `/admin/variant-groups/${variantForm.group_id}/variants`,
      "POST",
      { name: variantForm.name, price_delta: Number(variantForm.price_delta || 0) },
    );
    if (saved) setVariantForm({ group_id: "", name: "", price_delta: "" });
  }

  async function createAddon(event: FormEvent) {
    event.preventDefault();
    const saved = await saveOption(
      `/admin/products/${addonForm.product_id}/addons`,
      "POST",
      { name: addonForm.name, price_delta: Number(addonForm.price_delta || 0) },
    );
    if (saved) setAddonForm({ product_id: "", name: "", price_delta: "" });
  }

  if (!token) {
    return (
      <main className="mx-auto max-w-md px-6 py-20">
        <h1 className="mb-4 text-3xl font-black">Menu management</h1>
        <p className="mb-4 text-slate-600">Sign in through the staff dashboard first.</p>
        <a className="font-bold text-orange-600 underline" href="/admin/orders">
          Open staff sign in
        </a>
      </main>
    );
  }

  return (
    <main className="mx-auto max-w-6xl px-6 py-10">
      <header className="mb-8 flex items-center justify-between">
        <div>
          <p className="text-sm font-semibold uppercase tracking-[0.2em] text-orange-600">Sushi Poços</p>
          <h1 className="text-4xl font-black">Menu management</h1>
        </div>
        <button
          onClick={() => {
            localStorage.removeItem("admin-token");
            setToken(null);
          }}
          className="rounded-xl border px-4 py-2 font-bold"
        >
          Sign out
        </button>
      </header>
      {error && (
        <p role="alert" className="mb-4 rounded-xl bg-red-50 p-3 text-red-700">
          {error}
        </p>
      )}
      <section className="grid gap-5 md:grid-cols-2">
        <form onSubmit={createCategory} className="space-y-3 rounded-2xl bg-white p-5 shadow-sm">
          <h2 className="text-xl font-black">New category</h2>
          <input
            required
            minLength={2}
            value={category}
            onChange={(event) => setCategory(event.target.value)}
            className="w-full rounded-xl border p-3"
            placeholder="Category name"
          />
          <button className="rounded-xl bg-slate-950 px-4 py-3 font-bold text-white">Save category</button>
        </form>
        <form onSubmit={createProduct} className="space-y-3 rounded-2xl bg-white p-5 shadow-sm">
          <h2 className="text-xl font-black">New product</h2>
          <input
            required
            minLength={2}
            value={product.name}
            onChange={(event) => setProduct({ ...product, name: event.target.value })}
            className="w-full rounded-xl border p-3"
            placeholder="Product name"
          />
          <textarea
            value={product.description}
            onChange={(event) => setProduct({ ...product, description: event.target.value })}
            className="w-full rounded-xl border p-3"
            placeholder="Description"
          />
          <input
            required
            type="number"
            step="0.01"
            min="0"
            value={product.price}
            onChange={(event) => setProduct({ ...product, price: event.target.value })}
            className="w-full rounded-xl border p-3"
            placeholder="Current price"
          />
          <input
            type="number"
            step="0.01"
            min="0"
            value={product.original_price}
            onChange={(event) => setProduct({ ...product, original_price: event.target.value })}
            className="w-full rounded-xl border p-3"
            placeholder="Original price (optional)"
          />
          <select
            required
            value={product.category_id}
            onChange={(event) => setProduct({ ...product, category_id: event.target.value })}
            className="w-full rounded-xl border p-3"
          >
            <option value="">Choose category</option>
            {categories.map((item) => (
              <option key={item.id} value={item.id}>
                {item.name}
              </option>
            ))}
          </select>
          <button className="rounded-xl bg-slate-950 px-4 py-3 font-bold text-white">Save product</button>
        </form>
      </section>
      <section className="mt-8 rounded-2xl bg-white p-5 shadow-sm">
        <h2 className="mb-2 text-xl font-black">Product options</h2>
        <p className="mb-5 text-sm text-slate-600">
          Variants are single choices such as flavor or size. Add-ons are optional paid extras.
        </p>
        <div className="grid gap-5 lg:grid-cols-3">
          <form onSubmit={createGroup} className="space-y-3 rounded-xl border p-4">
            <h3 className="font-black">New variant group</h3>
            <select required value={groupForm.product_id} onChange={(event) => setGroupForm({ ...groupForm, product_id: event.target.value })} className="w-full rounded-xl border p-3">
              <option value="">Choose product</option>
              {products.map((item) => <option key={item.id} value={item.id}>{item.name}</option>)}
            </select>
            <input required minLength={2} value={groupForm.name} onChange={(event) => setGroupForm({ ...groupForm, name: event.target.value })} className="w-full rounded-xl border p-3" placeholder="Group name, e.g. Flavor" />
            <label className="flex items-center gap-2 text-sm"><input type="checkbox" checked={groupForm.required} onChange={(event) => setGroupForm({ ...groupForm, required: event.target.checked })} /> Required choice</label>
            <button className="rounded-xl bg-slate-950 px-4 py-3 font-bold text-white">Save group</button>
          </form>
          <form onSubmit={createVariant} className="space-y-3 rounded-xl border p-4">
            <h3 className="font-black">New variant</h3>
            <select required value={variantForm.group_id} onChange={(event) => setVariantForm({ ...variantForm, group_id: event.target.value })} className="w-full rounded-xl border p-3">
              <option value="">Choose group</option>
              {products.flatMap((item) => item.variant_groups.map((group) => <option key={group.id} value={group.id}>{item.name} — {group.name}</option>))}
            </select>
            <input required minLength={2} value={variantForm.name} onChange={(event) => setVariantForm({ ...variantForm, name: event.target.value })} className="w-full rounded-xl border p-3" placeholder="Variant name" />
            <input type="number" step="0.01" min="0" value={variantForm.price_delta} onChange={(event) => setVariantForm({ ...variantForm, price_delta: event.target.value })} className="w-full rounded-xl border p-3" placeholder="Additional price" />
            <button className="rounded-xl bg-slate-950 px-4 py-3 font-bold text-white">Save variant</button>
          </form>
          <form onSubmit={createAddon} className="space-y-3 rounded-xl border p-4">
            <h3 className="font-black">New add-on</h3>
            <select required value={addonForm.product_id} onChange={(event) => setAddonForm({ ...addonForm, product_id: event.target.value })} className="w-full rounded-xl border p-3">
              <option value="">Choose product</option>
              {products.map((item) => <option key={item.id} value={item.id}>{item.name}</option>)}
            </select>
            <input required minLength={2} value={addonForm.name} onChange={(event) => setAddonForm({ ...addonForm, name: event.target.value })} className="w-full rounded-xl border p-3" placeholder="Add-on name" />
            <input type="number" step="0.01" min="0" value={addonForm.price_delta} onChange={(event) => setAddonForm({ ...addonForm, price_delta: event.target.value })} className="w-full rounded-xl border p-3" placeholder="Additional price" />
            <button className="rounded-xl bg-slate-950 px-4 py-3 font-bold text-white">Save add-on</button>
          </form>
        </div>
      </section>
      <section className="mt-8 rounded-2xl bg-white p-5 shadow-sm">
        <h2 className="mb-4 text-xl font-black">Published products</h2>
        <div className="grid gap-3 md:grid-cols-3">
          {products.map((item) => (
            <article key={item.id} className="rounded-xl border p-4">
              <strong>{item.name}</strong>
              <p className="text-sm text-slate-500">{item.category.name}</p>
              <div className="mt-2 flex items-center gap-2">
                {item.original_price && <del className="text-sm text-slate-400">R$ {item.original_price}</del>}
                <strong>R$ {item.price}</strong>
                {item.discount_percent && (
                  <span className="rounded-full bg-emerald-100 px-2 py-1 text-xs font-bold text-emerald-700">
                    {item.discount_percent}% OFF
                  </span>
                )}
              </div>
              <p className="text-sm text-slate-600">{item.description}</p>
              {item.variant_groups.map((group) => (
                <div className="mt-3 border-t pt-2 text-xs" key={group.id}>
                  <button type="button" className="font-bold underline" onClick={() => void saveOption(`/admin/variant-groups/${group.id}`, "PATCH", { active: !group.active })}>
                    {group.name} · {group.active ? "deactivate" : "activate"}
                  </button>
                  {group.variants.map((variant) => (
                    <button type="button" className="ml-2 underline" key={variant.id} onClick={() => void saveOption(`/admin/variants/${variant.id}`, "PATCH", { active: !variant.active })}>
                      {variant.name} ({variant.active ? "on" : "off"})
                    </button>
                  ))}
                </div>
              ))}
              {item.addons.map((addon) => (
                <button type="button" className="mr-2 mt-2 text-xs underline" key={addon.id} onClick={() => void saveOption(`/admin/addons/${addon.id}`, "PATCH", { active: !addon.active })}>
                  + {addon.name} ({addon.active ? "on" : "off"})
                </button>
              ))}
            </article>
          ))}
        </div>
      </section>
    </main>
  );
}
