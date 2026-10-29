import { useNavigate } from "react-router-dom";

import { useAuth } from "../context/useAuth";

function Hero() {
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();

  return (
    <section className="hero">
      <div className="hero-left">
        <span className="badge">AI-powered recycling</span>
        <h1>Smart waste classification for an authenticated journey.</h1>
        <h2>Register, sign in, upload one image, and get disposal guidance.</h2>
        <p>
          WasteWise AI now supports protected profile and upload routes,
          restored auth state, and a real API-backed prediction flow that
          returns category, confidence, bin guidance, and a prediction ID.
        </p>

        <div className="hero-buttons">
          <button
            className="primary-button"
            onClick={() => navigate(isAuthenticated ? "/prediction" : "/register")}
          >
            {isAuthenticated ? "Upload image" : "Create account"}
          </button>

          <button
            className="ghost-button"
            onClick={() => navigate(isAuthenticated ? "/profile" : "/login")}
          >
            {isAuthenticated ? "View profile" : "Sign in"}
          </button>
        </div>
      </div>

      <div className="hero-right">
        <div className="circle">Sort smarter</div>
      </div>
    </section>
  );
}

export default Hero;
