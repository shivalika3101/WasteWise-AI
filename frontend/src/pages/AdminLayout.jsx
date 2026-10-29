import { NavLink, Outlet } from "react-router-dom";

import Navbar from "../components/Navbar";

function AdminLayout() {
  return (
    <div className="page-shell">
      <Navbar />
      <main className="content-layout">
        <span className="badge">Admin</span>
        <nav className="admin-tabs">
          <NavLink to="/console/users">Users</NavLink>
          <NavLink to="/console/bins">Bins</NavLink>
          <NavLink to="/console/disposal-instructions">Instructions</NavLink>
          <NavLink to="/console/mappings">Mappings</NavLink>
        </nav>
        <Outlet />
      </main>
    </div>
  );
}

export default AdminLayout;
