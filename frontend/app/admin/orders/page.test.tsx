import { render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import AdminOrdersPage from "./page";

beforeEach(() => {
  vi.stubGlobal("fetch", vi.fn().mockResolvedValue({ ok: false, status: 401 }));
});

describe("AdminOrdersPage", () => {
  it("treats an anonymous session as the normal sign-in state", async () => {
    render(<AdminOrdersPage />);

    expect(screen.getByRole("heading", { name: "Staff sign in" })).toBeInTheDocument();
    await waitFor(() => expect(fetch).toHaveBeenCalledWith(
      expect.stringContaining("/orders"),
      { credentials: "include", cache: "no-store" },
    ));
    expect(screen.queryByRole("alert")).not.toBeInTheDocument();
  });
});
