import type { CartItem } from "@/types/cart";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? process.env.API_URL ?? "http://127.0.0.1:8000";

export interface OrderResult {
  number: string;
  tracking_token: string;
  status: string;
  fulfillment_method: "delivery" | "pickup";
  payment_method: "pix" | "card_on_delivery" | "cash";
  subtotal: string;
  delivery_fee: string;
  total: string;
  items: Array<{
    product_name: string;
    quantity: number;
    unit_price: string;
    total: string;
  }>;
}

export class OrderRequestError extends Error {
  constructor(message: string, public status: number, public quote?: { subtotal: string; delivery_fee: string; total: string }) {
    super(message);
  }
}

export async function createOrder(payload: Record<string, unknown>): Promise<OrderResult> {
  const response = await fetch(`${API_URL}/orders`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    const detail = body.detail;
    const messages: Record<string, string> = {
      "The store is currently closed.": "O estabelecimento está fechado para novos pedidos.",
      "Delivery is currently unavailable.": "A entrega está indisponível. Revise a modalidade de recebimento.",
      "Pickup is currently unavailable.": "A retirada está indisponível. Revise a modalidade de recebimento.",
      "The selected payment method is unavailable.": "A forma de pagamento foi desativada. Escolha outra opção.",
      "One of the selected products is unavailable.": "Um produto ficou indisponível. Revise sua sacola.",
      "This address is outside the delivery area.": "O endereço está fora da área de entrega. Confira os bairros atendidos ou escolha retirada.",
    };
    throw new OrderRequestError(
      detail?.code === "price_changed" ? `${detail.message} Se o preço dos produtos mudou, refaça os itens pelo cardápio.` : messages[detail] ?? "Não foi possível criar o pedido. Revise os dados e as regras da loja.",
      response.status,
      detail?.code === "price_changed" ? detail : undefined,
    );
  }
  return response.json() as Promise<OrderResult>;
}

export function cartItemsToOrderItems(items: CartItem[]) {
  return items.map((item) => ({
    product_id: item.product_id,
    quantity: item.quantity,
    addon_ids: item.addon_ids,
    variant_ids: item.variant_ids ?? [],
    notes: item.notes || null,
  }));
}
