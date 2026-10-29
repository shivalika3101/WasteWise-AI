import { useEffect, useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";

import BinChoiceGrid from "../components/BinChoiceGrid";
import BinResultCard from "../components/BinResultCard";
import Navbar from "../components/Navbar";
import { useAuth } from "../context/useAuth";
import { fetchBinOptions, submitBinExamination } from "../services/api";
import { getBinChoices } from "../utils/binDisplay";

function BinVerification() {
  const location = useLocation();
  const navigate = useNavigate();
  const { token } = useAuth();
  const prediction = location.state?.category;
  const predictionId = location.state?.predictionId;
  const image = location.state?.image;
  const fileName = location.state?.fileName;
  const confidence = location.state?.confidence;

  const [binOptions, setBinOptions] = useState([]);
  const [selectedBinId, setSelectedBinId] = useState(location.state?.selectedBinId ?? null);
  const [result, setResult] = useState(location.state?.examination ?? null);
  const [error, setError] = useState("");
  const [isLoadingBins, setIsLoadingBins] = useState(Boolean(predictionId));
  const [isSubmitting, setIsSubmitting] = useState(false);
  const localBinChoices = getBinChoices(binOptions);

  useEffect(() => {
    if (!predictionId || !token) {
      return undefined;
    }

    let cancelled = false;
    async function loadBins() {
      try {
        const bins = await fetchBinOptions(token);
        if (!cancelled) {
          setBinOptions(bins);
        }
      } catch (loadError) {
        if (!cancelled) {
          setError(loadError.message);
        }
      } finally {
        if (!cancelled) {
          setIsLoadingBins(false);
        }
      }
    }

    loadBins();
    return () => {
      cancelled = true;
    };
  }, [predictionId, token]);

  async function verifyBin() {
    if (!selectedBinId || !predictionId || !token) {
      setError("Select a bin before verifying your answer.");
      return;
    }

    setError("");
    setResult(null);
    setIsSubmitting(true);
    try {
      const examination = await submitBinExamination({
        token,
        predictionId,
        selectedBinId,
      });
      setResult(examination);
      navigate("/bin-verification", {
        replace: true,
        state: {
          ...location.state,
          examination,
          selectedBinId,
        },
      });
    } catch (submissionError) {
      setError(submissionError.message);
    } finally {
      setIsSubmitting(false);
    }
  }

  function retryBinChoice() {
    setResult(null);
    setError("");
    navigate("/bin-verification", {
      replace: true,
      state: {
        ...location.state,
        examination: null,
        selectedBinId,
      },
    });
  }

  return (
    <div className="page-shell">
      <Navbar />
      <div className="bin-page">
        <div className="bin-container">
          <Link to="/result" state={location.state} className="back-btn">
            Back to result
          </Link>

          <h1>Bin verification</h1>
          <p>Select the local container that matches the API&apos;s recommended disposal route.</p>

          <section className={`verification-context ${image ? "verification-context-with-image" : ""}`}>
            {image ? (
              <div className="verification-image-panel">
                <img src={image} alt="Uploaded waste" className="verification-image" />
                {fileName ? <p className="preview-caption">{fileName}</p> : null}
              </div>
            ) : null}

            <div className="verification-context-details">
              <div className="detected-item">
                <h2>Detected waste</h2>
                <h3>{prediction ?? "No prediction loaded"}</h3>
              </div>
              <div className="verification-meta-grid">
                <article className="result-item">
                  <h3>Confidence</h3>
                  <p>
                    {typeof confidence === "number"
                      ? `${(confidence * 100).toFixed(1)}%`
                      : "Unavailable"}
                  </p>
                </article>
                <article className="result-item">
                  <h3>Prediction ID</h3>
                  <p>{predictionId ?? "Unavailable"}</p>
                </article>
              </div>
            </div>
          </section>

          {!predictionId ? (
            <p className="form-message error" role="alert">
              This step needs a fresh prediction. Return to the upload page and try again.
            </p>
          ) : null}

          {!result && isLoadingBins ? (
            <p role="status" aria-live="polite">Loading bin choices…</p>
          ) : null}
          {!result && !isLoadingBins && predictionId ? (
            <BinChoiceGrid
              bins={localBinChoices}
              selectedBinId={selectedBinId}
              onSelect={setSelectedBinId}
              disabled={isSubmitting}
            />
          ) : null}

          {!result ? (
            <button
              className="verify-main-btn"
              type="button"
              onClick={verifyBin}
              disabled={!predictionId || !selectedBinId || isLoadingBins || isSubmitting}
            >
              {isSubmitting ? "Checking answer…" : "Verify bin"}
            </button>
          ) : null}

          {error ? <p className="form-message error" role="alert">{error}</p> : null}
          {result ? (
            <div
              className={`verification-result ${result.is_correct ? "verification-correct" : "verification-incorrect"}`}
              role="status"
              aria-live="polite"
            >
              <div className="verification-heading">
                <span className="verification-icon" aria-hidden="true">
                  {result.is_correct ? "✓" : "×"}
                </span>
                <div>
                  <h2>{result.is_correct ? "Correct bin choice" : "That bin is not correct"}</h2>
                  <p>
                    {result.is_correct
                      ? "Your selected bin matches the recommendation."
                      : "Your choice and the recommended bin are shown together below."}
                  </p>
                </div>
              </div>

              <div className={`verification-comparison ${result.is_correct ? "single-bin-result" : ""}`}>
                <BinResultCard
                  binName={result.selected_bin}
                  label={result.is_correct ? "Your choice - correct" : "Your choice - incorrect"}
                  status={result.is_correct ? "correct" : "incorrect"}
                  animate={result.is_correct}
                />
                {!result.is_correct ? (
                  <BinResultCard
                    binName={result.recommended_bin}
                    label="Recommended bin - correct"
                    status="correct"
                    animate
                  />
                ) : null}
              </div>

              <div className="verification-guidance">
                <h3>Disposal guidance</h3>
                <p>{result.guidance}</p>
              </div>

              <div className="verification-actions">
                {!result.is_correct ? (
                  <button className="ghost-button" type="button" onClick={retryBinChoice}>
                    Try another bin
                  </button>
                ) : null}
                <Link to="/prediction" className="primary-button link-button">
                  Check another image
                </Link>
              </div>
            </div>
          ) : null}
        </div>
      </div>
    </div>
  );
}

export default BinVerification;
