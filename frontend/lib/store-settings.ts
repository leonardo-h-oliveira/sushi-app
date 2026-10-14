const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000";

export type StoreSettings = {
  is_open: boolean;
  delivery_enabled: boolean;
  pickup_enabled: boolean;
  pix_enabled: boolean;
  card_on_delivery_enabled: boolean;
  cash_enabled: boolean;
  delivery_fee: string;
  minimum_order: string;
};

export const DEFAULT_STORE_SETTINGS: StoreSettings = {
  is_open: true,
  delivery_enabled: true,
  pickup_enabled: true,
  pix_enabled: true,
  card_on_delivery_enabled: true,
  cash_enabled: true,
  delivery_fee: "5.00",
  minimum_order: "0.00",
};

export async function fetchStoreSettings(): Promise<StoreSettings> {
  const response = await fetch(`${API_URL}/store-settings`);
  if (!response.ok) throw new Error("Não foi possível carregar as configurações da loja.");
  return { ...DEFAULT_STORE_SETTINGS, ...(await response.json()) };
}
