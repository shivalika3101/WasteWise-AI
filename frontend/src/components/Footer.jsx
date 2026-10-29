import { Link } from "react-router-dom";

function Footer() {
  return (
    <footer>
      <h2>WasteWise AI</h2>
      <p>Cardiff University MSc Data Science Project</p>
      <p className="footer-links">
        <Link to="/how-to">How to</Link>
        <Link to="/learn">Learn</Link>
        <Link to="/about">About</Link>
      </p>
      <small>Copyright 2026 Team B</small>
    </footer>
  );
}

export default Footer;
