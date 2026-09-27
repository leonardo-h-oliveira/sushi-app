"use client";

import { useMemo, useState } from "react";

import type { Category, Product, ProductAddon } from "@/types/menu";

const money = new Intl.NumberFormat("pt-BR", {
  style: "currency",
  currency: "BRL",
});

interface MenuScreenProps {
  categories: Category[];
  products: Product[];
}

export function MenuScreen({ categories, products }: MenuScreenProps) {
  const [selectedProduct, setSelectedProduct] = useState<Product | null>(null);
  const [quantity, setQuantity] = useState(1);
  const [selectedAddons, setSelectedAddons] = useState<number[]>([]);
  const [selectedVariants, setSelectedVariants] = useState<Record<number, number>>({});
  const [notes, setNotes] = useState("");
  const [cartNotice, setCartNotice] = useState("");
  const populatedCategories = categories.filter((category) =>
    products.some((product) => product.category.id === category.id),
  );
  const selectedAddonTotal = useMemo(
    () => selectedProduct?.addons
      .filter((addon) => selectedAddons.includes(addon.id))
      .reduce((total, addon) => total + Number(addon.price_delta), 0) ?? 0,
    [selectedAddons, selectedProduct],
  );
  const selectedVariantTotal = useMemo(
    () => selectedProduct?.variant_groups
      .flatMap((group) => group.variants)
      .filter((variant) => Object.values(selectedVariants).includes(variant.id))
      .reduce((total, variant) => total + Number(variant.price_delta), 0) ?? 0,
    [selectedProduct, selectedVariants],
  );
  const selectedTotal = selectedProduct
    ? (Number(selectedProduct.price) + selectedAddonTotal + selectedVariantTotal) * quantity
    : 0;

  function openProduct(product: Product) {
    setSelectedProduct(product);
    setQuantity(1);
    setSelectedAddons([]);
    setSelectedVariants({});
    setNotes("");
    setCartNotice("");
  }

  function toggleAddon(addon: ProductAddon) {
    setSelectedAddons((current) => current.includes(addon.id)
      ? current.filter((id) => id !== addon.id)
      : [...current, addon.id]);
  }

  function addConfiguredItem() {
    if (!selectedProduct) return;
    const activeGroups = selectedProduct.variant_groups.filter((group) => group.active);
    const missingGroup = activeGroups.find(
      (group) => group.required && !selectedVariants[group.id],
    );
    if (missingGroup) {
      setCartNotice(`Escolha uma opção de ${missingGroup.name}.`);
      return;
    }
    const selectedVariantItems = activeGroups.flatMap((group) =>
      group.variants
        .filter((variant) => variant.active && selectedVariants[group.id] === variant.id)
        .map((variant) => ({ group, variant })),
    );
    const currentCart = JSON.parse(localStorage.getItem("sushi-cart") ?? "[]") as unknown[];
    currentCart.push({
      product_id: selectedProduct.id,
      name: selectedProduct.name,
      quantity,
      addon_ids: selectedAddons,
      addon_names: selectedProduct.addons
        .filter((addon) => selectedAddons.includes(addon.id))
        .map((addon) => addon.name),
      variant_ids: selectedVariantItems.map(({ variant }) => variant.id),
      variant_names: selectedVariantItems.map(
        ({ group, variant }) => `${group.name}: ${variant.name}`,
      ),
      notes: notes.trim(),
      unit_total: (
        Number(selectedProduct.price) + selectedAddonTotal + selectedVariantTotal
      ).toFixed(2),
    });
    localStorage.setItem("sushi-cart", JSON.stringify(currentCart));
    setCartNotice("Item adicionado ao seu pedido.");
  }

  return (
    <main>
      <header className="site-header">
        <a className="brand" href="#menu" aria-label="Sushi Poços, início">
          <span className="brand-mark" aria-hidden="true">SP</span>
          <span><strong>Sushi Poços</strong><small>cozinha japonesa</small></span>
        </a>
        <nav aria-label="Navegação principal">
          <a href="#menu">Cardápio</a>
          <a href="#about">Nossa casa</a>
          <a href="/cart">Sacola</a>
        </nav>
      </header>

      <section className="hero" aria-labelledby="hero-title">
        <div className="hero-copy">
          <p className="eyebrow"><span /> Feito no momento</p>
          <h1 id="hero-title">Seu ritual japonês,<br /><em>mais perto.</em></h1>
          <p className="hero-description">
            Ingredientes frescos, combinações autorais e o cuidado de sempre — agora em poucos toques.
          </p>
          <a className="primary-button" href="#menu">Explorar o cardápio <span aria-hidden="true">↓</span></a>
        </div>
        <div className="hero-art" aria-hidden="true">
          <span className="sun" />
          <div className="plate"><span /><span /><span /></div>
          <p>Poços de Caldas<br />Minas Gerais</p>
        </div>
      </section>

      <section className="menu" id="menu" aria-labelledby="menu-title">
        <div className="section-heading">
          <div><p className="eyebrow">Escolha com calma</p><h2 id="menu-title">Nosso cardápio</h2></div>
          <p>{products.length} {products.length === 1 ? "opção disponível" : "opções disponíveis"}</p>
        </div>

        {products.length > 0 && populatedCategories.length > 0 && (
          <nav className="category-nav" aria-label="Categorias do cardápio">
            {populatedCategories.map((category, index) => (
              <a className={index === 0 ? "active" : ""} href={`#${category.slug}`} key={category.id}>
                {category.name}
              </a>
            ))}
          </nav>
        )}

        {products.length === 0 ? (
          <div className="empty-state">
            <span aria-hidden="true">○</span>
            <h3>O cardápio está sendo atualizado.</h3>
            <p>Volte em breve para descobrir as opções fresquinhas do dia.</p>
          </div>
        ) : (
          populatedCategories.map((category) => (
            <section className="category-section" id={category.slug} key={category.id} aria-labelledby={`${category.slug}-title`}>
              <div className="category-title">
                <h3 id={`${category.slug}-title`}>{category.name}</h3><span />
              </div>
              <div className="product-grid">
                {products.filter((product) => product.category.id === category.id).map((product) => (
                  <article className="product-card" key={product.id}>
                    <button className="card-open" type="button" onClick={() => openProduct(product)} aria-label={`Configurar ${product.name}`}>
                    <div className="product-image">
                      {product.image_url ? (
                        <div
                          className="remote-product-image"
                          role="img"
                          aria-label={`Imagem de ${product.name}`}
                          style={{ backgroundImage: `url(${product.image_url})` }}
                        />
                      ) : <span aria-hidden="true">寿司</span>}
                    </div>
                    <div className="product-copy">
                      <h4>{product.name}</h4>
                      <p>{product.description || "Preparado com ingredientes selecionados."}</p>
                      <div className="product-price">
                        {product.original_price && (
                          <span>{money.format(Number(product.original_price))}</span>
                        )}
                        <strong>{money.format(Number(product.price))}</strong>
                        {product.discount_percent && (
                          <em>{product.discount_percent}% OFF</em>
                        )}
                      </div>
                    </div>
                      <span className="card-arrow" aria-hidden="true">→</span>
                    </button>
                  </article>
                ))}
              </div>
            </section>
          ))
        )}
      </section>

      {selectedProduct && (
        <div className="detail-backdrop" role="presentation" onMouseDown={(event) => {
          if (event.target === event.currentTarget) setSelectedProduct(null);
        }}>
          <section className="product-detail" role="dialog" aria-modal="true" aria-labelledby="detail-title">
            <button className="detail-close" type="button" onClick={() => setSelectedProduct(null)} aria-label="Fechar detalhes">×</button>
            <p className="eyebrow">{selectedProduct.category.name}</p>
            <h2 id="detail-title">{selectedProduct.name}</h2>
            <p className="detail-description">{selectedProduct.description || "Preparado com ingredientes selecionados."}</p>
            <div className="detail-price">
              {selectedProduct.original_price && (
                <del>{money.format(Number(selectedProduct.original_price))}</del>
              )}
              <strong>{money.format(Number(selectedProduct.price))}</strong>
              {selectedProduct.discount_percent && (
                <span>{selectedProduct.discount_percent}% OFF</span>
              )}
            </div>

            {selectedProduct.addons.length > 0 && (
              <fieldset className="addons-fieldset">
                <legend>Quer deixar do seu jeito?</legend>
                {selectedProduct.addons.filter((addon) => addon.active).map((addon) => (
                  <label className="addon-option" key={addon.id}>
                    <input
                      type="checkbox"
                      checked={selectedAddons.includes(addon.id)}
                      onChange={() => toggleAddon(addon)}
                    />
                    <span>{addon.name}</span>
                    <strong>+ {money.format(Number(addon.price_delta))}</strong>
                  </label>
                ))}
              </fieldset>
            )}

            {selectedProduct.variant_groups
              .filter((group) => group.active && group.variants.some((variant) => variant.active))
              .map((group) => (
                <fieldset className="addons-fieldset" key={group.id}>
                  <legend>
                    {group.name}{group.required ? " *" : " (opcional)"}
                  </legend>
                  {group.variants.filter((variant) => variant.active).map((variant) => (
                    <label className="addon-option" key={variant.id}>
                      <input
                        type="radio"
                        name={`variant-group-${group.id}`}
                        required={group.required}
                        checked={selectedVariants[group.id] === variant.id}
                        onChange={() => {
                          setSelectedVariants((current) => ({
                            ...current,
                            [group.id]: variant.id,
                          }));
                          setCartNotice("");
                        }}
                      />
                      <span>{variant.name}</span>
                      <strong>
                        {Number(variant.price_delta) > 0
                          ? `+ ${money.format(Number(variant.price_delta))}`
                          : "Incluso"}
                      </strong>
                    </label>
                  ))}
                </fieldset>
              ))}

            <label className="notes-field">Observações (opcional)
              <textarea value={notes} maxLength={180} onChange={(event) => setNotes(event.target.value)} placeholder="Ex.: pouco shoyu, sem cebolinha..." />
            </label>
            <div className="detail-actions">
              <div className="quantity-control" aria-label="Quantidade">
                <button type="button" onClick={() => setQuantity((current) => Math.max(1, current - 1))} aria-label="Diminuir quantidade">−</button>
                <output>{quantity}</output>
                <button type="button" onClick={() => setQuantity((current) => current + 1)} aria-label="Aumentar quantidade">+</button>
              </div>
              <button className="primary-button add-button" type="button" onClick={addConfiguredItem}>
                Adicionar · {money.format(selectedTotal)}
              </button>
            </div>
            {cartNotice && <p className="cart-notice" role="status">{cartNotice} <a href="/cart">Ver sua sacola →</a></p>}
          </section>
        </div>
      )}

      <footer id="about">
        <p className="brand-footer">Sushi Poços</p>
        <p>Comida japonesa feita com atenção aos detalhes.</p>
        <a href="#menu">Voltar ao cardápio ↑</a>
      </footer>
    </main>
  );
}
