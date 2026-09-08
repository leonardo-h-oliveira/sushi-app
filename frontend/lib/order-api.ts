import type { CartItem } from "@/types/cart";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? process.env.API_URL ?? "http://127.0.0.1:8000";

export interface OrderResult {
  number: string;
  status: string;
  total: string;
}

export async function createOrder(payload: Record<string, unknown>): Promise<OrderResult> {
  const response = await fetch(`${API_URL}/orders`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!response.ok) throw new Error("Não foi possível criar o pedido.");
  return response.json() as Promise<OrderResult>;
}

export function cartItemsToOrderItems(items: CartItem[]) {
  return items.map((item) => ({
    product_id: item.product_id,
    quantity: item.quantity,
    addon_ids: item.addon_ids,
    notes: item.notes || null,
  }));
}
