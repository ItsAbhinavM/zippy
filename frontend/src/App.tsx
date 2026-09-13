import { useState } from "react";
import { Box, Typography, Button, CircularProgress } from "@mui/material";
import { startSession, endSession,type StartSessionResponse } from "./api/session";
import { useStateSocket } from "./hooks/useStaterSocket";
import { CallProvider } from "./livekit/callProvider";
import { AgentPanel } from "./components/AgentPanel";
import { CardGrid } from "./components/cards/CardGrid";
import { useFinancialStore } from "./store/useFinancialStore";
import { wordmarkFont } from "./theme";

export default function App() {
  const [session, setSession] = useState<StartSessionResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const reset = useFinancialStore((s) => s.reset);

  useStateSocket(session?.session_id ?? null);

  const handleStart = async () => {
    setLoading(true);
    try {
      const res = await startSession();
      setSession(res);
    } finally {
      setLoading(false);
    }
  };

  const handleEnd = async () => {
    if (session) await endSession(session.session_id);
    setSession(null);
    reset();
  };

  return (
    <Box sx={{ minHeight: "100vh", bgcolor: "background.default" }}>
      {/* Centered header — the one deliberately playful moment */}
      <Box sx={{ textAlign: "center", pt: 6, pb: 4 }}>
        <Typography
          sx={{
            fontFamily: wordmarkFont,
            fontWeight: 800,
            fontSize: { xs: 40, sm: 52 },
            color: "primary.main",
            letterSpacing: 0.5,
          }}
        >
          Zippy
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
          Your 30-day financial plan, talked through out loud.
        </Typography>
      </Box>

      {!session && (
        <Box sx={{ textAlign: "center", pb: 10 }}>
          <Button variant="contained" size="large" onClick={handleStart} disabled={loading} sx={{ px: 4, py: 1.25 }}>
            {loading ? <CircularProgress size={22} color="inherit" /> : "Start conversation"}
          </Button>
        </Box>
      )}

      {session && (
        <CallProvider serverUrl={session.room_url} token={session.user_token}>
          <Box
            sx={{
              maxWidth: 1180,
              mx: "auto",
              px: 3,
              pb: 6,
              display: "grid",
              gridTemplateColumns: { xs: "1fr", md: "1fr 380px" },
              gap: 4,
              alignItems: "start",
            }}
          >
            <CardGrid />
            <AgentPanel onEnd={handleEnd} />
          </Box>
        </CallProvider>
      )}
    </Box>
  );
}