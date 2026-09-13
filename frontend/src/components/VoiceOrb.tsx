import { Box, Typography } from "@mui/material";
import {
  useParticipantIds,
  useAudioLevelObserver,
} from "@daily-co/daily-react";
import { useState } from "react";

export function VoiceOrb() {
  const participantIds = useParticipantIds({ filter: "remote" });
  const botId = participantIds[0];

  const [level, setLevel] = useState(0);

  useAudioLevelObserver(
    botId,
    (audioLevel) => {
      setLevel(audioLevel);
    }
  );

  const scale = 1 + Math.min(level, 1) * 0.4;

  return (
    <Box display="flex" flexDirection="column" alignItems="center" gap={1}>
      <Box
        sx={{
          width: 72,
          height: 72,
          borderRadius: "50%",
          bgcolor: "primary.main",
          transform: `scale(${scale})`,
          transition: "transform 80ms ease-out",
          opacity: botId ? 1 : 0.4,
        }}
      />

      <Typography variant="caption" color="text.secondary">
        {botId ? "Assistant is on the call" : "Connecting…"}
      </Typography>
    </Box>
  );
}