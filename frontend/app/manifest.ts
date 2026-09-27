import type { MetadataRoute } from "next";

export default function manifest(): MetadataRoute.Manifest {
  return {
    name: "Sushi Poços",
    short_name: "Sushi Poços",
    description: "Cardápio e pedidos do Sushi Poços.",
    start_url: "/",
    display: "standalone",
    background_color: "#fffaf5",
    theme_color: "#0f172a",
    lang: "pt-BR",
    icons: [
      { src: "/sushi-icon.svg", sizes: "any", type: "image/svg+xml", purpose: "any" },
    ],
  };
}
