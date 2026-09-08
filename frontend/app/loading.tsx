export default function Loading() {
  return (
    <main className="state-page" aria-busy="true" aria-live="polite">
      <div className="loading-mark" aria-hidden="true" />
      <p className="eyebrow">Sushi Poços</p>
      <h1>Preparando o cardápio...</h1>
      <p>Um instante enquanto buscamos as opções disponíveis.</p>
    </main>
  );
}
