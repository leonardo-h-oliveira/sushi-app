import { expect, test } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";

for (const width of [320, 390]) {
  test(`customer flow stays usable at ${width}px and the product dialog supports keyboard navigation`, async ({ page }) => {
    await page.setViewportSize({ width, height: 844 });
    await page.goto("/");
    const open = page.getByRole("button", { name: "Configurar Poke de salmão", exact: true });
    await open.focus();
    await page.keyboard.press("Enter");
    await expect(page.getByRole("button", { name: "Fechar detalhes" })).toBeFocused();
    await page.keyboard.press("Shift+Tab");
    await expect(page.getByRole("button", { name: /Adicionar/ })).toBeFocused();
    await page.keyboard.press("Tab");
    await expect(page.getByRole("button", { name: "Fechar detalhes" })).toBeFocused();
    await page.keyboard.press("Escape");
    await expect(page.getByRole("dialog")).toHaveCount(0);
    await expect(open).toBeFocused();
    await open.click();
    await page.getByRole("button", { name: /Adicionar/ }).click();
    await page.keyboard.press("Escape");

    for (const path of ["/", "/cart", "/checkout", "/admin/orders"]) {
      await page.goto(path);
      if (path === "/checkout") await expect(page.getByLabel("Nome completo")).toBeVisible();
      if (path === "/cart") await expect(page.getByRole("link", { name: /Continuar para checkout/ })).toBeVisible();
      const overflow = await page.evaluate(() => document.documentElement.scrollWidth > window.innerWidth + 1);
      expect(overflow, `horizontal overflow at ${path}`).toBeFalsy();
      const results = await new AxeBuilder({ page }).withTags(["wcag2a", "wcag2aa", "wcag21aa"]).analyze();
      expect(results.violations.filter((item) => item.impact === "critical" || item.impact === "serious"), JSON.stringify(results.violations)).toEqual([]);
    }
  });
}
