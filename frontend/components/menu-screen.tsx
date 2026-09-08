import type { Category, Product } from "@/types/menu";

const money = new Intl.NumberFormat("pt-BR", {
  style: "currency",
  currency: "BRL",
});

interface MenuScreenProps {
  categories: Category[];
  products: Product[];
}

export function MenuScreen({ categories, products }: MenuScreenProps) {
  const populatedCategories = categories.filter((category) =>
    products.some((product) => product.category.id === category.id),
  );

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
                      <strong>{money.format(Number(product.price))}</strong>
                    </div>
                    <span className="card-arrow" aria-hidden="true">→</span>
                  </article>
                ))}
              </div>
            </section>
          ))
        )}
      </section>

      <footer id="about">
        <p className="brand-footer">Sushi Poços</p>
        <p>Comida japonesa feita com atenção aos detalhes.</p>
        <a href="#menu">Voltar ao cardápio ↑</a>
      </footer>
    </main>
  );
}
