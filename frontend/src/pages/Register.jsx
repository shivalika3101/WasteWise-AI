import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import Navbar from "../components/Navbar";
import { useAuth } from "../context/useAuth";

function Register() {
  const navigate = useNavigate();
  const { signUp } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleSubmit(event) {
    event.preventDefault();

    if (password !== confirmPassword) {
      setError("Passwords do not match.");
      return;
    }

    setError("");
    setIsSubmitting(true);

    try {
      await signUp(email, password);
      navigate("/profile", { replace: true });
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
          <span className="badge">Create your account</span>
          <h1>Register once, then upload and classify with protected access.</h1>
          <p>
            After registration we immediately sign you in and restore the
            session on later visits until you sign out or the token expires.
          </p>
        </section>

        <section className="auth-panel">
          <h2>Get started</h2>
          <p className="auth-copy">Your password must be at least 8 characters.</p>

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
                placeholder="Choose a strong password"
                autoComplete="new-password"
                minLength={8}
                required
              />
            </label>

            <label>
              Confirm password
              <input
                type="password"
                value={confirmPassword}
                onChange={(event) => setConfirmPassword(event.target.value)}
                placeholder="Repeat your password"
                autoComplete="new-password"
                minLength={8}
                required
              />
            </label>

            {error ? <p className="form-message error">{error}</p> : null}

            <button className="primary-button" type="submit" disabled={isSubmitting}>
              {isSubmitting ? "Creating account..." : "Register"}
            </button>
          </form>

          <p className="auth-switch">
            Already registered? <Link to="/login">Sign in</Link>.
          </p>
        </section>
      </main>
    </div>
  );
}

export default Register;
