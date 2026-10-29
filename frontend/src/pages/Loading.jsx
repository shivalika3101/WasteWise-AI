import { useEffect } from "react";
import { useLocation, useNavigate } from "react-router-dom";

import Navbar from "../components/Navbar";

function Loading() {
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    const timer = setTimeout(() => {
      navigate("/result", {
        state: location.state,
      });
    }, 2500);

    return () => clearTimeout(timer);
  }, [location.state, navigate]);

  return (
    <div className="page-shell">
      <Navbar />
      <div className="loading-page">
        <div className="loader"></div>
        <h1>AI is analysing your image...</h1>
        <p>Please wait a few seconds.</p>
      </div>
    </div>
  );
}

export default Loading;
