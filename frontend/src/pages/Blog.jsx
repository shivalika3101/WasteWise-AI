import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import Footer from "../components/Footer";
import Navbar from "../components/Navbar";
import { fetchBlogPosts } from "../services/api";

function Blog() {
  const [posts, setPosts] = useState([]);
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;

    async function loadPosts() {
      try {
        const nextPosts = await fetchBlogPosts();
        if (!Array.isArray(nextPosts)) {
          // The API is reachable but did not return a post list. In the Docker
          // stack an unproxied /blog request is answered by nginx with
          // index.html and a 200, so the client receives an HTML string.
          throw new Error("The learning posts could not be loaded. Please try again later.");
        }
        if (!cancelled) {
          setPosts(nextPosts);
        }
      } catch (loadError) {
        if (!cancelled) {
          setError(loadError.message);
        }
      } finally {
        if (!cancelled) {
          setIsLoading(false);
        }
      }
    }

    loadPosts();
    return () => {
      cancelled = true;
    };
  }, []);

  return (
    <div className="page-shell">
      <Navbar />
      <main className="content-layout learn-layout">
        <section className="card-surface learn-hero">
          <span className="badge">Learn with WasteWise</span>
          <h1>Small changes make waste less wasteful.</h1>
          <p>Practical, reviewed explainers to help you avoid contamination and make more confident disposal choices.</p>
        </section>

        {isLoading ? <p className="page-message">Loading learning posts…</p> : null}
        {error ? <p className="form-message error" role="alert">{error}</p> : null}
        {!isLoading && !error && posts.length === 0 ? (
          <p className="page-message">No learning posts are available yet. Please check back soon.</p>
        ) : null}
        {!isLoading && !error && posts.length > 0 ? (
          <section className="post-grid" aria-label="Learning posts">
            {posts.map((post) => (
              <article className="card-surface post-card" key={post.slug}>
                <p className="eyebrow">Learn</p>
                <h2>{post.title}</h2>
                <p>{post.summary}</p>
                <Link to={`/learn/${post.slug}`} className="text-link">
                  Read article <span aria-hidden="true">→</span>
                </Link>
              </article>
            ))}
          </section>
        ) : null}
      </main>
      <Footer />
    </div>
  );
}

export default Blog;
