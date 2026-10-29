const LOCAL_BIN_DETAILS = {
  "Mixed Dry Recycling": {
    name: "Red recycling sack",
    description: "Clean plastic bottles and containers, tins, cans and empty cartons.",
    visual: "red-sack",
  },
  "Plastic & Cans": {
    name: "Red recycling sack",
    description: "Clean plastics, tins, cans and empty cartons.",
    visual: "red-sack",
  },
  "Paper & Card": {
    name: "Blue recycling sack",
    description: "Clean paper and cardboard. Pizza boxes must be grease-free.",
    visual: "blue-sack",
  },
  Glass: {
    name: "Glass caddy",
    description: "Empty glass jars and bottles. Do not include lids.",
    visual: "glass-caddy",
  },
  "Food / Organic": {
    name: "Food-waste caddy",
    description: "Food scraps, peelings and used tea bags. Keep it separate from recycling.",
    visual: "food-caddy",
  },
  "General Waste": {
    name: "General waste (black bag)",
    description: "Items that cannot be recycled, reused or composted.",
    visual: "general-waste",
  },
  Textiles: {
    name: "Textile bank or donation point",
    description: "Clean, dry clothing and shoes for reuse or textile recycling.",
    visual: "textile-bank",
  },
};

const LOCAL_BIN_ORDER = [
  ["Mixed Dry Recycling", "Plastic & Cans"],
  ["Paper & Card"],
  ["Food / Organic"],
  ["Glass"],
  ["General Waste"],
  ["Textiles"],
];

export function getBinDisplay(binName) {
  return LOCAL_BIN_DETAILS[binName] ?? {
    name: binName || "Bin information unavailable",
    description: "Check your local council guidance before disposal.",
    visual: "general-waste",
  };
}

export function getBinChoices(bins) {
  return LOCAL_BIN_ORDER.flatMap((binNames) => {
    const bin = binNames
      .map((binName) => bins.find((option) => option.name === binName))
      .find(Boolean);

    if (!bin) {
      return [];
    }

    return [{ ...bin, ...getBinDisplay(bin.name) }];
  });
}
