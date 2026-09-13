import { useEffect, useState } from "react";
import { Fade, Paper, Typography, Box } from "@mui/material";
import { useFinancialStore } from "../store/useFinancialStore";

const AUTO_HIDE_MS = 6000;

export function LiveCaption() {
  const transcript = useFinancialStore((s) => s.transcript);
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    if (!transcript) return;
    setVisible(true);
    const timer = setTimeout(() => setVisible(false), AUTO_HIDE_MS);
    return () => clearTimeout(timer);
  }, [transcript]);

  return (
    <Box sx={{ minHeight: 76, display: "flex", alignItems: "flex-start", justifyContent: "center", px: 2 }}>
      {transcript && (
        <Fade in={visible} timeout={{ enter: 200, exit: 450 }}>
          <Paper
            elevation={2}
            sx={{
              px: 2.25,
              py: 1.5,
              borderRadius: 3,          // rectangle with rounded corners, not a pill
              maxWidth: 380,
              width: "100%",
              bgcolor: transcript.role === "assistant" ? "rgba(201,162,39,0.12)" : "background.paper",
              border: "1px solid",
              borderColor: transcript.role === "assistant" ? "rgba(201,162,39,0.35)" : "divider",
            }}
          >
            <Typography
              variant="caption"
              sx={{ fontWeight: 700, color: transcript.role === "assistant" ? "primary.main" : "text.secondary" }}
            >
              {transcript.role === "assistant" ? "Zippy" : "You"}
            </Typography>
            <Typography variant="body2" sx={{ mt: 0.25, whiteSpace: "pre-wrap", wordBreak: "break-word" }}>
              {transcript.text}
            </Typography>
          </Paper>
        </Fade>
      )}
    </Box>
  );
}