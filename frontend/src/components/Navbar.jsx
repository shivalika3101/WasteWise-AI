import { Link } from "react-router-dom";

import { useAuth } from "../context/useAuth";

function Navbar() {
  const { isAuthenticated, signOut, user } = useAuth();

  return (
    <nav className="navbar">
      <Link to="/" className="logo" aria-label="WasteWise AI home">
        WasteWise AI
      </Link>

      <div className="menu">
        <Link to="/">Home</Link>
        <Link to="/how-to">How to</Link>
        <Link to="/learn">Learn</Link>
        <Link to="/about">About</Link>
        {isAuthenticated ? <Link to="/profile">Profile</Link> : null}
        {isAuthenticated && user?.role === "admin" ? <Link to="/console/users">Admin</Link> : null}
      </div>

      <div className="nav-actions">
        {isAuthenticated ? (
          <>
            <span className="nav-user">{user?.email}</span>
            <button type="button" className="ghost-button" onClick={signOut}>
              Sign out
            </button>
          </>
        ) : (
          <>
            <Link to="/login" className="ghost-button link-button">
              Sign in
            </Link>
            <Link to="/register" className="primary-button link-button">
              Register
            </Link>
          </>
        )}
      </div>
    </nav>
  );
}

export default Navbar;
