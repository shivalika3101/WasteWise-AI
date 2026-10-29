import { Link, useLocation } from "react-router-dom";

import BinResultCard from "../components/BinResultCard";
import Navbar from "../components/Navbar";

function Result() {
  const location = useLocation();

  const result = location.state ?? {
    image: null,
    category: "No result loaded",
    confidence: 0,
    bin: "Unknown",
    guidance: "Upload an image to view a fresh prediction.",
    predictionId: null,
  };
  return (
    <div className="page-shell">
      <Navbar />
      <main className="content-layout">
        <section className="card-surface result-shell">
          <Link to="/prediction" className="back-btn">
            Back to upload
          </Link>

          <h1>Prediction result</h1>

          <div className={`result-grid${result.image ? "" : " result-grid-no-image"}`}>
            {result.image ? (
              <div className="image-section">
                <img src={result.image} alt="Uploaded waste" className="result-image" />
                {result.fileName ? <p className="preview-caption">{result.fileName}</p> : null}
              </div>
            ) : null}

            <div className="details-section">
              <div className="result-item">
                <h3>Predicted waste</h3>
                <p>{result.category}</p>
              </div>

              <div className="result-item">
                <h3>Confidence</h3>
                <p>{(result.confidence * 100).toFixed(1)}%</p>
              </div>

              <BinResultCard
                binName={result.bin}
                label="Recommended bin"
                status="correct"
                animate
              />

              <div className="result-item">
                <h3>Disposal guidance</h3>
                <p>{result.guidance}</p>
              </div>

              <div className="result-item">
                <h3>Prediction ID</h3>
                <p>{result.predictionId ?? "Unavailable"}</p>
              </div>

              <div className="button-group">
                <Link to="/bin-verification" state={result} className="verify-btn">
                  Review bin step
                </Link>
                <Link to="/prediction" className="scan-btn">
                  Upload another
                </Link>
              </div>
            </div>
          </div>
        </section>
      </main>
    </div>
  );
}

export default Result;
