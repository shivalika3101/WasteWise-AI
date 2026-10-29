function CameraView({
  videoRef,
  previewSrc,
  live,
  corners = "green",
  statusText,
  badge = "Camera Off",
}) {
  return (
    <div className={`camera-stage ${corners === "danger" ? "corners-danger" : ""}`}>
      <div className="camera-frame">
        {live ? (
          <>
            <video ref={videoRef} className="camera-video" playsInline muted />
            <div className="camera-overlay" aria-hidden="true">
              <div className="camera-corners"></div>
            </div>
          </>
        ) : previewSrc ? (
          <img
            src={previewSrc}
            alt="Captured waste preview"
            className="camera-preview-image"
          />
        ) : (
          <div className="camera-placeholder">
            <p>{statusText}</p>
          </div>
        )}
      </div>

      <div className="camera-status-row">
        <span className={`status-dot ${live ? "is-live" : "is-off"}`}></span>
        <span>{badge}</span>
      </div>
    </div>
  );
}

export default CameraView;
