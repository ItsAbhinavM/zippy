import { createTheme } from "@mui/material/styles";

// A private-bank-at-night palette: ink backgrounds, brass accent for
// money, muted teal secondary. Deliberately not the default fintech
// blue/green or the generic warm-cream/terracotta AI-page look.
export const theme = createTheme({
  palette: {
    mode: "dark",
    background: { default: "#11171B", paper: "#1B2328" },
    primary: { main: "#C9A227", contrastText: "#181310" },
    secondary: { main: "#3F7F74" },
    success: { main: "#4C9A6A" },
    warning: { main: "#D98E3E" },
    error: { main: "#C1553D" },
    text: { primary: "#F3EFE6", secondary: "#A9B0AE" },
    divider: "rgba(243,239,230,0.08)",
  },
  shape: { borderRadius: 16 },
  typography: {
    fontFamily: `"Manrope", "Helvetica", "Arial", sans-serif`,
    h6: { fontWeight: 700 },
    subtitle2: { fontWeight: 700 },
    button: { fontWeight: 700, textTransform: "none" },
  },
  components: {
    MuiPaper: {
      styleOverrides: {
        root: {
          backgroundImage: "none",
          boxShadow: "0 2px 14px rgba(0,0,0,0.35)",
        },
      },
    },
    MuiChip: {
      styleOverrides: { root: { fontWeight: 700 } },
    },
    MuiButton: {
      styleOverrides: { root: { borderRadius: 999 } },
    },
  },
});

// Used only for the "Zippy" wordmark — the one deliberately playful
// element against an otherwise restrained UI.
export const wordmarkFont = `"Baloo 2", "Manrope", sans-serif`;