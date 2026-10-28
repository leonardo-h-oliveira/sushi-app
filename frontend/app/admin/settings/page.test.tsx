import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, expect, it, vi } from "vitest";
import AdminSettingsPage from "./page";
import { DEFAULT_STORE_SETTINGS } from "@/lib/store-settings";

beforeEach(() => vi.unstubAllGlobals());

it("loads and saves operational settings", async () => {
  vi.stubGlobal("fetch", vi.fn()
    .mockResolvedValueOnce({ ok: true, json: async () => DEFAULT_STORE_SETTINGS })
    .mockResolvedValueOnce({ ok: true, json: async () => ({ ...DEFAULT_STORE_SETTINGS, delivery_fee: "8.50" }) }));
  render(<AdminSettingsPage />);
  const fee = screen.getByLabelText("Taxa de entrega");
  await waitFor(() => expect(fee).toBeEnabled());
  expect(fee).toHaveValue(5);
  fireEvent.change(fee, { target: { value: "8.50" } });
  fireEvent.click(screen.getByRole("button", { name: "Salvar configurações" }));
  await screen.findByText("Configurações salvas.");
  expect(fee).toHaveValue(8.5);
});

it("prevents editing before settings load and permits retry after a failed load", async () => {
  const fetchMock = vi.fn().mockRejectedValueOnce(new Error("offline")).mockResolvedValue({ ok: true, json: async () => DEFAULT_STORE_SETTINGS });
  vi.stubGlobal("fetch", fetchMock);
  render(<AdminSettingsPage />);
  expect(screen.getByRole("button", { name: "Salvar configurações" })).toBeDisabled();
  await screen.findByText(/Não foi possível carregar/);
  expect(screen.getByLabelText("Taxa de entrega")).toBeDisabled();
  fireEvent.click(screen.getByRole("button", { name: "Tentar novamente" }));
  await waitFor(() => expect(screen.getByLabelText("Taxa de entrega")).toBeEnabled());
});

it("sends only changed fields and recovers from a rejected PATCH", async () => {
  const fetchMock = vi.fn().mockResolvedValueOnce({ ok: true, json: async () => ({ ...DEFAULT_STORE_SETTINGS, is_open: false }) }).mockRejectedValueOnce(new Error("offline"));
  vi.stubGlobal("fetch", fetchMock);
  render(<AdminSettingsPage />);
  await waitFor(() => expect(screen.getByLabelText("Taxa de entrega")).toBeEnabled());
  fireEvent.change(screen.getByLabelText("Taxa de entrega"), { target: { value: "8.50" } });
  fireEvent.click(screen.getByRole("button", { name: "Salvar configurações" }));
  await screen.findByText(/Confira sua conexão/);
  expect(JSON.parse(fetchMock.mock.calls[1][1].body)).toEqual({ delivery_fee: "8.50" });
  expect(screen.getByRole("button", { name: "Salvar configurações" })).toBeEnabled();
  expect(screen.getByLabelText("Aberto para novos pedidos")).not.toBeChecked();
});
