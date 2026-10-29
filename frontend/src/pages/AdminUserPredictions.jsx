import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";

import { useAuth } from "../context/useAuth";
import { fetchAdminUser, fetchAdminUserPredictions } from "../services/api";
import { getBinDisplay } from "../utils/binDisplay";

const PAGE_SIZE = 20;

function AdminUserPredictions() {
  const { userId } = useParams();
  const { token } = useAuth();
  const [user, setUser] = useState(null);
  const [predictions, setPredictions] = useState([]);
  const [status, setStatus] = useState("loading");
  const [hasMore, setHasMore] = useState(false);
  const [isLoadingMore, setIsLoadingMore] = useState(false);

  useEffect(() => {
    let isCurrent = true;

    async function load() {
      try {
        const [userResult, predictionsResult] = await Promise.all([
          fetchAdminUser(token, userId),
          fetchAdminUserPredictions(token, userId, { limit: PAGE_SIZE }),
        ]);
        if (!isCurrent) {
          return;
        }
        setUser(userResult);
        setPredictions(predictionsResult);
        setHasMore(predictionsResult.length === PAGE_SIZE);
        setStatus("ready");
      } catch (error) {
        if (isCurrent) {
          setStatus(error.status === 404 ? "not-found" : "error");
        }
      }
    }

    load();
    return () => {
      isCurrent = false;
    };
  }, [token, userId]);

  async function loadMore() {
    setIsLoadingMore(true);
    try {
      const nextPage = await fetchAdminUserPredictions(token, userId, {
        limit: PAGE_SIZE,
        offset: predictions.length,
      });
      setPredictions((current) => [...current, ...nextPage]);
      setHasMore(nextPage.length === PAGE_SIZE);
    } catch {
      setHasMore(false);
    } finally {
      setIsLoadingMore(false);
    }
  }

  if (status === "loading") {
    return <p className="history-status">Loading predictions...</p>;
  }

  if (status === "not-found") {
    return <p className="form-message error">This user does not exist.</p>;
  }

  if (status === "error") {
    return <p className="form-message error">Could not load this user's predictions.</p>;
  }

  return (
    <section className="card-surface history-panel">
      <div className="section-heading">
        <div>
          <p className="eyebrow">Prediction history</p>
          <h2>{user.email}</h2>
        </div>
        <Link className="ghost-button link-button" to="/console/users">
          Back to users
        </Link>
      </div>

      {predictions.length === 0 ? (
        <div className="history-status">
          <h3>No predictions yet</h3>
          <p>This user has not scanned any items.</p>
        </div>
      ) : (
        <div className="history-list">
          {predictions.map((prediction) => {
            const binDisplay = getBinDisplay(prediction.bin);
            return (
              <div className="history-item" key={prediction.prediction_id}>
                <div>
                  <h3>{prediction.category}</h3>
                  <p>{binDisplay.name}</p>
                  <p className="history-guidance">{prediction.guidance}</p>
                </div>
                <div className="history-meta">
                  <span>{(prediction.confidence * 100).toFixed(1)}% confident</span>
                  <time dateTime={prediction.created_at}>
                    {new Date(prediction.created_at).toLocaleDateString()}
                  </time>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {hasMore ? (
        <button
          className="ghost-button history-load-more"
          type="button"
          disabled={isLoadingMore}
          onClick={loadMore}
        >
          {isLoadingMore ? "Loading more..." : "Load more predictions"}
        </button>
      ) : null}
    </section>
  );
}

export default AdminUserPredictions;
