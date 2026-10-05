import type { Metadata, Viewport } from "next";
import { ServiceWorkerRegistration } from "@/components/service-worker-registration";
import "./globals.css";

export const metadata: Metadata = {
  title: "Sushi Poços | Cardápio",
  description: "Sushi fresco, combinações autorais e pedidos sem complicação.",
  manifest: "/manifest.webmanifest",
  icons: {
    icon: "/sushi-icon.jpg",
    apple: "/sushi-icon.jpg",
  },
};

export const viewport: Viewport = { themeColor: "#0f172a" };

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="pt-BR">
      <body><ServiceWorkerRegistration />{children}</body>
    </html>
  );
}
