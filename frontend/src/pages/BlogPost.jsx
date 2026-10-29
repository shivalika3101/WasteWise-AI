import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";

import Footer from "../components/Footer";
import Navbar from "../components/Navbar";
import { fetchBlogPost } from "../services/api";

function BlogPost() {
  const { slug } = useParams();
  const [post, setPost] = useState(null);
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;

    async function loadPost() {
      setIsLoading(true);
      setError("");
      try {
        const nextPost = await fetchBlogPost(slug);
        if (typeof nextPost?.body !== "string" || typeof nextPost?.title !== "string") {
          throw new Error("This article could not be loaded. Please try again later.");
        }
        if (!cancelled) {
          setPost(nextPost);
        }
      } catch (loadError) {
        if (!cancelled) {
          setPost(null);
          setError(loadError.status === 404 ? "This learning post could not be found." : loadError.message);
        }
      } finally {
        if (!cancelled) {
          setIsLoading(false);
        }
      }
    }

    loadPost();
    return () => {
      cancelled = true;
    };
  }, [slug]);

  return (
    <div className="page-shell">
      <Navbar />
      <main className="content-layout article-layout">
        <Link to="/learn" className="back-btn">Back to Learn</Link>
        {isLoading ? <p className="page-message">Loading article…</p> : null}
        {error ? <p className="form-message error" role="alert">{error}</p> : null}
        {post ? (
          <article className="card-surface article-card">
            <p className="eyebrow">Learn</p>
            <h1>{post.title}</h1>
            <p className="article-summary">{post.summary}</p>
            <div className="article-body">
              {post.body.split("\n\n").map((paragraph) => <p key={paragraph}>{paragraph}</p>)}
            </div>
          </article>
        ) : null}
      </main>
      <Footer />
    </div>
  );
}

export default BlogPost;
