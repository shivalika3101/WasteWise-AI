import BinVisual from "./BinVisual";

function BinChoiceGrid({ bins, selectedBinId, onSelect, disabled = false }) {
  return (
    <div className="bin-options" aria-label="Bin choices">
      {bins.map((bin) => (
        <button
          key={bin.id}
          type="button"
          className={`bin-option-card ${selectedBinId === bin.id ? "active-bin" : ""}`}
          aria-pressed={selectedBinId === bin.id}
          disabled={disabled}
          onClick={() => onSelect(bin.id)}
        >
          <BinVisual
            kind={bin.visual}
            label={`${bin.name} illustration`}
            className="bin-option-visual"
          />
          <span className="bin-option-copy">
            <strong>{bin.name}</strong>
            <span>{bin.description}</span>
          </span>
        </button>
      ))}
    </div>
  );
}

export default BinChoiceGrid;
