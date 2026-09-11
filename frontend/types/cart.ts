export interface CartItem {
  product_id: number;
  name: string;
  quantity: number;
  addon_ids: number[];
  addon_names: string[];
  variant_ids: number[];
  variant_names: string[];
  notes: string;
  unit_total: string;
}
