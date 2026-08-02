// Three theme families, each with a light and dark variant. Palettes match
// the original "Visual Direction" pitch exactly (see that artifact for the
// full rationale/mockups) — only semantic tokens not shown in the pitch
// (error, info, surface-variant) were filled in following the same reuse
// patterns the pitch itself established.

export const tastingNotesLight = {
  dark: false,
  colors: {
    background: '#FAF6EE',
    surface: '#FFFDF8',
    'surface-variant': '#EDE0C9',
    primary: '#3E6259',
    secondary: '#6B4A30',
    error: '#9C4A3E',
    warning: '#8A6E4B',
    success: '#3E6259',
    info: '#3E6259',
    cider: '#3E6259',
    whiskey: '#8A6E4B',
    coffee: '#6B4A30',
    glow: '#3E6259',
    'on-background': '#262220',
    'on-surface': '#262220',
    'on-primary': '#FAF6EE',
    'on-secondary': '#FAF6EE',
  },
};

export const tastingNotesDark = {
  dark: true,
  colors: {
    background: '#1C1917',
    surface: '#221E1A',
    'surface-variant': '#2E2822',
    primary: '#6FA396',
    secondary: '#B98A5F',
    error: '#BE6552',
    warning: '#C9A878',
    success: '#6FA396',
    info: '#6FA396',
    cider: '#6FA396',
    whiskey: '#C9A878',
    coffee: '#B98A5F',
    glow: '#6FA396',
    'on-background': '#EDE6D8',
    'on-surface': '#EDE6D8',
    'on-primary': '#14201D',
    'on-secondary': '#14201D',
  },
};

export const cellarLight = {
  dark: false,
  colors: {
    background: '#F3E9DC',
    surface: '#FBF3E7',
    'surface-variant': '#EADBC6',
    primary: '#B0592A',
    secondary: '#6B3F2A',
    error: '#9C3B2E',
    warning: '#E8A33D',
    success: '#7A8F4A',
    info: '#3E6259',
    cider: '#7A8F4A',
    whiskey: '#B0592A',
    coffee: '#6B3F2A',
    glow: '#E8A33D',
    'on-background': '#241712',
    'on-surface': '#241712',
    'on-primary': '#FFF3E6',
    'on-secondary': '#FFF3E6',
  },
};

export const cellarDark = {
  dark: true,
  colors: {
    background: '#1A120D',
    surface: '#241812',
    'surface-variant': '#2E1F16',
    primary: '#D97D3F',
    secondary: '#C99B73',
    error: '#C15B45',
    warning: '#E8A33D',
    success: '#9FB373',
    info: '#6FA396',
    cider: '#9FB373',
    whiskey: '#D97D3F',
    coffee: '#C99B73',
    glow: '#E8A33D',
    'on-background': '#F3E9DC',
    'on-surface': '#F3E9DC',
    'on-primary': '#1A120D',
    'on-secondary': '#1A120D',
  },
};

export const ledgerLight = {
  dark: false,
  colors: {
    background: '#EFE7DC',
    surface: '#F7F1E7',
    'surface-variant': '#E3D6BE',
    primary: '#8A6822',
    secondary: '#6E1F2A',
    error: '#6E1F2A',
    warning: '#8A6822',
    success: '#5A6B3F',
    info: '#5A4D34',
    cider: '#5A4D34',
    whiskey: '#5A4D34',
    coffee: '#5A4D34',
    glow: '#8A6822',
    'on-background': '#14110F',
    'on-surface': '#14110F',
    'on-primary': '#14110F',
    'on-secondary': '#EFE7DC',
  },
};

export const ledgerDark = {
  dark: true,
  colors: {
    background: '#14110F',
    surface: '#1B1714',
    'surface-variant': '#241F19',
    primary: '#C9A15A',
    secondary: '#6E1F2A',
    error: '#C9727E',
    warning: '#C9A15A',
    success: '#8FA36F',
    info: '#C9A15A',
    cider: '#C9A15A',
    whiskey: '#C9A15A',
    coffee: '#C9A15A',
    glow: '#C9A15A',
    'on-background': '#EFE7DC',
    'on-surface': '#EFE7DC',
    'on-primary': '#14110F',
    'on-secondary': '#EFE7DC',
  },
};

export const THEME_FAMILIES = [
  { key: 'tastingNotes', label: 'Tasting Notes', tagline: 'Quiet — a cupping scoresheet', swatch: '#3E6259' },
  { key: 'cellar', label: 'The Cellar', tagline: 'Bold — oak, copper, cask-room warmth', swatch: '#B0592A' },
  { key: 'ledger', label: 'The Ledger', tagline: "Moody — a bartender's log", swatch: '#C9A15A' },
];

const VALID_THEME_NAMES = new Set(
  THEME_FAMILIES.flatMap((f) => [`${f.key}Light`, `${f.key}Dark`])
);

export function themeNameFor(family, dark) {
  return `${family}${dark ? 'Dark' : 'Light'}`;
}

export function familyFromThemeName(name) {
  return name.replace(/(Light|Dark)$/, '');
}

export function isDarkThemeName(name) {
  return name.endsWith('Dark');
}

const STORAGE_KEY = 'cask-and-cup-theme';

export function getStoredTheme() {
  try {
    return localStorage.getItem(STORAGE_KEY);
  } catch {
    return null;
  }
}

export function setStoredTheme(name) {
  try {
    localStorage.setItem(STORAGE_KEY, name);
  } catch {
    // ignore (private browsing, etc.)
  }
}

export function prefersDark() {
  return window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
}

export function initialTheme() {
  const stored = getStoredTheme();
  if (stored && VALID_THEME_NAMES.has(stored)) {
    return stored;
  }
  return themeNameFor('cellar', prefersDark());
}
