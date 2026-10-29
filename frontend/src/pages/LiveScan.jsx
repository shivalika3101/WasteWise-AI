import { Link, useNavigate } from "react-router-dom";

function LiveScan() {

  const navigate = useNavigate();

  return (

    <div className="live-page">

      <div className="live-container">

        <Link to="/" className="back-btn">

          ← Back Home

        </Link>

        <h1>Live Waste Detection</h1>

        <p>

          Use your device camera to scan waste in real time.

        </p>

        <div className="camera-frame">

          <div className="camera-header">

            <span className="live-dot"></span>

            LIVE CAMERA

          </div>

          <div className="camera-screen">

            📷

            <p>

              Camera Preview

            </p>

          </div>

        </div>

        <div className="camera-buttons">

          <button className="capture-btn">

            📸 Capture Image

          </button>

          <button className="switch-btn">

            🔄 Switch Camera

          </button>

        </div>

        <button

          className="predict-btn"

          onClick={() => navigate("/result")}

        >

          Continue to Prediction

        </button>

      </div>

    </div>

  );

}

export default LiveScan;