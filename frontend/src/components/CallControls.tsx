import { Button, Stack, Chip } from "@mui/material";
import MicIcon from "@mui/icons-material/Mic";
import MicOffIcon from "@mui/icons-material/MicOff";
import CallEndIcon from "@mui/icons-material/CallEnd";
import { useLocalParticipant, useConnectionState } from "@livekit/components-react";
import { ConnectionState } from "livekit-client";

export function CallControls({ onEnd }: { onEnd: () => void }) {
  const { localParticipant } = useLocalParticipant();
  const connectionState = useConnectionState();

  const muted = !localParticipant?.isMicrophoneEnabled;

  const toggleMute = () => {
    localParticipant?.setMicrophoneEnabled(muted);
  };

  return (
    <Stack direction="row" spacing={2} alignItems="center">
      <Chip
        size="small"
        label={connectionState === ConnectionState.Connected ? "Live" : "Connecting"}
        color={connectionState === ConnectionState.Connected ? "success" : "default"}
      />
      <Button
        variant="outlined"
        startIcon={muted ? <MicOffIcon /> : <MicIcon />}
        onClick={toggleMute}
      >
        {muted ? "Unmute" : "Mute"}
      </Button>
      <Button
        variant="contained"
        color="error"
        startIcon={<CallEndIcon />}
        onClick={onEnd}
      >
        End conversation
      </Button>
    </Stack>
  );
}