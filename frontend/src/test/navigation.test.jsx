import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";

import Footer from "../components/Footer";
import Navbar from "../components/Navbar";
import { renderWithProviders } from "./helpers";

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

const PUBLIC_LINKS = [
  ["How to", "/how-to"],
  ["Learn", "/learn"],
  ["About", "/about"],
];

describe("navigation", () => {
  it.each(PUBLIC_LINKS)("navbar links %s to %s", async (name, href) => {
    renderWithProviders(<Navbar />);
    expect(await screen.findByRole("link", { name })).toHaveAttribute("href", href);
  });

  it.each(PUBLIC_LINKS)("footer links %s to %s", async (name, href) => {
    renderWithProviders(<Footer />);
    expect(await screen.findByRole("link", { name })).toHaveAttribute("href", href);
  });

  it("hides the profile link when signed out", async () => {
    renderWithProviders(<Navbar />);
    await screen.findByRole("link", { name: "Learn" });
    expect(screen.queryByRole("link", { name: /profile/i })).not.toBeInTheDocument();
  });

  it("reaches every public link by keyboard alone", async () => {
    const user = userEvent.setup();
    renderWithProviders(<Navbar />);
    await screen.findByRole("link", { name: "Learn" });

    const reached = new Set();
    for (let press = 0; press < 12; press += 1) {
      await user.tab();
      const active = document.activeElement;
      if (active?.tagName === "A") {
        reached.add(active.getAttribute("href"));
      }
    }

    for (const [, href] of PUBLIC_LINKS) {
      expect(reached).toContain(href);
    }
  });
});
