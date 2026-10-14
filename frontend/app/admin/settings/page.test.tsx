import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, expect, it, vi } from "vitest";

import AdminSettingsPage from "./page";

const settings = {
  is_open: true,
  delivery_enabled: true,
  pickup_enabled: true,
  pix_enabled: true,
  card_on_delivery_enabled: true,
  cash_enabled: true,
  delivery_fee: "5.00",
  minimum_order: "0.00",
};

beforeEach(() => {
  vi.stubGlobal("fetch", vi.fn()
    .mockResolvedValueOnce({ ok: true, status: 200, json: async () => settings })
    .mockResolvedValueOnce({ ok: true, status: 200, json: async () => ({ ...settings, delivery_fee: "8.50" }) }));
});

it("loads and saves the operational settings", async () => {
  render(<AdminSettingsPage />);
  const fee = await screen.findByLabelText("Taxa de entrega");
  expect(fee).toHaveValue(5);
  fireEvent.change(fee, { target: { value: "8.50" } });
  fireEvent.click(screen.getByRole("button", { name: "Salvar configurações" }));

  await waitFor(() => expect(screen.getByRole("status")).toHaveTextContent("Configurações salvas"));
  expect(fetch).toHaveBeenLastCalledWith(expect.stringContaining("/admin/store-settings"), expect.objectContaining({ method: "PATCH" }));
});
