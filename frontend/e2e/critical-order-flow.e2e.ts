import { expect, test } from "@playwright/test";

test("customer order moves through staff workflow and tracking", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByRole("heading", { name: "Nosso cardápio" })).toBeVisible();

  await page.getByRole("button", { name: "Configurar Poke de salmão", exact: true }).click();
  await page.getByLabel("Observações (opcional)").fill("Pedido automatizado de teste");
  await page.getByRole("button", { name: /Adicionar/ }).click();
  await page.goto("/cart");

  await page.getByRole("radio", { name: /Retirada/ }).check();
  await expect(page.getByText("R$ 55,90", { exact: true }).last()).toBeVisible();
  await page.getByRole("link", { name: /Continuar para checkout/ }).click();

  await expect(page.getByRole("radio", { name: /Retirada/ })).toBeChecked();
  await expect(page.getByRole("group", { name: "Endereço de entrega" })).toHaveCount(0);
  await page.getByLabel("Nome completo").fill("Cliente E2E");
  await page.getByLabel("Telefone").fill("35999990000");
  await page.getByRole("radio", { name: /Cartão na entrega/ }).check();
  await page.getByRole("button", { name: /Confirmar pedido/ }).click();

  await expect(page.getByRole("heading", { name: "Obrigado por pedir com a gente." })).toBeVisible();
  const trackingHref = await page.getByRole("link", { name: /Acompanhar pedido/ }).getAttribute("href");
  expect(trackingHref).toMatch(/^\/orders\/[A-Za-z0-9_-]{32}$/);
  const orderNumber = (await page.getByText(/Seu número é/).locator("strong").innerText()).trim();

  await page.goto("/admin/orders");
  await page.getByLabel("Username").fill("e2e-admin");
  await page.getByLabel("Password").fill("e2e-password");
  await page.getByRole("button", { name: "Sign in" }).click();

  const orderCard = page.locator("article").filter({ hasText: orderNumber });
  await expect(orderCard).toContainText("Cliente E2E");
  await orderCard.getByLabel(`Status do pedido ${orderNumber}`).selectOption("preparing");

  await page.goto(trackingHref!);
  await expect(page.getByRole("heading", { name: "Em preparo" })).toBeVisible();
  await expect(page.getByRole("region", { name: "Detalhes do pedido" })).toContainText("Retirada");
  await expect(page.getByRole("region", { name: "Detalhes do pedido" })).toContainText("Cartão na entrega");
});
