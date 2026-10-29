import BinVisual from "./BinVisual";
import { getBinDisplay } from "../utils/binDisplay";

function BinResultCard({ binName, label, status, animate = false }) {
  const bin = getBinDisplay(binName);

  return (
    <article className={`bin-result-card bin-result-${status}`}>
      <BinVisual
        kind={bin.visual}
        label={`${bin.name} illustration`}
        className={`bin-result-visual ${animate ? "confirmed-bin-visual" : ""}`}
      />
      <div className="bin-result-copy">
        <span className="bin-result-label">{label}</span>
        <h3>{bin.name}</h3>
        <p>{bin.description}</p>
      </div>
    </article>
  );
}

export default BinResultCard;
