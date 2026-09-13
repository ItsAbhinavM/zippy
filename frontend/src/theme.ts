import { createTheme } from "@mui/material/styles";

export const theme = createTheme({
  palette: {
    mode: "light",
    primary: { main: "#2E6F5E" },   // muted teal-green — calm, not alarming
    secondary: { main: "#B5651D" }, // warm amber accent for warnings/conflicts
    background: { default: "#F7F7F5" },
    success: { main: "#2E7D32" },
    warning: { main: "#ED6C02" },
    error: { main: "#C62828" },
  },
  shape: { borderRadius: 12 },
  typography: {
    fontFamily: `"Roboto", "Helvetica", "Arial", sans-serif`,
    h6: { fontWeight: 600 },
  },
  components: {
    MuiCard: {
      styleOverrides: {
        root: { boxShadow: "0 1px 4px rgba(0,0,0,0.08)" },
      },
    },
  },
});