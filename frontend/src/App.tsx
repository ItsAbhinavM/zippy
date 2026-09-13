import { useState } from "react";
import { Container, Box, Typography, Button, Stack, CircularProgress } from "@mui/material";
import { startSession, endSession,type StartSessionResponse } from "./api/session";
import { useStateSocket } from "./hooks/useStaterSocket";
import { CallProvider } from "./livekit/callProvider";
import { CallControls } from "./components/CallControls";
import { VoiceOrb } from "./components/VoiceOrb";
import { CardGrid } from "./components/cards/CardGrid";
import { useFinancialStore } from "./store/useFinancialStore";

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
    <Container maxWidth="md" sx={{ py: 4 }}>
      <Typography variant="h4" fontWeight={700} gutterBottom>
        Zippy — 30-Day Financial Plan
      </Typography>

      {!session && (
        <Box sx={{ textAlign: "center", py: 8 }}>
          <Typography variant="body1" color="text.secondary" mb={3}>
            Start a conversation to build your 30-day financial plan.
          </Typography>
          <Button
            variant="contained"
            size="large"
            onClick={handleStart}
            disabled={loading}
          >
            {loading ? <CircularProgress size={24} color="inherit" /> : "Start conversation"}
          </Button>
        </Box>
      )}

      {session && (
        <CallProvider serverUrl={session.room_url} token={session.user_token}>
          <Stack spacing={3}>
            <Stack direction="row" justifyContent="space-between" alignItems="center">
              <VoiceOrb />
              <CallControls onEnd={handleEnd} />
            </Stack>
            <CardGrid />
          </Stack>
        </CallProvider>
      )}
    </Container>
  );
}