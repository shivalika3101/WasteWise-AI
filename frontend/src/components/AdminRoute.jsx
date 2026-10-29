import { Navigate, Outlet } from "react-router-dom";

import { useAuth } from "../context/useAuth";

function AdminRoute() {
  const { isAuthenticated, isRestoring, user } = useAuth();

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
    return <Navigate to="/login" replace />;
  }

  if (user?.role !== "admin") {
    return <Navigate to="/profile" replace />;
  }

  return <Outlet />;
}

export default AdminRoute;
