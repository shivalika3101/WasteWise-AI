import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import Navbar from "../components/Navbar";
import { useAuth } from "../context/useAuth";
import { fetchPredictionHistory, fetchProfileSummary } from "../services/api";
import { getBinDisplay } from "../utils/binDisplay";

const PAGE_SIZE = 10;

function Profile() {
  const { signOut, token, user } = useAuth();
  const [history, setHistory] = useState([]);
  const [historyState, setHistoryState] = useState("loading");
  const [summary, setSummary] = useState(null);
  const [summaryState, setSummaryState] = useState("loading");
  const [hasMoreHistory, setHasMoreHistory] = useState(false);
  const [isLoadingMore, setIsLoadingMore] = useState(false);
  const [reloadVersion, setReloadVersion] = useState(0);

  useEffect(() => {
    let isCurrent = true;

    async function loadProfile() {
      const [historyResult, summaryResult] = await Promise.allSettled([
        fetchPredictionHistory(token, { limit: PAGE_SIZE }),
        fetchProfileSummary(token),
      ]);

      if (!isCurrent) {
        return;
      }

      const expired = [historyResult, summaryResult].some(
        (result) => result.status === "rejected" && result.reason?.status === 401,
      );

      if (expired) {
        setHistoryState("expired");
        setSummaryState("expired");
        return;
      }

      if (historyResult.status === "fulfilled") {
        setHistory(historyResult.value);
        setHasMoreHistory(historyResult.value.length === PAGE_SIZE);
        setHistoryState("ready");
      } else {
        setHistoryState("error");
      }

      if (summaryResult.status === "fulfilled") {
        setSummary(summaryResult.value);
        setSummaryState("ready");
      } else {
        setSummaryState("error");
      }
    }

    loadProfile();
    return () => {
      isCurrent = false;
    };
  }, [reloadVersion, token]);

  function retryProfile() {
    setHistoryState("loading");
    setSummaryState("loading");
    setHistory([]);
    setSummary(null);
    setHasMoreHistory(false);
    setReloadVersion((currentVersion) => currentVersion + 1);
  }

  async function loadMoreHistory() {
    setIsLoadingMore(true);

    try {
      const nextPage = await fetchPredictionHistory(token, {
        limit: PAGE_SIZE,
        offset: history.length,
      });
      setHistory((currentHistory) => [...currentHistory, ...nextPage]);
      setHasMoreHistory(nextPage.length === PAGE_SIZE);
    } catch (error) {
      if (error.status === 401) {
        setHistoryState("expired");
      } else {
        setHistoryState("error");
      }
    } finally {
      setIsLoadingMore(false);
    }
  }

  return (
    <div className="page-shell">
      <Navbar />
      <main className="content-layout">
        <section className="profile-hero card-surface">
          <div>
            <span className="badge">Protected profile</span>
            <h1>Your account is authenticated.</h1>
          </div>
          <Link to="/prediction" className="primary-button link-button">
            Upload an image
          </Link>
        </section>

        <section className="card-grid">
          <article className="card-surface">
            <p className="eyebrow">Account email</p>
            <h2>{user?.email}</h2>
          </article>

          <article className="card-surface">
            <p className="eyebrow">Member since</p>
            <h2>
              {user?.created_at
                ? new Date(user.created_at).toLocaleString()
                : "Unknown"}
            </h2>
          </article>
        </section>

        {summaryState === "loading" ? (
          <p className="history-status">Loading your activity summary…</p>
        ) : null}

        {summaryState === "ready" ? (
          <section className="summary-grid" aria-label="Activity summary">
            <article className="card-surface">
              <p className="eyebrow">Total scans</p>
              <h2>{summary.total_predictions}</h2>
            </article>
            <article className="card-surface">
              <p className="eyebrow">Latest result</p>
              <h2>{summary.latest_prediction?.category ?? "No scans yet"}</h2>
            </article>
            <article className="card-surface">
              <p className="eyebrow">Most frequent category</p>
              <h2>{summary.most_frequent_category ?? "No scans yet"}</h2>
            </article>
          </section>
        ) : null}

        {summaryState === "error" ? (
          <p className="form-message error">
            Your activity summary is unavailable right now. Your scan history may still load below.
          </p>
        ) : null}

        <section className="card-surface history-panel">
          <div className="section-heading">
            <div>
              <p className="eyebrow">Your scans</p>
              <h2>Prediction history</h2>
            </div>
            <Link to="/prediction" className="ghost-button link-button">
              Scan an item
            </Link>
          </div>

          {historyState === "loading" ? (
            <p className="history-status">Loading your previous scans…</p>
          ) : null}

          {historyState === "expired" ? (
            <div className="form-message error">
              <p>Your sign-in session has expired. Please sign in again to view your history.</p>
              <button className="ghost-button" type="button" onClick={signOut}>
                Go to sign in
              </button>
            </div>
          ) : null}

          {historyState === "error" ? (
            <div className="form-message error">
              <p>We could not load your prediction history.</p>
              <button className="ghost-button" type="button" onClick={retryProfile}>
                Try again
              </button>
            </div>
          ) : null}

          {historyState === "ready" && history.length === 0 ? (
            <div className="history-status">
              <h3>No scans yet</h3>
              <p>Upload your first waste image to start building your history.</p>
            </div>
          ) : null}

          {historyState === "ready" && history.length > 0 ? (
            <div className="history-list">
              {history.map((prediction) => {
                const binDisplay = getBinDisplay(prediction.bin);
                const createdAt = new Date(prediction.created_at);
                const hasValidCreatedAt = !Number.isNaN(createdAt.getTime());

                return (
                  <Link
                    className="history-item"
                    key={prediction.prediction_id}
                    to="/result"
                    state={{
                      category: prediction.category,
                      confidence: prediction.confidence,
                      bin: prediction.bin,
                      guidance: prediction.guidance,
                      predictionId: prediction.prediction_id,
                    }}
                  >
                    <div>
                      <h3>{prediction.category}</h3>
                      <p>{binDisplay.name}</p>
                      <p className="history-guidance">{prediction.guidance}</p>
                    </div>
                    <div className="history-meta">
                      <span>{(prediction.confidence * 100).toFixed(1)}% confident</span>
                      {hasValidCreatedAt ? (
                        <time dateTime={prediction.created_at}>
                          {createdAt.toLocaleString([], {
                            dateStyle: "medium",
                            timeStyle: "short",
                          })}
                        </time>
                      ) : (
                        <span>Time unavailable</span>
                      )}
                    </div>
                  </Link>
                );
              })}
            </div>
          ) : null}

          {historyState === "ready" && hasMoreHistory ? (
            <button
              className="ghost-button history-load-more"
              type="button"
              disabled={isLoadingMore}
              onClick={loadMoreHistory}
            >
              {isLoadingMore ? "Loading more…" : "Load more scans"}
            </button>
          ) : null}
        </section>
      </main>
    </div>
  );
}

export default Profile;
