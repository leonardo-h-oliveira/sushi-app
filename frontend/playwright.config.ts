import { defineConfig, devices } from "@playwright/test";
import { mkdtempSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";

// Each invocation gets a fresh isolated database, including local reruns.
const databasePath = process.env.SUSHI_E2E_DATABASE_PATH ?? join(mkdtempSync(join(tmpdir(), "sushi-e2e-")), "orders.db");
process.env.SUSHI_E2E_DATABASE_PATH = databasePath;

const apiUrl = "http://127.0.0.1:8000";

export default defineConfig({
  testDir: "./e2e",
  testMatch: "**/*.e2e.ts",
  fullyParallel: false,
  workers: 1,
  retries: process.env.CI ? 1 : 0,
  reporter: process.env.CI ? [["github"], ["html", { open: "never" }]] : "list",
  use: {
    baseURL: "http://127.0.0.1:3000",
    screenshot: "only-on-failure",
    trace: "retain-on-failure",
  },
  projects: [{ name: "chromium", use: { ...devices["Desktop Chrome"] } }],
  webServer: [
    {
      command: "python -m alembic -c ../backend/alembic.ini upgrade head && python ../backend/seed.py && python -m uvicorn app.main:app --app-dir ../backend --host 127.0.0.1 --port 8000",
      url: `${apiUrl}/health`,
      reuseExistingServer: false,
      timeout: 120_000,
      env: {
        DATABASE_URL: `sqlite:///${databasePath.replaceAll("\\", "/")}`,
        ENVIRONMENT: "test",
        ADMIN_USERNAME: "e2e-admin",
        ADMIN_PASSWORD: "e2e-password",
        AUTH_SECRET: "e2e-auth-secret-with-sufficient-length",
        CORS_ORIGINS: "http://127.0.0.1:3000",
      },
    },
    {
      command: "pnpm dev --hostname 127.0.0.1",
      url: "http://127.0.0.1:3000",
      reuseExistingServer: false,
      timeout: 120_000,
      env: { API_URL: apiUrl, NEXT_PUBLIC_API_URL: apiUrl },
    },
  ],
});
