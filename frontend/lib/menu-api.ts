import type { Category, Product } from "@/types/menu";

const API_URL = process.env.API_URL ?? "http://127.0.0.1:8000";

async function request<T>(path: string): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, { cache: "no-store" });
  if (!response.ok) {
    throw new Error(`Menu API request failed with status ${response.status}.`);
  }
  return response.json() as Promise<T>;
}

export async function getMenu(): Promise<{
  categories: Category[];
  products: Product[];
}> {
  const [categories, products] = await Promise.all([
    request<Category[]>("/categories"),
    request<Product[]>("/products"),
  ]);
  return { categories, products };
}
