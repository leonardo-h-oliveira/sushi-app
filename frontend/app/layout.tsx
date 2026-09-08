import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Sushi Poços | Cardápio",
  description: "Sushi fresco, combinações autorais e pedidos sem complicação.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="pt-BR">
      <body>{children}</body>
    </html>
  );
}
