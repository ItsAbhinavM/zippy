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

  if (!transcript) return null;

  const isAssistant = transcript.role === "assistant";

  return (
    <Box sx={{ display: "flex", justifyContent: "center", width: "100%" }}>
      <Fade in={visible} timeout={{ enter: 200, exit: 500 }}>
        <Paper
          elevation={3}
          sx={{
            px: 2.5,
            py: 1.25,
            borderRadius: 999,
            maxWidth: "90%",
            bgcolor: isAssistant ? "primary.main" : "background.paper",
            color: isAssistant ? "primary.contrastText" : "text.primary",
            border: isAssistant ? "none" : "1px solid",
            borderColor: "divider",
          }}
        >
          <Typography variant="caption" sx={{ opacity: 0.75, display: "block", fontWeight: 600 }}>
            {isAssistant ? "Zippy" : "You"}
          </Typography>
          <Typography variant="body2">{transcript.text}</Typography>
        </Paper>
      </Fade>
    </Box>
  );
}