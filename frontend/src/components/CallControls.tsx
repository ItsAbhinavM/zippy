import { Button, Paper, Box, Typography, IconButton } from "@mui/material";
import MicIcon from "@mui/icons-material/Mic";
import MicOffIcon from "@mui/icons-material/MicOff";
import CallEndIcon from "@mui/icons-material/CallEnd";
import { useLocalParticipant, useConnectionState } from "@livekit/components-react";
import { ConnectionState } from "livekit-client";

export function CallControls({ onEnd }: { onEnd: () => void }) {
  const { localParticipant } = useLocalParticipant();
  const connectionState = useConnectionState();
  const connected = connectionState === ConnectionState.Connected;
  const muted = !localParticipant?.isMicrophoneEnabled;

  const toggleMute = () => localParticipant?.setMicrophoneEnabled(muted);

  return (
    <Paper
      elevation={3}
      sx={{
        borderRadius: 999,
        px: 1.5,
        py: 1,
        display: "flex",
        alignItems: "center",
        gap: 1.5,
        width: "fit-content",
        mx: "auto",
      }}
    >
      <Box
        sx={{
          width: 8,
          height: 8,
          borderRadius: "50%",
          bgcolor: connected ? "success.main" : "text.secondary",
          ml: 0.5,
        }}
      />
      <Typography variant="caption" color="text.secondary" sx={{ mr: 0.5 }}>
        {connected ? "Live" : "Connecting"}
      </Typography>

      <IconButton onClick={toggleMute} color={muted ? "warning" : "default"} size="small">
        {muted ? <MicOffIcon fontSize="small" /> : <MicIcon fontSize="small" />}
      </IconButton>

      <Button
        variant="contained"
        color="error"
        size="small"
        startIcon={<CallEndIcon />}
        onClick={onEnd}
        sx={{ px: 2 }}
      >
        End
      </Button>
    </Paper>
  );
}