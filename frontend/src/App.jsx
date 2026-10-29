import { Navigate, Route, Routes } from "react-router-dom";

import AdminRoute from "./components/AdminRoute";
import GuestRoute from "./components/GuestRoute";
import ProtectedRoute from "./components/ProtectedRoute";
import About from "./pages/About";
import AdminBins from "./pages/AdminBins";
import AdminInstructions from "./pages/AdminInstructions";
import AdminLayout from "./pages/AdminLayout";
import AdminMappings from "./pages/AdminMappings";
import AdminUsers from "./pages/AdminUsers";
import AdminUserPredictions from "./pages/AdminUserPredictions";
import BinVerification from "./pages/BinVerification";
import Home from "./pages/Home";
import HowTo from "./pages/HowTo";
import LiveScan from "./pages/LiveScan";
import Loading from "./pages/Loading";
import Blog from "./pages/Blog";
import BlogPost from "./pages/BlogPost";
import Login from "./pages/Login";
import Prediction from "./pages/Prediction";
import Profile from "./pages/Profile";
import Register from "./pages/Register";
import Result from "./pages/Result";

function App() {
  return (
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/about" element={<About />} />
      <Route path="/learn" element={<Blog />} />
      <Route path="/learn/:slug" element={<BlogPost />} />
      <Route path="/how-to" element={<HowTo />} />
      <Route path="/live-scan" element={<LiveScan />} />

      <Route element={<GuestRoute />}>
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
      </Route>

      <Route element={<ProtectedRoute />}>
        <Route path="/profile" element={<Profile />} />
        <Route path="/prediction" element={<Prediction />} />
        <Route path="/bin-verification" element={<BinVerification />} />
        <Route path="/result" element={<Result />} />
        <Route path="/loading" element={<Loading />} />
      </Route>

      <Route element={<AdminRoute />}>
        <Route path="/console" element={<AdminLayout />}>
          <Route index element={<Navigate to="users" replace />} />
          <Route path="users" element={<AdminUsers />} />
          <Route path="users/:userId/predictions" element={<AdminUserPredictions />} />
          <Route path="bins" element={<AdminBins />} />
          <Route path="disposal-instructions" element={<AdminInstructions />} />
          <Route path="mappings" element={<AdminMappings />} />
        </Route>
      </Route>
    </Routes>
  );
}

export default App;
