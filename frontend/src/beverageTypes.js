// Single source of truth for per-type fields, driving both the beverage
// add/edit form (detailFields) and the add-rating dialog (ratingAttributeFields,
// which get bundled into Rating.attributes). Add a field here to start
// tracking it — no backend changes needed for ratingAttributeFields since
// they're stored as JSON.

export const BEVERAGE_TYPES = {
  cider: {
    label: "Cider",
    detailFields: [
      { key: "abv", label: "ABV (%)", type: "number" },
      { key: "style", label: "Style", type: "text" },
    ],
    ratingAttributeFields: [],
  },
  whiskey: {
    label: "Whiskey",
    detailFields: [
      { key: "abv", label: "ABV (%)", type: "number" },
      { key: "style", label: "Style", type: "text" },
      { key: "year", label: "Year", type: "number" },
      { key: "batch_number", label: "Batch Number", type: "text" },
    ],
    ratingAttributeFields: [],
  },
  coffee: {
    label: "Coffee",
    detailFields: [
      { key: "origin", label: "Origin", type: "text" },
      { key: "roast_level", label: "Roast Level", type: "text" },
      { key: "process", label: "Process", type: "text" },
      { key: "varietal", label: "Varietal", type: "text" },
    ],
    ratingAttributeFields: [
      { key: "grind_size", label: "Grind Size", type: "text" },
      { key: "brew_method", label: "Brew Method", type: "text" },
      { key: "water_ratio", label: "Water Ratio", type: "text" },
      { key: "water_temp_c", label: "Water Temp (°C)", type: "number" },
    ],
  },
};

export const BEVERAGE_TYPE_OPTIONS = Object.entries(BEVERAGE_TYPES).map(
  ([value, { label }]) => ({ value, title: label })
);

export function typeLabel(type) {
  return BEVERAGE_TYPES[type]?.label || type;
}
