import { useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";

import Navbar from "../components/Navbar";
import { useAuth } from "../context/useAuth";

function Login() {
  const navigate = useNavigate();
  const location = useLocation();
  const { signIn } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  const nextPath = location.state?.from?.pathname ?? "/profile";

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");
    setIsSubmitting(true);

    try {
      await signIn(email, password);
      navigate(nextPath, { replace: true });
    } catch (submissionError) {
      setError(submissionError.message);
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <div className="page-shell">
      <Navbar />
      <main className="auth-layout">
        <section className="auth-panel auth-aside">
          <span className="badge">Authenticated prototype</span>
          <h1>Sign in to classify waste and save your prediction.</h1>
          <p>
            This milestone uses bearer-token auth, a protected profile, and an
            upload flow that sends only the image file to the API.
          </p>
          <ul className="auth-points">
            <li>Session is restored after refresh.</li>
            <li>Protected routes redirect to sign in.</li>
            <li>One image upload returns a full prediction result.</li>
          </ul>
        </section>

        <section className="auth-panel">
          <h2>Welcome back</h2>
          <p className="auth-copy">Use your project account to continue.</p>

          <form className="auth-form" onSubmit={handleSubmit}>
            <label>
              Email
              <input
                type="email"
                value={email}
                onChange={(event) => setEmail(event.target.value)}
                placeholder="name@example.com"
                autoComplete="email"
                autoCapitalize="none"
                spellCheck={false}
                required
              />
            </label>

            <label>
              Password
              <input
                type="password"
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                placeholder="At least 8 characters"
                autoComplete="current-password"
                required
              />
            </label>

            {error ? <p className="form-message error">{error}</p> : null}

            <button className="primary-button" type="submit" disabled={isSubmitting}>
              {isSubmitting ? "Signing in..." : "Sign in"}
            </button>
          </form>

          <p className="auth-switch">
            Need an account? <Link to="/register">Create one here</Link>.
          </p>
        </section>
      </main>
    </div>
  );
}

export default Login;
