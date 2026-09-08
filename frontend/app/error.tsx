"use client";

export default function ErrorPage({ reset }: { reset: () => void }) {
  return (
    <main className="state-page" role="alert">
      <span className="state-symbol" aria-hidden="true">!</span>
      <p className="eyebrow">Algo saiu do ritmo</p>
      <h1>Não foi possível carregar o cardápio.</h1>
      <p>Confira sua conexão e tente novamente em alguns instantes.</p>
      <button className="primary-button" onClick={reset}>Tentar novamente</button>
    </main>
  );
}
