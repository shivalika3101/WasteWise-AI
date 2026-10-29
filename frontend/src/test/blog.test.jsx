import { screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import Blog from "../pages/Blog";
import BlogPost from "../pages/BlogPost";
import { renderWithProviders } from "./helpers";

vi.mock("../services/api", () => ({
  fetchBlogPosts: vi.fn(),
  fetchBlogPost: vi.fn(),
  fetchCurrentUser: vi.fn(),
  loginUser: vi.fn(),
  logoutUser: vi.fn(),
  registerUser: vi.fn(),
}));

const api = await import("../services/api");

const POSTS = [
  {
    slug: "contamination-prevention",
    title: "Stopping contamination before it starts",
    summary: "Why one greasy pizza box can spoil a batch.",
    created_at: "2026-07-20T10:00:00",
  },
];

beforeEach(() => {
  api.fetchCurrentUser.mockResolvedValue(null);
});

describe("Learn index", () => {
  it("shows a loading state before the API responds", () => {
    api.fetchBlogPosts.mockReturnValue(new Promise(() => {}));
    renderWithProviders(<Blog />, { route: "/learn" });
    expect(screen.getByText(/loading learning posts/i)).toBeInTheDocument();
  });

  it("lists published posts and links to each detail page", async () => {
    api.fetchBlogPosts.mockResolvedValue(POSTS);
    renderWithProviders(<Blog />, { route: "/learn" });

    const heading = await screen.findByRole("heading", { name: POSTS[0].title });
    expect(heading).toBeInTheDocument();

    const link = screen.getByRole("link", { name: /read article/i });
    expect(link).toHaveAttribute("href", "/learn/contamination-prevention");
  });

  it("shows an empty state rather than a blank page when there are no posts", async () => {
    api.fetchBlogPosts.mockResolvedValue([]);
    renderWithProviders(<Blog />, { route: "/learn" });
    expect(await screen.findByText(/no learning posts are available/i)).toBeInTheDocument();
  });

  it("surfaces an error when the API is unreachable", async () => {
    api.fetchBlogPosts.mockRejectedValue(new Error("Cannot reach the WasteWise API."));
    renderWithProviders(<Blog />, { route: "/learn" });

    const alert = await screen.findByRole("alert");
    expect(alert).toHaveTextContent(/cannot reach the wastewise api/i);
  });

  it("shows the error state instead of crashing on a non-array body", async () => {
    // Regression guard: if /blog is not proxied, nginx serves index.html with
    // a 200, the client receives an HTML string, and .map() used to throw.
    api.fetchBlogPosts.mockResolvedValue("<!doctype html><html></html>");
    renderWithProviders(<Blog />, { route: "/learn" });

    const alert = await screen.findByRole("alert");
    expect(alert).toHaveTextContent(/could not be loaded/i);
  });
});

describe("Learn article", () => {
  it("renders the article body", async () => {
    api.fetchBlogPost.mockResolvedValue({
      slug: "contamination-prevention",
      title: "Stopping contamination before it starts",
      summary: "A summary.",
      body: "First paragraph.\n\nSecond paragraph.",
      created_at: "2026-07-20T10:00:00",
    });
    renderWithProviders(<BlogPost />, { route: "/learn/contamination-prevention" });

    expect(await screen.findByText("First paragraph.")).toBeInTheDocument();
    expect(screen.getByText("Second paragraph.")).toBeInTheDocument();
  });

  it("shows a clear not-found message for an unknown slug", async () => {
    const error = new Error("Post not found");
    error.status = 404;
    api.fetchBlogPost.mockRejectedValue(error);

    renderWithProviders(<BlogPost />, { route: "/learn/not-a-real-post" });

    const alert = await screen.findByRole("alert");
    expect(alert).toHaveTextContent(/could not be found/i);
  });
});
