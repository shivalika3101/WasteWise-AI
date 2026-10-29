import { Navigate, Outlet, useLocation } from "react-router-dom";

import { useAuth } from "../context/useAuth";

function ProtectedRoute() {
  const { isAuthenticated, isRestoring } = useAuth();
  const location = useLocation();

  if (isRestoring) {
    return (
      <div className="page-shell centered-shell">
        <div className="status-card">
          <div className="loader loader-inline" aria-hidden="true"></div>
          <h1>Restoring your session</h1>
          <p>Checking your saved sign-in before opening this page.</p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace state={{ from: location }} />;
  }

  return <Outlet />;
}

export default ProtectedRoute;
