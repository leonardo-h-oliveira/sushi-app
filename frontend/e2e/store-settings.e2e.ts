import { expect, test } from "@playwright/test";

test("staff can configure operational rules and the server enforces delivery area", async ({ page }) => {
  const api = "http://127.0.0.1:8000";
  expect((await page.request.post(`${api}/auth/login`, { data: { username: "e2e-admin", password: "e2e-password" } })).ok()).toBeTruthy();
  const original = await (await page.request.get(`${api}/admin/store-settings`)).json();
  try {
    await page.goto("/admin/settings");
    await expect(page.getByLabel("Bairros atendidos")).toBeEnabled();
    await page.getByLabel("Bairros atendidos").fill("Centro\nSão José");
    await page.getByLabel("Como pagar por PIX").fill("Solicite a chave à equipe antes de pagar.");
    await page.getByRole("button", { name: "Salvar configurações" }).click();
    await expect(page.getByRole("status")).toContainText("Configurações salvas");
    await page.reload();
    await expect(page.getByLabel("Bairros atendidos")).toHaveValue("Centro\nSão José");
    const products = await (await page.request.get(`${api}/products`)).json();
    const product = products.find((item: { name: string }) => item.name === "Poke de salmão");
    const response = await page.request.post(`${api}/orders`, { data: {
      customer_name: "Teste de área", phone: "35999990002", fulfillment_method: "delivery", payment_method: "pix",
      expected_total: (Number(product.price) + Number(original.delivery_fee)).toFixed(2),
      address: { street: "Rua de Teste", number: "123", neighborhood: "Fora da área" },
      items: [{ product_id: product.id, quantity: 1 }],
    } });
    expect(response.status()).toBe(422);
    expect((await response.json()).detail).toBe("This address is outside the delivery area.");
  } finally {
    const restored = await page.request.patch(`${api}/admin/store-settings`, { data: Object.fromEntries(Object.entries(original).filter(([key]) => key !== "next_opening")) });
    expect(restored.ok()).toBeTruthy();
  }
});
