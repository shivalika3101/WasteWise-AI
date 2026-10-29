function BinVisual({ kind, label, className = "" }) {
  const visualClassName = `bin-visual bin-visual-${kind} ${className}`.trim();

  if (kind === "red-sack" || kind === "blue-sack") {
    return (
      <svg className={visualClassName} viewBox="0 0 84 104" role="img" aria-label={label}>
        <title>{label}</title>
        <path className="bin-visual-body bin-visual-outline" d="M23 25 L61 25 L66 91 Q64 98 57 99 L27 99 Q20 98 18 91 Z" />
        <g className="bin-visual-lid">
          <path className="bin-visual-detail bin-visual-outline" d="M22 29 Q42 21 62 29 L60 34 Q42 28 24 34 Z" />
          <path className="bin-visual-detail bin-visual-outline" d="M24 25 Q29 15 35 24 M49 24 Q56 15 61 25" fill="none" />
        </g>
        <path className="bin-visual-outline bin-visual-folds" d="M28 38 Q42 33 56 38 M27 50 Q42 45 57 50 M26 63 Q42 58 58 63" fill="none" />
        <rect className="bin-visual-label bin-visual-outline" x="31" y="69" width="22" height="14" rx="3" />
      </svg>
    );
  }

  if (kind === "food-caddy" || kind === "glass-caddy") {
    return (
      <svg className={visualClassName} viewBox="0 0 84 104" role="img" aria-label={label}>
        <title>{label}</title>
        <path className="bin-visual-body bin-visual-outline" d="M20 31 H64 L60 93 Q59 98 54 98 H30 Q25 98 24 93 Z" />
        <g className="bin-visual-lid">
          <path className="bin-visual-detail bin-visual-outline" d="M18 30 H66 V38 H18 Z" />
        </g>
        <path className="bin-visual-outline" d="M27 30 Q29 16 42 16 Q55 16 57 30" fill="none" />
        <rect className="bin-visual-label bin-visual-outline" x="31" y="58" width="22" height="16" rx="3" />
      </svg>
    );
  }

  if (kind === "textile-bank") {
    return (
      <svg className={visualClassName} viewBox="0 0 84 104" role="img" aria-label={label}>
        <title>{label}</title>
        <path className="bin-visual-body bin-visual-outline" d="M18 24 Q18 18 24 18 H60 Q66 18 66 24 V98 H18 Z" />
        <g className="bin-visual-lid">
          <path className="bin-visual-detail bin-visual-outline" d="M27 34 H57 V54 H27 Z" />
          <path className="bin-visual-dark bin-visual-outline" d="M31 40 H53 V47 H31 Z" />
        </g>
        <path className="bin-visual-label bin-visual-outline" d="M33 65 H51 V84 H33 Z M30 71 H54" />
      </svg>
    );
  }

  return (
    <svg className={visualClassName} viewBox="0 0 84 104" role="img" aria-label={label}>
      <title>{label}</title>
      <path className="bin-visual-body bin-visual-outline" d="M33 22 H51 L48 30 Q62 43 65 88 Q65 98 55 99 H29 Q19 98 19 88 Q22 43 36 30 Z" />
      <g className="bin-visual-lid">
        <path className="bin-visual-detail bin-visual-outline" d="M33 22 Q42 27 51 22 L48 30 Q42 34 36 30 Z" />
        <path className="bin-visual-detail bin-visual-outline" d="M33 22 L28 15 M51 22 L56 15 M34 24 Q42 29 50 24" fill="none" />
      </g>
      <path className="bin-visual-outline bin-visual-folds" d="M28 53 Q42 45 56 53 M26 68 Q42 60 58 68" fill="none" />
    </svg>
  );
}

export default BinVisual;
