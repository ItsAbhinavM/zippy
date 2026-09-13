import { Box, Typography } from "@mui/material";
import { useRemoteParticipants } from "@livekit/components-react";
import { AmbientGlow } from "./AmbientGlow";
import { useAgentAudioState } from "../hooks/useAgentAudioState";

const STATE_LABEL = {
  idle: "Listening",
  processing: "Thinking",
  replying: "Speaking",
};

export function VoiceOrb() {
  const remoteParticipants = useRemoteParticipants();
  const botPresent = remoteParticipants.length > 0;
  const audioState = useAgentAudioState();

  return (
    <Box
      sx={{
        position: "relative",
        height: 320,
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "flex-end",
        pb: 4,
      }}
    >
      <AmbientGlow state={audioState} />

      <Box
        sx={{
          position: "relative",
          zIndex: 1,
          width: 108,
          height: 108,
          borderRadius: "50%",
          background: "linear-gradient(160deg, #C9A227 0%, #8F7218 100%)",
          opacity: botPresent ? 1 : 0.35,
          boxShadow: botPresent ? "0 0 40px rgba(201,162,39,0.35)" : "none",
          transition: "opacity 400ms ease, box-shadow 400ms ease",
        }}
      />
      <Typography
        variant="caption"
        sx={{ mt: 2, position: "relative", zIndex: 1, color: "text.secondary", fontWeight: 600 }}
      >
        {botPresent ? STATE_LABEL[audioState] : "Connecting…"}
      </Typography>
    </Box>
  );
}