import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import BinChoiceGrid from "../components/BinChoiceGrid";
import Navbar from "../components/Navbar";
import { useAuth } from "../context/useAuth";
import {
  createPrediction,
  fetchBinOptions,
  submitBinExamination,
} from "../services/api";
import { getBinChoices } from "../utils/binDisplay";
import demoBottleImage from "../assets/plastic_water_bottle.png";

function Prediction() {
  const { token } = useAuth();
  const navigate = useNavigate();
  const [file, setFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState("");
  const [mode, setMode] = useState("");
  const [binOptions, setBinOptions] = useState([]);
  const [selectedBinId, setSelectedBinId] = useState(null);
  const [isLoadingBins, setIsLoadingBins] = useState(false);
  const [binError, setBinError] = useState("");
  const [binLoadAttempt, setBinLoadAttempt] = useState(0);
  const [savedPrediction, setSavedPrediction] = useState(null);
  const [error, setError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const localBinChoices = getBinChoices(binOptions);

  useEffect(() => {
    if (mode !== "verify" || !token) {
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
          setBinError(loadError.message);
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
  }, [binLoadAttempt, mode, token]);

  function selectMode(nextMode) {
    if (nextMode !== mode) {
      setMode(nextMode);
      setSavedPrediction(null);
      setError("");
      if (nextMode === "verify") {
        setIsLoadingBins(true);
        setBinError("");
      }
    }
  }

  function retryBinLoading() {
    setIsLoadingBins(true);
    setBinError("");
    setBinLoadAttempt((attempt) => attempt + 1);
  }

  function handleImage(event) {
    if (event.target.files.length === 0) {
      return;
    }

    const nextFile = event.target.files[0];
    setFile(nextFile);
    setPreviewUrl(URL.createObjectURL(nextFile));
    setSavedPrediction(null);
    setError("");
  }

  async function handleDemoImage() {
    try {
      const response = await fetch(demoBottleImage);
      const demoBlob = await response.blob();
      const demoFile = new File([demoBlob], "demo-plastic-water-bottle.png", {
        type: "image/png",
      });

      setFile(demoFile);
      setPreviewUrl(demoBottleImage);
      setSavedPrediction(null);
      setError("");
    } catch {
      setError("The demo image could not be loaded. Please choose an image instead.");
    }
  }

  async function handleSubmit() {
    if (!file || !token || !mode) {
      return;
    }

    if (mode === "verify" && !selectedBinId) {
      setError("Choose the bin you think is correct before verifying.");
      return;
    }

    setError("");
    setIsSubmitting(true);

    try {
      let prediction = savedPrediction;

      if (!prediction) {
        prediction = await createPrediction({ token, file });
        if (mode === "verify") {
          setSavedPrediction(prediction);
        }
      }

      const resultState = {
        image: previewUrl,
        fileName: file.name,
        predictionId: prediction.prediction_id,
        category: prediction.category,
        confidence: prediction.confidence,
        bin: prediction.bin,
        guidance: prediction.guidance,
      };

      if (mode === "detect") {
        navigate("/result", { state: resultState });
        return;
      }

      const examination = await submitBinExamination({
        token,
        predictionId: prediction.prediction_id,
        selectedBinId,
      });
      navigate("/bin-verification", {
        state: {
          ...resultState,
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

  return (
    <div className="page-shell">
      <Navbar />
      <main className="content-layout">
        <section className="upload-header card-surface">
          <div>
            <Link to="/profile" className="back-btn">
              Back to profile
            </Link>
            <h1>Choose how you want to check your waste</h1>
            <p>
              Let WasteWise identify the right bin, or choose a bin first and
              check whether it is correct.
            </p>
          </div>
        </section>

        <section className="journey-options" aria-label="Waste checking options">
          <button
            type="button"
            className={`journey-option ${mode === "detect" ? "active" : ""}`}
            aria-pressed={mode === "detect"}
            onClick={() => selectMode("detect")}
          >
            <span>
              <strong>Detect my waste</strong>
              <span>Upload an image to identify its category and recommended bin.</span>
            </span>
          </button>
          <button
            type="button"
            className={`journey-option ${mode === "verify" ? "active" : ""}`}
            aria-pressed={mode === "verify"}
            onClick={() => selectMode("verify")}
          >
            <span>
              <strong>Verify my bin choice</strong>
              <span>Choose a bin, upload your waste, and check your decision.</span>
            </span>
          </button>
        </section>

        {mode ? (
          <section className={`upload-panel ${mode === "verify" ? "verification-upload-panel" : ""}`}>
            <div className="upload-box upload-box-large">
              {previewUrl ? (
                <>
                  <img src={previewUrl} alt="Waste preview" className="preview-image" />
                  <p className="preview-caption">{file?.name}</p>
                </>
              ) : (
                <>
                  <div className="upload-icon">Preview</div>
                  <h2>Select an image</h2>
                  <p>Supported formats: JPG, JPEG, PNG up to 5 MB.</p>
                </>
              )}

              <label className="primary-button file-button">
                Choose image
                <input type="file" accept="image/png,image/jpeg" onChange={handleImage} hidden />
              </label>
              <button className="demo-button" type="button" onClick={handleDemoImage}>
                Try a demo plastic bottle
              </button>
            </div>

            <aside className="card-surface upload-summary">
              {mode === "verify" ? (
                <>
                  <div>
                    <h2>Choose your bin</h2>
                    <p>Select the bin you would use before uploading for verification.</p>
                  </div>

                  {isLoadingBins ? (
                    <p role="status" aria-live="polite">Loading bin choices...</p>
                  ) : null}
                  {binError ? (
                    <div className="form-message error" role="alert">
                      <span>{binError}</span>
                      <button
                        className="ghost-button"
                        type="button"
                        onClick={retryBinLoading}
                      >
                        Try loading bins again
                      </button>
                    </div>
                  ) : null}
                  {!isLoadingBins && !binError ? (
                    <BinChoiceGrid
                      bins={localBinChoices}
                      selectedBinId={selectedBinId}
                      onSelect={setSelectedBinId}
                      disabled={isSubmitting}
                    />
                  ) : null}
                </>
              ) : (
                <>
                  <h2>What you will get</h2>
                  <ul className="checklist">
                    <li>The detected waste category.</li>
                    <li>The recommended local bin.</li>
                    <li>Confidence and disposal guidance.</li>
                  </ul>
                </>
              )}

              {error ? (
                <div className="form-message error" role="alert">
                  <span>{error}</span>
                  {mode === "verify" && savedPrediction ? (
                    <span>Your image is already analysed. Retry will only check the bin choice.</span>
                  ) : null}
                </div>
              ) : null}

              <button
                className="primary-button"
                type="button"
                disabled={
                  !file ||
                  isSubmitting ||
                  (mode === "verify" && (!selectedBinId || isLoadingBins || Boolean(binError)))
                }
                onClick={handleSubmit}
              >
                {isSubmitting
                  ? mode === "verify" ? "Checking choice..." : "Analysing image..."
                  : mode === "verify" && savedPrediction ? "Retry verification"
                  : mode === "verify" ? "Verify my bin"
                  : "Detect waste"}
              </button>
            </aside>
          </section>
        ) : (
          <section className="card-surface journey-prompt">
            <p>Select either option above to continue.</p>
          </section>
        )}
      </main>
    </div>
  );
}

export default Prediction;
