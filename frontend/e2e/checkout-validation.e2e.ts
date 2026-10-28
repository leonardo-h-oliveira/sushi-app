import { expect, test, type Page } from "@playwright/test";

async function addPokeToCart(page: Page) {
  await page.goto("/");
  await expect(page.getByRole("heading", { name: "Nosso cardápio" })).toBeVisible();
  await page.getByRole("button", { name: "Configurar Poke de salmão", exact: true }).click();
  await page.getByRole("button", { name: /Adicionar/ }).click();
}

test("delivery checkout requires customer and address information", async ({ page }) => {
  await addPokeToCart(page);
  await page.goto("/checkout");

  await page.getByRole("button", { name: /Confirmar pedido/ }).click();
  await expect(page.getByRole("alert").filter({ hasText: "nome e telefone" })).toBeVisible();

  await page.getByLabel("Nome completo").fill("Cliente Entrega E2E");
  await page.getByLabel("Telefone").fill("35999990001");
  await page.getByRole("button", { name: /Confirmar pedido/ }).click();
  await expect(page.getByRole("alert").filter({ hasText: "rua, número e bairro" })).toBeVisible();

  await page.getByLabel("Rua").fill("Rua de Teste");
  await page.getByLabel("Número").fill("123");
  await page.getByLabel("Bairro").fill("Centro");
  await page.getByRole("button", { name: /Confirmar pedido/ }).click();

  await expect(page.getByRole("heading", { name: "Obrigado por pedir com a gente." })).toBeVisible();
  const summary = page.getByRole("region", { name: "Resumo do pedido" });
  await expect(summary).toContainText("Entrega");
  await expect(summary).toContainText("PIX");
  await expect(summary).toContainText("R$ 60,90");
});
