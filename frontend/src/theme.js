// "The Cellar" — warm, tactile theme inspired by an actual cask room:
// oak, copper, amber light. See design pitch for the full rationale.

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
  if (stored === 'cellarLight' || stored === 'cellarDark') {
    return stored;
  }
  return prefersDark() ? 'cellarDark' : 'cellarLight';
}
