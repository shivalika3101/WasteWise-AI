import { screen } from "@testing-library/react";
import { readFileSync } from "node:fs";

import { beforeEach, describe, expect, it, vi } from "vitest";

import About from "../pages/About";
import HowTo from "../pages/HowTo";
import { expectNoSeriousA11yViolations, renderWithProviders } from "./helpers";

vi.mock("../services/api", () => ({
  fetchCurrentUser: vi.fn(),
  loginUser: vi.fn(),
  logoutUser: vi.fn(),
  registerUser: vi.fn(),
}));

const api = await import("../services/api");

beforeEach(() => {
  api.fetchCurrentUser.mockResolvedValue(null);
});

const PAGES = [
  ["How-to", HowTo, "/how-to"],
  ["About", About, "/about"],
];

describe.each(PAGES)("%s page", (name, Page, route) => {
  it("has exactly one level-one heading", async () => {
    renderWithProviders(<Page />, { route });
    await screen.findAllByRole("heading");
    expect(screen.getAllByRole("heading", { level: 1 })).toHaveLength(1);
  });

  it("does not skip a heading level", async () => {
    renderWithProviders(<Page />, { route });
    const headings = await screen.findAllByRole("heading");
    const levels = headings.map((heading) => Number(heading.tagName[1]));

    levels.reduce((deepest, level) => {
      expect(level).toBeLessThanOrEqual(deepest + 1);
      return Math.max(deepest, level);
    }, 0);
  });

  it("has no serious accessibility violations", async () => {
    const { container } = renderWithProviders(<Page />, { route });
    await screen.findAllByRole("heading");
    await expectNoSeriousA11yViolations(container);
  });
});

describe("reduced motion", () => {
  it("the stylesheet honours prefers-reduced-motion", () => {
    // Resolved from the vitest root (the frontend folder) rather than from
    // import.meta.url, which is not a file:// URL under the test runner.
    const stylesheet = readFileSync("src/index.css", "utf8");
    expect(stylesheet).toMatch(/@media\s*\(prefers-reduced-motion:\s*reduce\)/);
  });
});
