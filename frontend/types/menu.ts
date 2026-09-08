export interface Category {
  id: number;
  name: string;
  slug: string;
  active: boolean;
}

export interface Product {
  id: number;
  name: string;
  description: string;
  price: string;
  image_url: string | null;
  active: boolean;
  category: Pick<Category, "id" | "name" | "slug">;
  addons: ProductAddon[];
}

export interface ProductAddon {
  id: number;
  name: string;
  price_delta: string;
  active: boolean;
}
