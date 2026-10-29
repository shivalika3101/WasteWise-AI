import { Navigate, Outlet } from "react-router-dom";

import { useAuth } from "../context/useAuth";

function GuestRoute() {
  const { isAuthenticated, isRestoring } = useAuth();

  if (isRestoring) {
    return (
      <div className="page-shell centered-shell">
        <div className="status-card">
          <div className="loader loader-inline" aria-hidden="true"></div>
          <h1>Loading</h1>
          <p>Preparing the sign-in experience.</p>
        </div>
      </div>
    );
  }

  if (isAuthenticated) {
    return <Navigate to="/profile" replace />;
  }

  return <Outlet />;
}

export default GuestRoute;
