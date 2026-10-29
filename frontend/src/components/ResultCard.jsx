function ResultCard({ title, value, subtitle, icon, children, accent = "default" }) {
  return (
    <div className={`result-card compact-card accent-${accent}`}>
      <div className="compact-card-head">
        <div>
          <p className="compact-label">{title}</p>
          <h3>{value}</h3>
        </div>
        {icon ? <span className="compact-icon">{icon}</span> : null}
      </div>
      {subtitle ? <p className="compact-subtitle">{subtitle}</p> : null}
      {children}
    </div>
  );
}

export default ResultCard;
